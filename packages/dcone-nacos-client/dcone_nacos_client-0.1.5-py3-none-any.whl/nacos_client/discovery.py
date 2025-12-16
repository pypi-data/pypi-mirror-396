# discovery.py
import logging
from typing import Dict, List, Optional

from nacos import NacosClient

logger = logging.getLogger(__name__)


class ServiceDiscovery:
    def __init__(self, client: NacosClient):
        self.client = client

    def get_instances(
        self,
        service_name: str,
        group: str = "DEFAULT_GROUP",
        healthy_only: bool = True,
    ) -> List[Dict]:
        """
        获取服务实例列表
        返回格式: [{"ip": "...", "port": ..., "metadata": {...}, ...}]
        """
        try:
            instances = self.client.list_naming_instance(
                service_name=service_name,
                group_name=group,
                healthy_only=healthy_only,
            )
            # 过滤出可用字段
            result = []
            for inst in instances["hosts"]:
                result.append(
                    {
                        "ip": inst["ip"],
                        "port": inst["port"],
                        "weight": inst["weight"],
                        "healthy": inst["healthy"],
                        "metadata": getattr(inst, "metadata", {}),
                        "cluster": getattr(inst, "clusterName", "DEFAULT"),
                    }
                )
            logger.debug(f"Discovered {len(result)} instances for {service_name}")
            return result
        except Exception as e:
            logger.error(f"Failed to discover {service_name}: {e}")
            return []

    def get_one_healthy_instance(
        self, service_name: str, group: str = "DEFAULT_GROUP"
    ) -> Optional[Dict]:
        instances = self.get_instances(service_name, group, healthy_only=True)
        return instances[0] if instances else None
