from datetime import datetime

from pydantic import BaseModel


class BackupResponse(BaseModel):
    id: str
    domain_id: str
    status: str
    archive_path: str
    completed_at: datetime | None
    created_at: datetime
