from pydantic import BaseModel

from dattos_data_engine_common.storage.models import StorageConfig


class BaseRequest(BaseModel):
    storage: StorageConfig
