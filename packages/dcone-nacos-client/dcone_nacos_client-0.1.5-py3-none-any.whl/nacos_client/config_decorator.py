import functools
import logging
from typing import Any, Dict

from .config_app import AppConfig, app_config

logger = logging.getLogger(__name__)


def from_nacos_config(config_path: str = None):
    """
    通用注解装饰器，用于从Nacos配置中实例化实体

    Args:
        config_path: 配置路径，如 "nacos.shared_configs" 或 "pgsql"
    """

    def decorator(cls):
        original_init = cls.__init__

        @functools.wraps(original_init)
        def new_init(self, config: AppConfig = app_config, *args, **kwargs):
            # 调用原始构造函数
            original_init(self, *args, **kwargs)

            # 如果提供了Nacos配置，则进行属性填充
            if config and config_path:
                config_data = config.get(config_path)
                if config_data:
                    _populate_object_from_dict(self, config_data)

        cls.__init__ = new_init
        return cls

    return decorator


def _extract_config_by_path(config: Dict[str, Any], path: str) -> Dict[str, Any]:
    """根据路径从配置字典中提取子配置"""
    keys = path.split(".")
    current = config
    current.get(path)
    return current


def _populate_object_from_dict(obj: Any, data: Dict[str, Any]):
    """将字典数据填充到对象属性中，支持嵌套对象类型"""
    for key, value in data.items():
        # 转换为Python风格的属性名（下划线命名）
        attr_name = key.replace("-", "_")
        if hasattr(obj, attr_name):
            # 正确获取类型注解
            attr_type = None
            if hasattr(obj, "__annotations__"):
                attr_type = obj.__annotations__.get(attr_name)

            # 检查是否为复杂类型
            if isinstance(value, dict) and attr_type and hasattr(attr_type, "__call__"):
                # 处理嵌套对象
                nested_obj = getattr(obj, attr_name)
                if nested_obj is None:
                    # 如果属性为空，尝试创建新实例
                    try:
                        # 确保类型是可调用的（类）
                        if callable(attr_type):
                            nested_obj = attr_type()
                            setattr(obj, attr_name, nested_obj)
                            _populate_object_from_dict(nested_obj, value)
                    except Exception as e:
                        print(f"Failed to create nested object for {attr_name}: {e}")
                        continue
                else:
                    _populate_object_from_dict(nested_obj, value)
            elif isinstance(value, list) and len(value) > 0:
                # 处理列表类型
                if isinstance(value[0], dict):
                    item_type = _get_list_item_type(obj, attr_name)
                    if item_type and callable(item_type):
                        nested_list = []
                        for item_data in value:
                            try:
                                item_obj = item_type()
                                _populate_object_from_dict(item_obj, item_data)
                                nested_list.append(item_obj)
                            except Exception as e:
                                print(
                                    f"Failed to create list item for {attr_name}: {e}"
                                )
                                continue
                        setattr(obj, attr_name, nested_list)
                else:
                    # 简单列表类型直接赋值
                    setattr(obj, attr_name, value)
            else:
                # 简单类型直接赋值
                setattr(obj, attr_name, value)


def _get_list_item_type(obj: Any, attr_name: str):
    """获取列表属性的元素类型"""
    try:
        # 通过类型注解获取元素类型
        if hasattr(obj, "__annotations__"):
            annotations = obj.__annotations__
            attr_type = annotations.get(attr_name)
            if hasattr(attr_type, "__args__") and len(attr_type.__args__) > 0:
                return attr_type.__args__[0]
    except Exception:
        pass
    return None
