from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class QueryDto:
    rtsp_src: str
    state: str
    id: Optional[int] = None
    created_at: Optional[datetime] = None