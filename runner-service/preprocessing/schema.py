from pydantic import BaseModel, EncodedBytes
from enum import Enum

# сообщение кафки
class MessageConsume(BaseModel):
    id : str
    rtsp_src: str

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

class MessageFrame(BaseModel):
    id : str
    frame_id: str
    # frame: EncodedBytes
