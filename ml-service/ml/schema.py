from pydantic import BaseModel, Base64Bytes
from enum import Enum

class MessageConsume(BaseModel):
    id : str
    frame_id: str
    frame: Base64Bytes

class StateEnum(str, Enum):
    STARTUP = "init_startup" # пользователем из апи -> STARTUP_PROCESS
    SHUTDOWN = "init_shutdown" # пользователем из апи -> SHUTDOWN_PROCESS
    SHUTDOWN_PROCESS = "in_shutdown_processing"
    STARTUP_PROCESS = "in_startup_processing"
    RUNNER_PROCESS = "runner_started" #runner started process
    ML_PROCESS = "ml_started" #ml started process
    INACTIVE_OK = "inactive" #stop process without error / answer to shutdown
    INACTIVE_ERROR = "inactive_error" #stop process with error 

class ServiceSenderEnum(str, Enum):
    API ="api"
    RUNNER = "runner"
    ML = "ml"


# сообщение кафки
class MessageState(BaseModel):
    id : str
    state: StateEnum
    error: bool
    sender: ServiceSenderEnum