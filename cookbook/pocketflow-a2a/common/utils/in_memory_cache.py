"""In Memory Cache utility."""

import threading
import time
from typing import Any, Dict, Optional


class InMemoryCache:
    """一个线程安全的单例类，用于管理缓存数据。

    确保整个应用程序中只存在一个缓存实例。
    """

    _instance: Optional["InMemoryCache"] = None
    _lock: threading.Lock = threading.Lock()
    _initialized: bool = False

    def __new__(cls):
        """重写 __new__ 以控制实例创建（单例模式）。

        在第一次实例化期间使用锁来确保线程安全。

        返回：
            InMemoryCache 的单例实例。
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化缓存存储。

        使用一个标志 (_initialized) 来确保此逻辑仅在单例实例的第一次创建时运行。
        """
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    # print("正在初始化会话缓存存储")
                    self._cache_data: Dict[str, Dict[str, Any]] = {}
                    self._ttl: Dict[str, float] = {}
                    self._data_lock: threading.Lock = threading.Lock()
                    self._initialized = True

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置一个键值对。

        参数：
            key: 数据的键。
            value: 要存储的数据。
            ttl: 生存时间（秒）。如果为 None，数据将不会过期。
        """
        with self._data_lock:
            self._cache_data[key] = value

            if ttl is not None:
                self._ttl[key] = time.time() + ttl
            else:
                if key in self._ttl:
                    del self._ttl[key]

    def get(self, key: str, default: Any = None) -> Any:
        """获取与键关联的值。

        参数：
            key: 会话中数据的键。
            default: 如果未找到会话或键，则返回的值。

        返回：
            缓存的值，如果未找到则返回默认值。
        """
        with self._data_lock:
            if key in self._ttl and time.time() > self._ttl[key]:
                del self._cache_data[key]
                del self._ttl[key]
                return default
            return self._cache_data.get(key, default)

    def delete(self, key: str) -> None:
        """从缓存中删除特定的键值对。

        参数：
            key: 要删除的键。

        返回：
            如果找到并删除了键，则为 True，否则为 False。
        """

        with self._data_lock:
            if key in self._cache_data:
                del self._cache_data[key]
                if key in self._ttl:
                    del self._ttl[key]
                return True
            return False

    def clear(self) -> bool:
        """删除所有数据。

        返回：
            如果数据已清除，则为 True，否则为 False。
        """
        with self._data_lock:
            self._cache_data.clear()
            self._ttl.clear()
            return True
        return False
