from typing import Optional

from ..models.models import BaseRequest


class BaseAsyncRequest(BaseRequest):
    request_id: str
    heartbeat_check_seconds_interval: Optional[int] = None
    webhook_uri: Optional[str] = None
    webhook_token: Optional[str] = None
