from typing import List, Optional

from pydantic import BaseModel

class SharedConfigEntity(BaseModel):
    data_id: str = ""
    group: str = ""
    refresh: bool = True


class NacosConfigEntity(BaseModel):
    service_host: Optional[str] = None
    server_addr: str = ""
    namespace: str = ""
    username: str = "nacos"
    password: str = "nacos"
    config_data_id: str = ""
    config_group: str = "DEFAULT_GROUP"
    shared_configs: List[SharedConfigEntity] = []
    metadata: dict = []
