from typing import Dict, Any, Optional
import hashlib
import time
import logging

# 配置日志
logger = logging.getLogger(__name__)

class SimpleCache:
    """简单的内存缓存实现"""
    
    def __init__(self, max_size: int = 1000, expiration_time: int = 3600):
        self.cache = {}
        self.max_size = max_size  # 最大缓存条目数
        self.expiration_time = expiration_time  # 缓存过期时间（秒）
    
    def _get_key(self, data: Any, **kwargs) -> str:
        """生成缓存键"""
        # 将数据和参数转换为字符串，然后生成MD5哈希
        key_str = str(data) + str(sorted(kwargs.items()))
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, data: Any, **kwargs) -> Optional[Any]:
        """获取缓存值"""
        key = self._get_key(data, **kwargs)
        if key in self.cache:
            item = self.cache[key]
            # 检查是否过期
            if time.time() - item["timestamp"] < self.expiration_time:
                return item["value"]
            else:
                # 删除过期缓存
                del self.cache[key]
        return None
    
    def set(self, data: Any, value: Any, **kwargs) -> None:
        """设置缓存值"""
        key = self._get_key(data, **kwargs)
        # 如果缓存已满，删除最旧的缓存
        if len(self.cache) >= self.max_size:
            # 找到最旧的缓存
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["timestamp"])
            del self.cache[oldest_key]
        # 设置新缓存
        self.cache[key] = {
            "value": value,
            "timestamp": time.time()
        }
    
    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()
    
    def size(self) -> int:
        """获取缓存大小"""
        return len(self.cache)

# 创建全局缓存实例
api_cache = SimpleCache(max_size=1000, expiration_time=3600)
