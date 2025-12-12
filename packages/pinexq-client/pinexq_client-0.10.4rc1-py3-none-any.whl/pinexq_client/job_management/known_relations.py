from enum import StrEnum


class Relations(StrEnum):
    SELF = "self"
    ITEM = "item"
    DOWNLOAD = "Download"
    CREATED_RESSOURCE = "created-resource"
    USED_TAGS = "UsedTags"
    USED_TAGS_ADMIN = "UsedTagsAdmin"

    # query pagination
    FIRST = "first"
    PREVIOUS = "previous"
    NEXT = "next"
    LAST = "last"
    ALL = "all"

    # job
    PARENT_JOB = "ParentJob"
    SELECTED_PROCESSING_STEP = "SelectedProcessingStep"
    INPUT_DATASLOT = "InputDataSlot"
    OUTPUT_DATASLOT = "OutputDataSlot"

    # workdata
    PRODUCED_BY_JOB = "ProducedByJob"
    PRODUCED_BY_PROCESSING_STEP = "ProducedByProcessingStep"

    # dataslots
    SELECTED = "Selected"
    ASSIGNED = "Assigned"

    # info
    CURRENT_USER = "CurrentUser"

    # Api Events
    API_EVENTS_ENDPOINT = "ApiEventsEndpoint"

    # Deployment
    DEPLOYMENT_REGISTRY_ENDPOINT = "Registry"
    REMOTE_ENDPOINT = "Remote"
