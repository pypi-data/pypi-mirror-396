from typing import Dict, Any, List, Optional
import json
import logging
import os
from datetime import datetime
from abc import ABC, abstractmethod

# 配置日志
logger = logging.getLogger(__name__)

class StorageBackend(ABC):
    """存储后端抽象基类"""
    
    @abstractmethod
    def save(self, data: Any, data_type: str, identifier: Optional[str] = None) -> str:
        """保存数据"""
        pass
    
    @abstractmethod
    def get(self, identifier: str, data_type: str) -> Optional[Any]:
        """获取数据"""
        pass
    
    @abstractmethod
    def update(self, identifier: str, data_type: str, update_data: Dict[str, Any]) -> bool:
        """更新数据"""
        pass
    
    @abstractmethod
    def delete(self, identifier: str, data_type: str) -> bool:
        """删除数据"""
        pass
    
    @abstractmethod
    def search(self, query: Dict[str, Any], data_type: str, limit: int = 100) -> List[Any]:
        """搜索数据"""
        pass
    
    @abstractmethod
    def count(self, data_type: str) -> int:
        """获取数据计数"""
        pass

class FileStorage(StorageBackend):
    """文件存储后端"""
    
    def __init__(self, storage_dir: str = "./data"):
        self.storage_dir = storage_dir
        # 创建存储目录
        os.makedirs(self.storage_dir, exist_ok=True)
        # 为每种数据类型创建子目录
        for data_type in ["event", "log", "vulnerability", "traffic", "alert"]:
            os.makedirs(os.path.join(self.storage_dir, data_type), exist_ok=True)
    
    def save(self, data: Any, data_type: str, identifier: Optional[str] = None) -> str:
        """保存数据到文件"""
        try:
            if not identifier:
                # 生成唯一标识符
                identifier = f"{data_type}_{datetime.now().timestamp()}"
            
            # 构建文件路径
            file_path = os.path.join(self.storage_dir, data_type, f"{identifier}.json")
            
            # 保存数据
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return identifier
        except Exception as e:
            logger.error(f"文件存储保存失败: {e}")
            return None
    
    def get(self, identifier: str, data_type: str) -> Optional[Any]:
        """从文件获取数据"""
        try:
            # 构建文件路径
            file_path = os.path.join(self.storage_dir, data_type, f"{identifier}.json")
            
            if not os.path.exists(file_path):
                return None
            
            # 读取数据
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return data
        except Exception as e:
            logger.error(f"文件存储读取失败: {e}")
            return None
    
    def update(self, identifier: str, data_type: str, update_data: Dict[str, Any]) -> bool:
        """更新文件数据"""
        try:
            # 获取现有数据
            data = self.get(identifier, data_type)
            if not data:
                return False
            
            # 更新数据
            data.update(update_data)
            
            # 保存更新后的数据
            return self.save(data, data_type, identifier) is not None
        except Exception as e:
            logger.error(f"文件存储更新失败: {e}")
            return False
    
    def delete(self, identifier: str, data_type: str) -> bool:
        """删除文件数据"""
        try:
            # 构建文件路径
            file_path = os.path.join(self.storage_dir, data_type, f"{identifier}.json")
            
            if not os.path.exists(file_path):
                return False
            
            # 删除文件
            os.remove(file_path)
            return True
        except Exception as e:
            logger.error(f"文件存储删除失败: {e}")
            return False
    
    def search(self, query: Dict[str, Any], data_type: str, limit: int = 100) -> List[Any]:
        """搜索文件数据"""
        try:
            result = []
            # 获取数据类型目录下的所有文件
            data_dir = os.path.join(self.storage_dir, data_type)
            
            for filename in os.listdir(data_dir):
                if not filename.endswith(".json"):
                    continue
                
                # 读取文件内容
                file_path = os.path.join(data_dir, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # 检查是否匹配查询条件
                match = True
                for key, value in query.items():
                    if key not in data or data[key] != value:
                        match = False
                        break
                
                if match:
                    result.append(data)
                    if len(result) >= limit:
                        break
            
            return result
        except Exception as e:
            logger.error(f"文件存储搜索失败: {e}")
            return []
    
    def count(self, data_type: str) -> int:
        """获取数据计数"""
        try:
            # 获取数据类型目录下的所有JSON文件数量
            data_dir = os.path.join(self.storage_dir, data_type)
            count = 0
            for filename in os.listdir(data_dir):
                if filename.endswith(".json"):
                    count += 1
            return count
        except Exception as e:
            logger.error(f"文件存储计数失败: {e}")
            return 0

class DataStorage:
    """数据存储模块，管理不同的存储后端"""
    
    def __init__(self, backend_type: str = "file"):
        self.backend_type = backend_type
        
        # 根据类型创建存储后端
        if backend_type == "file":
            self.backend = FileStorage()
        else:
            raise ValueError(f"不支持的存储后端类型: {backend_type}")
    
    def save_data(self, data: Any, data_type: str, identifier: Optional[str] = None) -> str:
        """保存数据"""
        return self.backend.save(data, data_type, identifier)
    
    def get_data(self, identifier: str, data_type: str) -> Optional[Any]:
        """获取数据"""
        return self.backend.get(identifier, data_type)
    
    def update_data(self, identifier: str, data_type: str, update_data: Dict[str, Any]) -> bool:
        """更新数据"""
        return self.backend.update(identifier, data_type, update_data)
    
    def delete_data(self, identifier: str, data_type: str) -> bool:
        """删除数据"""
        return self.backend.delete(identifier, data_type)
    
    def search_data(self, query: Dict[str, Any], data_type: str, limit: int = 100) -> List[Any]:
        """搜索数据"""
        return self.backend.search(query, data_type, limit)
    
    def get_data_count(self, data_type: str) -> int:
        """获取数据计数"""
        return self.backend.count(data_type)
    
    def batch_save(self, data_list: List[Any], data_type: str) -> List[str]:
        """批量保存数据"""
        identifiers = []
        for data in data_list:
            identifier = self.save_data(data, data_type)
            if identifier:
                identifiers.append(identifier)
        return identifiers
    
    def batch_get(self, identifiers: List[str], data_type: str) -> List[Any]:
        """批量获取数据"""
        result = []
        for identifier in identifiers:
            data = self.get_data(identifier, data_type)
            if data:
                result.append(data)
        return result

# 创建全局数据存储实例
data_storage = DataStorage()
