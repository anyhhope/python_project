from pydantic import BaseModel

# модельки для апи
class Query(BaseModel):
    state: str
    rtsp_src: str