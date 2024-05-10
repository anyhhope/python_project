from pydantic import BaseModel, Base64Bytes

class MessageConsume(BaseModel):
    id : str
    frame_id: str
    frame: Base64Bytes