# config.py

import json
import logging
import threading
from typing import Any, ClassVar, Dict, Optional

import yaml
from nacos import NacosClient

from .config_app import AppConfig,init_app_config
from .entity import SharedConfigEntity

logger = logging.getLogger(__name__)


class NacosConfig:
    """Nacos配置管理器"""

    # 类级单例（线程安全）
    _instance: ClassVar[Optional["NacosConfig"]] = None
    _instance_lock = threading.Lock()

    def __init__(
        self,
        client: NacosClient,
        data_id: str,
        group: str = "DEFAULT_GROUP",
        config_env: AppConfig = None,
        shared_configs: list[SharedConfigEntity] = [],
    ):
        self.client = client
        self.data_id = data_id
        self.group = group
        self.config_env = config_env or init_app_config()
        self._lock = threading.RLock()
        self.shared_configs = shared_configs
        self._nacos_config: Dict[str, Any] = {}
        self._load_and_watch(self.data_id, self.group)

        for shared_config in shared_configs:
            self._load_and_watch(shared_config.data_id, shared_config.group)

        # 将Nacos配置注入到统一配置环境
        self.config_env.set_remote_config(self._nacos_config)

        # 打印app_config配置
        logger.info(self.config_env.print_all_configs())

        # 注册单例
        if NacosConfig._instance is None:
            with NacosConfig._instance_lock:
                if NacosConfig._instance is None:
                    NacosConfig._instance = self
                    logger.info(
                        "Intialized NacosConfig with 3-level fallback: env > nacos > local"
                    )

    @classmethod
    def get_instance(cls) -> "NacosConfig":
        """供非请求上下文使用（如工具函数、service）"""
        if cls._instance is None:
            raise RuntimeError(
                "NacosConfig not initialized. "
                "Ensure init_nacos() is called during app startup."
            )
        return cls._instance

    def _detect_format(self) -> str:
        """根据 data_id 后缀判断格式"""
        if self.data_id.endswith((".yaml", ".yml")):
            return "yaml"
        elif self.data_id.endswith(".json"):
            return "json"
        else:
            # 默认尝试 YAML（因 YAML 是 JSON 超集）
            return "yaml"

    def _detect_format_by_data_id(self, data_id: str) -> str:
        """根据 data_id 后缀判断格式"""
        if data_id.endswith((".yaml", ".yml")):
            return "yaml"
        elif data_id.endswith(".json"):
            return "json"
        else:
            # 默认尝试 YAML（因 YAML 是 JSON 超集）
            return "yaml"

    def _parse_content(self, content: str, fmt: str) -> Dict[str, Any]:
        """安全解析配置内容"""
        if not content:
            return {}
        content = content.strip()
        if not content:
            return {}

        try:
            if fmt == "json":
                return json.loads(content)
            else:  # yaml or auto
                # 使用 yaml.safe_load，它能解析 JSON 和 YAML
                parsed = yaml.safe_load(content)
                # yaml.safe_load 可能返回非 dict（如纯字符串），需校验
                if parsed is None:
                    return {}
                if not isinstance(parsed, dict):
                    logger.warning(
                        f"Config {self.data_id} parsed as non-dict: {type(parsed)}"
                    )
                    return {}
                return parsed
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse {fmt.upper()} config '{self.data_id}': {e}")
            logger.debug(f"Problematic content:\n{content[:500]}...")
            raise

    def _load_and_watch(self, data_id: str = None, group: str = None):
        """首次加载 + 注册监听"""
        fmt = self._detect_format()
        try:
            raw = self._load(data_id, group)
            logger.info(f"Loaded config '{self.data_id}' (format: {fmt})")
        except Exception as e:
            logger.error(f"Failed to load initial config '{data_id}': {e}")
            self._nacos_config = {}  # 初始化为空 dict，避免后续 get 报错

        # 注册监听器
        self._watch(data_id, group, self._on_change_callback)

    def _load(self, data_id, group):
        raw = self.client.get_config(data_id, group)
        fmt = self._detect_format_by_data_id(data_id)
        parsed = self._parse_content(raw, fmt)
        self._nacos_config[f"{group}/{data_id}"] = parsed
        return parsed

    def _watch(self, data_id, group, callback):
        def wrapper(args):
            fmt = self._detect_format_by_data_id(data_id)
            new_config = self._parse_content(args["content"], fmt)
            # self._nacos_config[f"{group}/{data_id}"] = new_config
            callback(new_config, fmt, data_id, group)

        try:
            self.client.add_config_watcher(data_id, group, wrapper)
            logger.info(f"Started watching config '{data_id}' in group '{group}'")
        except Exception as e:
            logger.error(f"Failed to watch config '{data_id}' in group '{group}': {e}")

    def _on_change_callback(self, new_config: Dict[str, Any], fmt: str, data_id, group):
        """配置变更回调"""
        try:
            config_key = f"{group}/{data_id}"

            with self._lock:
                if config_key in self._nacos_config:
                    old_config = self._nacos_config[config_key]
                    # 使用深度比较，获取完整路径
                    changes = self._deep_diff(old_config, new_config)

                    # 更新配置
                    self._nacos_config[config_key] = new_config

                    # 记录变更详情
                    change_details = []
                    if changes["added"]:
                        added_info = []
                        for path, value in changes["added"].items():
                            added_info.append(f"{path}={value}")
                        change_details.append(f"added: {added_info}")

                    if changes["removed"]:
                        removed_info = []
                        for path, value in changes["removed"].items():
                            removed_info.append(f"{path}={value}")
                        change_details.append(f"removed: {removed_info}")

                    if changes["modified"]:
                        modified_info = []
                        for path, values in changes["modified"].items():
                            modified_info.append(
                                f"{path}: {values['old']} -> {values['new']}"
                            )
                        change_details.append(f"modified: {modified_info}")

                    if change_details:
                        logger.info(
                            f"Config '{data_id}' in group '{group}' updated (format: {fmt})"
                            + f" — {', '.join(change_details)}"
                        )
                    else:
                        logger.info(
                            f"Config '{data_id}' in group '{group}' updated (no changes detected)"
                        )
                else:
                    # 新配置
                    self._nacos_config[config_key] = new_config
                    logger.info(
                        f"New config '{data_id}' in group '{group}' loaded (format: {fmt})"
                    )

        except Exception as e:
            logger.error(f"Config update failed, keeping old config: {e}")

    def _deep_diff(
        self, old_dict: Dict[str, Any], new_dict: Dict[str, Any], prefix: str = ""
    ) -> Dict[str, Any]:
        """深度比较两个字典的差异，返回完整的变更路径和具体值"""
        changes = {"added": {}, "removed": {}, "modified": {}}

        # 获取所有键
        all_keys = set(old_dict.keys()) | set(new_dict.keys())

        for key in all_keys:
            current_path = f"{prefix}.{key}" if prefix else key

            if key not in old_dict:
                changes["added"][current_path] = new_dict[key]
            elif key not in new_dict:
                changes["removed"][current_path] = old_dict[key]
            else:
                old_val = old_dict[key]
                new_val = new_dict[key]

                # 如果都是字典，递归比较
                if isinstance(old_val, dict) and isinstance(new_val, dict):
                    nested_changes = self._deep_diff(old_val, new_val, current_path)
                    # 合并嵌套变更
                    for change_type in ["added", "removed", "modified"]:
                        if nested_changes[change_type]:
                            changes[change_type].update(nested_changes[change_type])
                # 如果值不同
                elif old_val != new_val:
                    changes["modified"][current_path] = {"old": old_val, "new": new_val}

        return changes

    def get(self, key: str, default=None):
        """通过配置环境获取配置"""
        return self.config_env.get(key, default)
