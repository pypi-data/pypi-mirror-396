import json
import logging
import threading
from typing import Any, Dict, List, Optional

from .utils import load_env_config, load_local_config

logger = logging.getLogger(__name__)


class AppConfig:
    """配置环境管理器，统一管理所有配置源"""

    def __init__(self, env_prefix: str = "", local_fallback_path: Optional[str] = "config/config.yaml", lowercase_enabled: bool = True):
        self._lock = threading.RLock()
        self.lowercase_enabled = lowercase_enabled
        self._fallback_config = (
            load_local_config(local_fallback_path) if local_fallback_path else {}
        )
        self._remote_configs: Dict[str, Dict[str, Any]] = {}
        self._env_config = load_env_config(env_prefix, lowercase_enabled)

    def get(self, key: str, default=None, case_sensitive: bool = True):
        """按优先级获取配置并合并：环境变量 > 远程配置 > 本地fallback

        Args:
            key: 配置键，支持点号分隔的嵌套键
            default: 默认值
            case_sensitive: 是否区分大小写，默认为True
        """
        # 将点号转换为双下划线，用于环境变量查找
        env_key = key.replace(".", "__").upper()
        keys = key.split(".")

        # 按优先级从低到高获取配置
        fallback_cfg = self._get_nested_config(self._fallback_config, keys, case_sensitive)
        remote_cfg = self._get_from_remote_configs(keys, case_sensitive)
        env_cfg = self._get_nested_config(self._env_config, keys, case_sensitive)
        # 如果都是非字典类型，按优先级返回
        configs = [fallback_cfg, remote_cfg, env_cfg]
        non_dict_configs = [
            cfg for cfg in configs if cfg is not None and not isinstance(cfg, dict)
        ]
        if non_dict_configs:
            return self._auto_cast(non_dict_configs[-1])  # 返回最高优先级的非字典配置

        # 如果涉及字典类型，进行合并
        result = {}
        # 按优先级从低到高合并字典配置
        for cfg in [fallback_cfg, remote_cfg, env_cfg]:
            if isinstance(cfg, dict):
                result.update(cfg)

        return result if result else default

    def _get_nested_config(self, config: Dict[str, Any], keys: List[str], case_sensitive: bool = True):
        """获取嵌套配置值"""
        if config is None:
            return None
        current = config
        for k in keys:
            if isinstance(current, dict):
                if case_sensitive:
                    current = current.get(k)
                else:
                    # 不区分大小写查找
                    current = next((v for kk, v in current.items() if kk.lower() == k.lower()), None)
                if current is None:
                    return None
            else:
                return None
        return current

    def _get_from_remote_configs(self, keys: List[str], case_sensitive: bool = True):
        """从远程配置中按优先级获取配置"""
        with self._lock:
            for config_dict in self._remote_configs.values():
                cfg = self._get_nested_config(config_dict, keys, case_sensitive)
                if cfg is not None:
                    return cfg
        return None

    # def get(self, key: str, default=None):
    #     """按优先级获取配置并合并：环境变量 > 远程配置 > 本地fallback"""
    #     keys = key.split(".")
    #
    #     # 按优先级从低到高获取配置
    #     fallback_cfg = self._get_nested_config(self._fallback_config, keys)
    #     remote_cfg = self._get_from_remote_configs(keys)
    #     env_cfg = self._get_nested_config(self._env_config, keys)
    #
    #     # 如果都是非字典类型，按优先级返回
    #     configs = [fallback_cfg, remote_cfg, env_cfg]
    #     non_dict_configs = [
    #         cfg for cfg in configs if cfg is not None and not isinstance(cfg, dict)
    #     ]
    #     if non_dict_configs:
    #         return self._auto_cast(non_dict_configs[-1])  # 返回最高优先级的非字典配置
    #
    #     # 如果涉及字典类型，进行合并
    #     result = {}
    #     # 按优先级从低到高合并字典配置
    #     for cfg in [fallback_cfg, remote_cfg, env_cfg]:
    #         if isinstance(cfg, dict):
    #             result.update(cfg)
    #
    #     return result if result else default
    #
    # def _get_from_remote_configs(self, keys: List[str]):
    #     """从远程配置中按优先级获取配置"""
    #     # 按照一定的优先级顺序遍历远程配置
    #     # 这里可以按照配置加载的顺序或者其他逻辑确定优先级
    #     with self._lock:
    #         for config_dict in self._remote_configs.values():
    #             cfg = self._get_nested_config(config_dict, keys)
    #             if cfg is not None:
    #                 return cfg
    #     return None
    #
    # def _get_nested_config(self, config: Dict[str, Any], keys: List[str]):
    #     """获取嵌套配置值"""
    #     # 判断config是否为null
    #     if config is None:
    #         return []
    #     current = config
    #     for k in keys:
    #         if isinstance(current, dict) and k in current:
    #             current = current[k]
    #         else:
    #             return None
    #     return current

    def set_remote_config(self, config: Dict[str, Any]):
        """添加远程配置"""
        with self._lock:
            self._remote_configs = config

    def _auto_cast(self, value: str) -> Any:
        """类型自动转换"""
        if isinstance(value, str):
            if value.lower() in ("true", "false"):
                return value.lower() == "true"
            if value.isdigit():
                return int(value)
            try:
                return float(value)
            except ValueError:
                pass
        return value

    def print_all_configs(self):
        """打印完整配置，按优先级顺序显示"""
        configs = [
            ("🟢 环境变量配置 (最高优先级)", self._env_config),
            ("🔵 远程配置 (Nacos等)", self._remote_configs),
            ("🟡 本地Fallback配置 (最低优先级)", self._fallback_config),
        ]

        print("\n" + "=" * 60)
        print("配置环境管理器 - 完整配置信息")
        print("=" * 60)

        for title, config_data in configs:
            print(f"\n{title}:")
            if config_data:
                print(json.dumps(config_data, indent=2, ensure_ascii=False))
            else:
                print("  (无配置数据)")

        print("\n" + "=" * 60)


# app_config = ConfigEnvironment(env_prefix="", local_fallback_path="config/config.yaml")

# 全局缓存 + 锁
_app_config: Optional[AppConfig] = None
_config_lock = threading.Lock()

def _create_config(
    env_prefix: str = "",
    local_fallback_path: str = "config/config.yaml"
) -> AppConfig:
    """工厂函数：创建新配置实例（一般只用于测试或多实例场景）"""
    return AppConfig(env_prefix, local_fallback_path)

def get_app_config() -> AppConfig:
    """获取全局唯一的配置实例（懒加载 + 线程安全）"""

    global _app_config
    if _app_config is not None:
        return _app_config
    with _config_lock:
        if _app_config is None:
            _app_config = AppConfig()  # 使用默认参数
        return _app_config


def get_config_value(
        key: str,
        default: Any = None,
        case_sensitive: bool = True
) -> Any:
    """
    快捷获取配置值。

    示例：
        host = get_config_value("database.host", default="localhost")

    注意：此函数是 get_app_config().get(...) 的便捷包装，
         所有逻辑仍由 ConfigEnvironment.get() 处理。
    """
    return get_app_config().get(key, default=default, case_sensitive=case_sensitive)

def init_app_config(
    env_prefix: str = "",
    local_fallback_path: str = "config/config.yaml",
    lowercase_enabled: bool = True
) -> AppConfig:
    """显式初始化全局配置（用于主程序入口，确保尽早加载）"""
    global _app_config
    with _config_lock:
        if _app_config is None:
            _app_config = AppConfig(env_prefix, local_fallback_path, lowercase_enabled)
        else:
            # 可选：抛出警告或允许覆盖（根据需求）
            pass
    return _app_config