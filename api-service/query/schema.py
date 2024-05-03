from pydantic import BaseModel
from enum import Enum

class StateEnum(str, Enum):
    STARTUP = "init_startup"
    STARTUP_PROCESS = "in_startup_processing" #runner started process
    SHUTDOWN = "init_shutdown"
    SHUTDOWN_PROCESS = "in_shutdown_processing"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"

# модельки для апи
class Query(BaseModel):
    state: StateEnum
    rtsp_src: str

# сообщение кафки
class Message(BaseModel):
    id : str
    rtsp_src: str