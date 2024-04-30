from pydantic import BaseModel
from enum import Enum

class StateEnum(str, Enum):
    STATE1 = "init_startup"
    STATE2 = "in_startup_processing"
    STATE3 = "init_shutdown"
    STATE4 = "in_shutdown_processing"
    STATE5 = "active"
    STATE6 = "inactive"
    STATE7 = "error"

# модельки для апи
class Query(BaseModel):
    state: StateEnum
    rtsp_src: str