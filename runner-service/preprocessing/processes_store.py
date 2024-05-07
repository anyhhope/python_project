from typing import Dict
from pydantic import BaseModel

from .customProcess import CustomProcess

class ProcessModel(BaseModel):
    process_id: int
    process: CustomProcess

    class Config:
        arbitrary_types_allowed = True

processes_store: Dict[str, ProcessModel] = {}