import queue
import threading
import time
from datetime import datetime, timedelta
from pydantic import BaseModel

import httpx
from httpx_sse import connect_sse

from dataclasses import dataclass

from pinexq_client.job_management import EntryPointHco, enter_jma


@dataclass
class WorkerInfo:
    worker: threading.Thread
    close_after: datetime | None = None

class ApiEvent(BaseModel):
    EventType: str
    ResourceType: str
    ResourceLink: str


class ApiEventManagerSingleton:
    _instance = None
    listening_clients: dict[httpx.Client, dict[str, list[queue.Queue]]]
    workers: dict[httpx.Client, WorkerInfo]
    sse_connection_cooldown_s: int
    connection_create_lock: threading.Lock
    reconnect_time_s: int

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Only initialize once
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.listening_clients = {}
            self.workers = {}
            self.connection_create_lock = threading.Lock()
            self.sse_connection_cooldown_s = 30 # avoid opening and closing fast
            self.reconnect_time_s = 5

    def subscribe_waiter(self, client: httpx.Client, resource_link:str, wait_queue: queue.Queue):
        open_sse_connections = False

        if not client in self.listening_clients:
            self.listening_clients[client] = {}
            open_sse_connections = True

        if resource_link not in self.listening_clients[client]:
            self.listening_clients[client][resource_link] = []

        self.listening_clients[client][resource_link].append(wait_queue)

        with self.connection_create_lock:
            if open_sse_connections:
                self.open_sse_connection(client)
            self.workers[client].close_after = None  # we use the connection now, do not close

    def unsubscribe_waiter(self, client: httpx.Client, resource_link: str, wait_queue: queue.Queue):
        if not client in self.listening_clients:
            return

        if resource_link not in self.listening_clients[client]:
            return

        # event should only be in here once
        self.listening_clients[client][resource_link].remove(wait_queue)

        # clean up if no events left
        if len(self.listening_clients[client][resource_link]) == 0:
            del self.listening_clients[client][resource_link]

            # if noone is subscribed anymore set shutdown time
            if not self.listening_clients[client]:
                self.workers[client].close_after = datetime.now() + timedelta(seconds=self.sse_connection_cooldown_s)


    def open_sse_connection(self, client: httpx.Client):
        sse_endpoint = self.get_sse_endpoint_from_api(client)

        # start worker for client
        worker_thread = threading.Thread(target=self.consume_sse_events, args=(client, sse_endpoint))
        self.workers[client] = WorkerInfo(worker=worker_thread)
        worker_thread.start()

    def consume_sse_events(self, client: httpx.Client, sse_endpoint: str):
        while True:
            try:
                if client.is_closed:
                    print("Client was closed, will close sse connection too")
                    self.close_connections(client)
                    return

                with connect_sse(client, "GET", sse_endpoint) as event_source:
                    for sse in event_source.iter_sse():
                        # close the thread if no one is using it anymore and cooldown has passed
                        close_after = self.workers[client].close_after
                        if close_after and datetime.now() > close_after:
                            self.close_connections(client)
                            return

                        if len(sse.data) <= 0: # keep alive has no data
                            continue

                        api_event = ApiEvent.model_validate_json(sse.data)

                        # for now, we only process job events
                        if api_event.ResourceType != "Job":
                            continue

                        job_link = api_event.ResourceLink
                        subscribed = self.listening_clients[client]
                        if job_link in subscribed:
                            for wait_queue in subscribed[job_link]:
                                wait_queue.put(job_link)
            except httpx.ReadError:
                print(f"SSE Connection lost. Reconnecting in {self.reconnect_time_s} seconds...")
                time.sleep(self.reconnect_time_s)
            except httpx.ConnectError as e:
                print(f"Failed to connect to SSE endpoint: {e}. Retrying in {self.reconnect_time_s} seconds...")
                time.sleep(self.reconnect_time_s)
            except Exception as ex:
                raise

    def close_connections(self, client: httpx.Client):
        del self.listening_clients[client]
        del self.workers[client]  # worker not needed any more

    @staticmethod
    def get_sse_endpoint_from_api(client)-> str:
        entrypoint: EntryPointHco = enter_jma(client)
        endpoint =  str(entrypoint.info_link.navigate().api_events_endpoint.get_url())
        return endpoint

