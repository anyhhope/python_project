from pydantic import BaseModel
from enum import Enum

class StateEnum(str, Enum):
    STARTUP = "init_startup"
    SHUTDOWN = "init_shutdown"
    ERROR = "init_error"
    SHUTDOWN_PROCESS = "in_shutdown_processing"
    RUNNER_PROCESS = "runner_started" #runner started process
    ML_PROCESS = "ml_started"
    INACTIVE_OK = "inactive"
    INACTIVE_ERROR = "inactive_error"


# сообщение кафки
class MessageState(BaseModel):
    id : str
    state: StateEnum