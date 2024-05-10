from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class DetectionDto:
    s3_url: str
    query_id: int
    detection_result: str
    id: Optional[int] = None
    created_at: Optional[datetime] = None