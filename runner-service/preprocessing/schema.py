from pydantic import BaseModel

# сообщение кафки
class MessageConsume(BaseModel):
    id : str
    rtsp_src: str