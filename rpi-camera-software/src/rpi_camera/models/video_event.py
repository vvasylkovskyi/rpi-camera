from pydantic import BaseModel, HttpUrl
from datetime import datetime


class VideoRecordingEvent(BaseModel):
    device_id: str
    video_url: str
    # timestamp: datetime
