from pydantic import BaseModel, Field
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

# модельки для апи
class Query(BaseModel):
    state: StateEnum = Field(examples=[StateEnum.STARTUP.value])
    rtsp_src: str = Field(examples=["rtsp://fake.kerberos.io/stream"])

# сообщение кафки
class Message(BaseModel):
    id : str
    rtsp_src: str