# client.py
import atexit
import logging
import signal
import threading
from typing import Optional

from nacos import NacosClient

from .config import NacosConfig
from .discovery import ServiceDiscovery
from .entity import SharedConfigEntity
from .registry import ServiceRegistry
from .config_app import AppConfig

logger = logging.getLogger(__name__)


class NacosClientManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        server_addresses: str,
        namespace: str = "",
        username: str = None,
        password: str = None,
    ):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.server_addresses = server_addresses
        self.namespace = namespace

        self.nacos_client = NacosClient(
            server_addresses=server_addresses,
            namespace=namespace,
            username=username,
            password=password,
        )

        self.config_manager: Optional[NacosConfig] = None
        self.registry: Optional[ServiceRegistry] = None
        self.discovery = ServiceDiscovery(self.nacos_client)

        self._setup_shutdown_hooks()
        self._initialized = True

    def init_config(
        self,
        data_id: str,
        group: str = "DEFAULT_GROUP",
        config_env: AppConfig = None,
        shared_configs: list[SharedConfigEntity] = [],
    ) -> NacosConfig:
        self.config_manager = NacosConfig(
            self.nacos_client, data_id, group, config_env, shared_configs
        )
        return self.config_manager

    def register_service(
        self,
        service_name: str,
        port: int,
        ip: str = None,
        group: str = "DEFAULT_GROUP",
        metadata: dict = None,
        heartbeat_interval: int = 5,
    ) -> ServiceRegistry:
        self.registry = ServiceRegistry(
            client=self.nacos_client,
            service_name=service_name,
            ip=ip,
            port=port,
            group=group,
            metadata=metadata,
            heartbeat_interval=heartbeat_interval,
        )
        self.registry.register()
        return self.registry

    def get_discovery(self) -> ServiceDiscovery:
        return self.discovery

    def _setup_shutdown_hooks(self):
        """注册优雅关闭钩子"""

        def _shutdown():
            if self.registry:
                self.registry.deregister()

        atexit.register(_shutdown)
        # 捕获 SIGTERM / SIGINT
        signal.signal(signal.SIGTERM, lambda s, f: _shutdown() or exit(0))
        signal.signal(signal.SIGINT, lambda s, f: _shutdown() or exit(0))

    def close(self):
        if self.registry:
            self.registry.deregister()
