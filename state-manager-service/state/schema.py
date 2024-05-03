from pydantic import BaseModel

# сообщение кафки
class MessageState(BaseModel):
    id : str
    state: str