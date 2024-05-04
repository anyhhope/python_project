from pydantic import BaseModel, Field
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
    state: StateEnum = Field(examples=[StateEnum.STARTUP.value])
    rtsp_src: str = Field(examples=["rtsp://fake.kerberos.io/stream"])

# сообщение кафки
class Message(BaseModel):
    id : str
    rtsp_src: str