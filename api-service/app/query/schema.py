from pydantic import BaseModel

class Query(BaseModel):
    status: str
    rtsp_src: str