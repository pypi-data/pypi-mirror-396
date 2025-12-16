# registry.py
import logging
import threading
from typing import Optional

from nacos import NacosClient

from .utils import SafeTimer, get_local_ip

logger = logging.getLogger(__name__)


class ServiceRegistry:
    def __init__(
        self,
        client: NacosClient,
        service_name: str,
        ip: Optional[str] = None,
        port: int = 8000,
        group: str = "DEFAULT_GROUP",
        cluster_name: str = "DEFAULT",
        weight: float = 1.0,
        metadata: dict = None,
        heartbeat_interval: int = 5,  # seconds
    ):
        self.client = client
        self.service_name = service_name
        self.ip = ip or get_local_ip()
        self.port = port
        self.group = group
        self.cluster_name = cluster_name
        self.weight = weight
        self.metadata = metadata or {}
        self.heartbeat_interval = heartbeat_interval
        self._registered = False
        self._shutdown = False
        self._lock = threading.Lock()
        self._heartbeat_timer: Optional[SafeTimer] = None

    def register(self):
        """注册服务实例"""
        with self._lock:
            if self._registered or self._shutdown:
                return
            try:
                self.client.add_naming_instance(
                    service_name=self.service_name,
                    ip=self.ip,
                    port=self.port,
                    group_name=self.group,
                    cluster_name=self.cluster_name,
                    weight=self.weight,
                    metadata=self.metadata,
                    ephemeral=True,  # 临时实例（依赖心跳）
                )
                self._registered = True
                logger.info(
                    f"Service registered: {self.service_name} @ {self.ip}:{self.port}"
                )
                self._start_heartbeat()
            except Exception as e:
                logger.error(f"Failed to register service: {e}")
                raise

    def _send_heartbeat(self):
        """发送心跳（Nacos SDK 内部已支持，但显式调用更可靠）"""
        if not self._registered or self._shutdown:
            return
        try:
            self.client.send_heartbeat(
                service_name=self.service_name,
                ip=self.ip,
                port=self.port,
                group_name=self.group,
                cluster_name=self.cluster_name,
                weight=self.weight,
                metadata=self.metadata,
            )
            logger.debug(f"Heartbeat sent for {self.service_name}")
        except Exception as e:
            logger.warning(f"Heartbeat failed: {e}")
        finally:
            # 确保定时器继续运行，除非明确停止
            if not self._shutdown and self._registered:
                self._start_heartbeat()

    def _start_heartbeat(self):
        self._heartbeat_timer = SafeTimer(self.heartbeat_interval, self._send_heartbeat)
        self._heartbeat_timer.start()

    def deregister(self):
        """主动注销服务（优雅关闭时调用）"""
        with self._lock:
            if not self._registered:
                return
            self._shutdown = True
            if self._heartbeat_timer:
                self._heartbeat_timer.cancel()
            try:
                self.client.remove_naming_instance(
                    service_name=self.service_name,
                    ip=self.ip,
                    port=self.port,
                    group_name=self.group,
                    cluster_name=self.cluster_name,
                )
                logger.info(f"Service deregistered: {self.service_name}")
            except Exception as e:
                logger.error(f"Failed to deregister: {e}")
            self._registered = False
