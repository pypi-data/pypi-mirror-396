"""
定义一个常量类
"""

from typing import ClassVar


class NacosConstant:
    """
    nacos配置相关常量
    """

    NACOS_SERVER_ADDRESSES: ClassVar[str] = "nacos.server_addr"
    NACOS_CONFIG_DATA_ID: ClassVar[str] = "nacos.config_data_id"
    NACOS_CONFIG_GROUP: ClassVar[str] = "nacos.config_group"
    NACOS_CONFIG_NAMESPACE: ClassVar[str] = "nacos.namespace"
    NACOS_CONFIG_USERNAME: ClassVar[str] = "nacos.username"
    NACOS_CONFIG_PASSWORD: ClassVar[str] = "nacos.password"

    """
    nacos服务注册相关常量
    """
    NACOS_SERVICE_NAME: ClassVar[str] = "app.name"
    NACOS_SERVICE_PORT: ClassVar[int] = "app.port"
    NACOS_SERVICE_HOST: ClassVar[str | None] = "nacos.service_host"
    NACOS_SERVICE_METADATA: ClassVar[dict | None] = "nacos.metadata"
