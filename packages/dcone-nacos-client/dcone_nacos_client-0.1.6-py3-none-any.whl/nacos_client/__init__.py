# nacos/__init__.py
import logging
from typing import Optional, Tuple

from .client import NacosClientManager
from .config_app import init_app_config, get_app_config, get_config_value
from .config import NacosConfig
from .constant import NacosConstant
from .discovery import ServiceDiscovery
from .entity import NacosConfigEntity, SharedConfigEntity

logger = logging.getLogger(__name__)

__all__ = ["init_nacos_client", "get_service_discovery", "NacosConstant", "get_config_value", "get_app_config"]


# 全局变量（由 init_nacos 设置）
_nacos_manager: Optional[NacosClientManager] = None


def init_nacos_client(local_fallback_path: str = "config/config.yaml",
    lowercase_enabled: bool = True):
    init_app_config(local_fallback_path=local_fallback_path, lowercase_enabled=lowercase_enabled)
    nacos_config_data = get_config_value("nacos", {})
    nacos_entity = NacosConfigEntity(**nacos_config_data)
    """
    初始化 Nacos 客户端
    """
    return init_nacos(
        server_addresses=nacos_entity.server_addr,
        namespace=nacos_entity.namespace,
        username=nacos_entity.username,
        password=nacos_entity.password,
        service_name=get_config_value(key=NacosConstant.NACOS_SERVICE_NAME, case_sensitive= False),
        service_port=get_config_value(key=NacosConstant.NACOS_SERVICE_PORT, case_sensitive= False),
        config_data_id=nacos_entity.config_data_id,
        config_group=nacos_entity.config_group,
        shared_configs=nacos_entity.shared_configs,
        metadata=nacos_entity.metadata,
    )


def init_nacos(
    server_addresses: str,
    namespace: str = "",
    username: str = "",
    password: str = "",
    service_name: str = "sv-maas-service",
    service_port: int = 8000,
    service_host: str | None = None,
    config_data_id: str = "sv-maas-service-prod.yaml",
    config_group: str = "DEFAULT_GROUP",
    shared_configs: list[SharedConfigEntity] = [],
    metadata: dict | None = None,
) -> Tuple[NacosClientManager, NacosConfig]:
    """
    初始化 Nacos：客户端 + 配置 + 服务注册
    返回 (client, config)，供依赖注入或全局使用
    """
    global _nacos_manager

    # 1. 创建客户端
    nacos_manager = NacosClientManager(
        server_addresses=server_addresses,
        namespace=namespace,
        username=username,
        password=password,
    )

    _nacos_manager = nacos_manager

    # 2. 加载配置
    config = nacos_manager.init_config(
        data_id=config_data_id,
        group=config_group,
        config_env=get_app_config(),
        shared_configs=shared_configs,
    )

    # 3. 注册服务
    nacos_manager.register_service(
        service_name=service_name,
        port=service_port,
        ip=service_host or None,
        group=config_group,
        metadata=metadata or {},
        heartbeat_interval=5,
    )
    logger.info("Application started with Nacos (env > nacos > local)")

    return nacos_manager, config


def get_nacos_config(key: str, default=None):
    return NacosConfig.get_instance().get(key, default)


def get_service_discovery() -> ServiceDiscovery:
    if _nacos_manager is None:
        raise RuntimeError("Nacos not initialized. Call init_nacos() in startup.")
    return _nacos_manager.get_discovery()
