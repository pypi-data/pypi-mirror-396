import queue
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Union, Self

from pinexq_client.core.api_event_manager import ApiEventManagerSingleton
from pinexq_client.core.polling import PollingException
from pinexq_client.job_management.tool import Job
from pinexq_client.job_management.hcos import JobQueryResultHco
from pinexq_client.job_management.model import JobStates



class JobGroup:
    """
    A wrapper class for a group of jobs for easier execution and waiting.
    Internally jobs are hold in a set so order of execution is not guaranteed

    Attributes:
        _jobs:
            Set of jobs in the group
    """

    _jobs: set[Job]

    class WaitJobErrorBehaviour(StrEnum):
        IGNORE = "ignore"
        CONTINUE = "continue"
        COMPLETE = "complete"

    def __init__(self):
        self._jobs: set[Job] = set()

    @classmethod
    def from_query_result(cls, job_query_result: JobQueryResultHco) -> Self:
        """
        Initializes a `JobGroup` object from a JobQueryResultHco object
        Args:
            job_query_result: The JobQueryResultHco object whose jobs are to be added to the JobGroup

        Returns:
            The newly created `JobGroup` instance
        """
        instance = cls()
        for job in job_query_result.iter_flat():
            instance.add_jobs(Job.from_hco(job))
        return instance

    def is_empty(self) -> bool:
        """
        True if the group is empty
        """
        return len(self._jobs) <= 0

    def add_jobs(self, jobs: Union[Job, list[Job]]) -> Self:
        """
        Add a job or multiple jobs to the group. Duplicates will not be added.

        Args:
            jobs: A job or a list of job objects to be added to the JobGroup

        Returns:
            This `JobGroup` object
        """

        if isinstance(jobs, list):
            self._jobs.update(jobs)
        else:
            self._jobs.add(jobs)
        return self

    def start_all(self) -> Self:
        """
        Start all jobs, throws if a job can not be started.

        Returns:
            This `JobGroup` object
        """
        for job in self._jobs:
            job.start()
        return self

    def wait_all(self, job_timeout_s: float | None = None, total_timeout_s: float | None = None) -> Self:
        """
        Wait for all jobs to complete or error state.
        If the overall timeout elapses and some jobs are not complete, then exception.

        Args:
            job_timeout_s:
                Individual job timeout in seconds.
            total_timeout_s:
                Timeout for the whole operation in seconds. Default is no timeout.
        Returns:
            This `JobGroup` object
        """
        start_time = datetime.now()
        for job in self._jobs:
            if total_timeout_s is not None:
                elapsed_time = datetime.now() - start_time
                if total_timeout_s - elapsed_time.total_seconds() <= 0:
                    raise Exception("Total timeout exceeded while waiting for jobs.")

            try:
                job.wait_for_completion(timeout_s=job_timeout_s)
            except Exception:
                pass
        return self

    def wait_any(self, timeout_s: float | None = None, fallback_polling_interval_s: float = 300)-> Self:
        """
        Waits for any job to completes or enters error state.

        Args:
            timeout_s:
                Timeout for the function. Throws in timeout.
            fallback_polling_interval_s:
                Interval for hard polls not using SSE notification.
        """

        # early exits
        if self.is_empty():
            return self

        # see if current job is already done, no polling
        if self._any_job_ended(self._jobs, refresh_job=False):
            return self

        if timeout_s is None:
            function_timeout_on = datetime.max
        else:
            # end this wait hard
            function_timeout_on = datetime.now() + timedelta(seconds=timeout_s)

        # this will be used in for all jobs so we get a notification if one changes
        any_job_changed_signal = queue.Queue()
        manager = ApiEventManagerSingleton()

        for job in self._jobs:
            manager.subscribe_waiter(job._client, str(job.job_hco.self_link.get_url()), any_job_changed_signal)

        try:
            job_done = self._any_job_ended(self._jobs, refresh_job=True)
            poll_all = False
            job_links_to_poll: set[Job] = set()
            while not job_done:
                time_till_function_timeout = function_timeout_on - datetime.now()
                if time_till_function_timeout.total_seconds() <= 0.0:
                    raise PollingException(f"Timeout waiting for JobGroup complete.")

                next_wait_timeout_s = min(float(time_till_function_timeout.seconds), fallback_polling_interval_s)
                try:
                    job_links_to_poll = set()
                    job_link_of_notified = any_job_changed_signal.get(timeout=next_wait_timeout_s)
                    job_links_to_poll.add(self._get_job_by_link(job_link_of_notified))
                except queue.Empty:
                    # timeout, check all. One might be silent completed
                    poll_all = True
                    pass

                # read all messages since we only want to poll new state once if there are multiple messages
                while not any_job_changed_signal.empty():
                    job_link_of_notified = any_job_changed_signal.get(timeout=next_wait_timeout_s)
                    job_links_to_poll.add(self._get_job_by_link(job_link_of_notified))

                if poll_all:
                    job_done = self._any_job_ended(self._jobs, refresh_job=True)
                else:
                    job_done = self._any_job_ended(job_links_to_poll, refresh_job=True)

        finally:
            for job in self._jobs:
                manager.unsubscribe_waiter(job._client, str(job.job_hco.self_link.get_url()), any_job_changed_signal)

        # refresh all that were not yet completed so all jobs in group are up to date
        self._refresh_uncompleted_jobs(self._jobs)
        return self

    def all_jobs_completed_ok(self, refresh_jobs = False) -> bool:
        for job in self._jobs:
            state = self._get_job_state(job, refresh_jobs)
            if state is not JobStates.completed:
                return False
        return True

    def get_jobs(self) -> list[Job]:
        """
        Returns the list of jobs in the group

        Returns:
            List of jobs in the group
        """
        return list(self._jobs)

    def get_completed_jobs(self, refresh_jobs = False) -> list[Job]:
        """
        Returns the list of jobs that are completed

        Returns:
            List of jobs
        """
        return [job for job in self._jobs if self._get_job_state(job, refresh_jobs) == JobStates.completed]

    def get_incomplete_jobs(self, refresh_jobs = False) -> list[Job]:
        """
        Returns the incomplete jobs in state JobStates.processing or JobStates.pending

        Returns:
             List of jobs
        """
        return [job for job in self._jobs if self._get_job_state(job, refresh_jobs) in  (JobStates.processing, JobStates.pending)]

    def get_error_jobs(self, refresh_jobs = False) -> list[Job]:
        """
        Returns the list of jobs that are in error state

        Returns:
             List of jobs
        """
        return [job for job in self._jobs if self._get_job_state(job, refresh_jobs) == JobStates.error]

    def has_error_jobs(self, refresh_jobs = False) -> bool:
        """ Check if there are jobs in error state."""
        return any(self._get_job_state(job, refresh_jobs) == JobStates.error for job in self._jobs)

    def has_incomplete_jobs(self, refresh_jobs = False) -> bool:
        """ Check if there are jobs in state JobStates.processing or JobStates.pending."""
        return any(self._get_job_state(job, refresh_jobs) in (JobStates.processing, JobStates.pending) for job in self._jobs)

    def has_completed_jobs(self, refresh_jobs = False) -> bool:
        """ Check if there are jobs in completed state."""
        return any(self._get_job_state(job, refresh_jobs) == JobStates.completed for job in self._jobs)

    def remove_error_jobs(self, refresh_jobs=False):
        """Remove all jobs in error state."""
        self.remove(self.get_error_jobs(refresh_jobs))

    def remove_incomplete_jobs(self, refresh_jobs=False):
        """Remove all jobs in state JobStates.processing or JobStates.pending."""
        self.remove(self.get_incomplete_jobs(refresh_jobs))

    def remove_completed_jobs(self, refresh_jobs=False):
        """Remove all completed jobs."""
        self.remove(self.get_completed_jobs(refresh_jobs))

    def remove(self, jobs: Job | list[Job]) -> Self:
        """
        Removes given job(s) from the group.

        Args:
            jobs:
                The Job instance(s) to be removed
        Returns:
            This `JobGroup` object
        """

        if isinstance(jobs, list):
            for job in jobs:
                self._jobs.remove(job)
        else:
            self._jobs.remove(jobs)

        return self

    def clear(self) -> Self:
        """
        Removes all jobs from the group

        Returns:
            This `JobGroup` object
        """
        self._jobs = set()
        return self

    @staticmethod
    def _any_job_ended(jobs: set[Job], refresh_job: bool) -> bool:
        # early exit by checking without polling in any case
        for job in jobs:
            state = JobGroup._get_job_state(job, refresh_job=False)
            if state == JobStates.completed:
                return True
            if state == JobStates.error:
                return True

        if refresh_job:
            for job in jobs:
                state = JobGroup._get_job_state(job, refresh_job=refresh_job)
                if state == JobStates.completed:
                    return True
                if state == JobStates.error:
                    return True
        return False

    @staticmethod
    def _refresh_uncompleted_jobs(jobs: set[Job]):
        for job in jobs:
            if job.job_hco.state != JobStates.completed and job.job_hco.state != JobStates.error:
                job.refresh()

        for job in jobs:
            if job.job_hco.state == JobStates.error:
                raise PollingException(f"Job failed'. Error:{job.job_hco.error_description}")

    @staticmethod
    def _get_job_state(job: Job, refresh_job: bool) -> JobStates:
        """Only poll jobs if forced, else use internal state"""
        if refresh_job:
            state = job.get_state()
        else:
            # use current internal job state to avoid polling ALL
            state = job.job_hco.state
        return state

    def _get_job_by_link(self, job_link: str)-> Job:
        for job in self._jobs:
            if str(job.self_link().get_url()) == job_link:
                return job
        raise Exception(f"Could not lookup job in internal list for link: {job_link}")
