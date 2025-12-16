# utils.py
import logging
import os
import re
import threading
import socket
from typing import Any, Dict

import yaml

logger = logging.getLogger(__name__)

def get_local_ip():
    # 1. 优先从环境变量获取（K8s / Docker 推荐）
    ip = os.getenv("POD_IP") or os.getenv("HOST_IP")
    if ip:
        return ip

    # 2. 尝试通过连接一个本地保留地址（不发包！）
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # 连接到一个不可能出去的地址，但会绑定本地出口 IP
            s.connect(("10.255.255.255", 1))
            ip = s.getsockname()[0]
        return ip
    except Exception:
        pass

    # 3. 最后 fallback 到 hostname 解析
    try:
        hostname = socket.gethostname()
        ip_list = socket.gethostbyname_ex(hostname)[2]
        for ip in ip_list:
            if not ip.startswith(("127.", "169.254.")):
                return ip
    except Exception:
        pass

    return "127.0.0.1"

def load_local_config(local_config_path: str = os.path.join("config", "config.yaml")):
    """加载本地配置文件"""
    local_config: Dict[str, Any] = {}
    try:
        with open(local_config_path, "r", encoding="utf-8") as f:
            local_config = yaml.safe_load(f) or {}
        logger.info(f"Loaded local config from {local_config_path}")
    except Exception as e:
        logger.warning(f"Failed to load local config: {e}")
    finally:
        return local_config


def load_env_config(prefix: str = "", lowercase_enabled: bool = True) -> Dict[str, Any]:
    """
    从环境变量加载配置，支持嵌套。
    示例：
      MODEL__TEMPERATURE=0.9 → {"model": {"temperature": "0.9"}}
      DATABASE__PORT=5432     → {"database": {"port": "5432"}}
    """
    env_config: Dict[str, Any] = {}
    pattern = re.compile(r"^[A-Z_][A-Z0-9_]*$")

    for key, value in os.environ.items():
        if prefix and not key.startswith(prefix):
            continue
        # clean_key = key[len(prefix) :] if prefix else key
        clean_key = key
        if not pattern.match(clean_key):
            continue


        # 将 A__B__C 转为 ["a", "b", "c"]
        parts = [part.lower() if lowercase_enabled else part
                 for part in clean_key.split("__") if part]
        if not parts:
            continue

        # 构建嵌套字典
        current = env_config
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value

    return env_config


class SafeTimer:
    """安全的定时器，支持取消"""

    def __init__(self, interval: float, function, *args, **kwargs):
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.timer = None
        self._lock = threading.Lock()

    def start(self):
        with self._lock:
            if self.timer is None or not self.timer.is_alive():
                self.timer = threading.Timer(self.interval, self._run)
                self.timer.daemon = True
                self.timer.start()

    def _run(self):
        try:
            self.function(*self.args, **self.kwargs)
        finally:
            self.start()  # 循环执行

    def cancel(self):
        with self._lock:
            if self.timer:
                self.timer.cancel()
                self.timer = None


def clean_dict_v1(data: dict) -> dict:
    """清除字典中值为None的字段"""
    return {k: v for k, v in data.items() if v is not None}
