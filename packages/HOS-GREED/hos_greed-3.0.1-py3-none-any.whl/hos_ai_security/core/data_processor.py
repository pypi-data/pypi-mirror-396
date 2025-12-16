from typing import Dict, Any, List, Optional
import json
import logging
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)

class DataProcessor:
    """数据处理模块，负责安全数据的标准化处理"""
    
    def __init__(self):
        # 定义支持的数据类型和标准化模板
        self.data_templates = {
            "event": {
                "required_fields": ["event_id", "event_type", "timestamp", "source", "target"],
                "optional_fields": ["severity", "description", "raw_data", "tags"]
            },
            "log": {
                "required_fields": ["log_id", "timestamp", "source", "content"],
                "optional_fields": ["log_type", "severity", "tags"]
            },
            "vulnerability": {
                "required_fields": ["vuln_id", "name", "severity", "target"],
                "optional_fields": ["description", "cvss_score", "remediation", "tags"]
            },
            "traffic": {
                "required_fields": ["traffic_id", "timestamp", "source_ip", "destination_ip", "protocol"],
                "optional_fields": ["source_port", "destination_port", "bytes_sent", "bytes_received", "tags"]
            },
            "alert": {
                "required_fields": ["alert_id", "timestamp", "alert_type", "source", "target"],
                "optional_fields": ["severity", "description", "confidence", "tags"]
            }
        }
    
    def standardize_data(self, data: Any, data_type: str) -> Dict[str, Any]:
        """将数据标准化为统一格式"""
        try:
            if data_type not in self.data_templates:
                raise ValueError(f"不支持的数据类型: {data_type}")
            
            template = self.data_templates[data_type]
            standardized_data = {}
            
            # 处理必填字段
            for field in template["required_fields"]:
                if isinstance(data, dict) and field in data:
                    standardized_data[field] = data[field]
                else:
                    # 生成默认值或标记缺失
                    standardized_data[field] = self._get_default_value(field, data_type)
            
            # 处理可选字段
            if isinstance(data, dict):
                for field in template["optional_fields"]:
                    if field in data:
                        standardized_data[field] = data[field]
            
            # 添加标准化元数据
            standardized_data["_standardized"] = True
            standardized_data["_data_type"] = data_type
            standardized_data["_processed_time"] = datetime.now().isoformat()
            
            return standardized_data
        except Exception as e:
            logger.error(f"数据标准化失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_default_value(self, field: str, data_type: str) -> Any:
        """获取字段的默认值"""
        if field == "event_id" or field == "log_id" or field == "vuln_id" or field == "traffic_id" or field == "alert_id":
            return f"{data_type}_default_{datetime.now().timestamp()}"
        elif field == "timestamp":
            return datetime.now().isoformat()
        elif field in ["severity", "confidence"]:
            return "medium"
        elif field in ["source", "target", "source_ip", "destination_ip", "event_type", "log_type", "vuln_name", "alert_type", "protocol"]:
            return "unknown"
        elif field in ["description", "content"]:
            return ""
        elif field in ["raw_data", "remediation", "tags"]:
            return []
        elif field in ["cvss_score"]:
            return 0.0
        elif field in ["source_port", "destination_port", "bytes_sent", "bytes_received"]:
            return 0
        else:
            return None
    
    def convert_data_format(self, data: Any, from_format: str, to_format: str) -> Any:
        """转换数据格式"""
        try:
            if from_format == to_format:
                return data
            
            if from_format == "json":
                # 从JSON转换到其他格式
                if to_format == "text":
                    return json.dumps(data, ensure_ascii=False, indent=2)
                elif to_format == "csv":
                    return self._json_to_csv(data)
                else:
                    raise ValueError(f"不支持的目标格式: {to_format}")
            elif from_format == "text":
                # 从文本转换到其他格式
                if to_format == "json":
                    return json.loads(data)
                else:
                    raise ValueError(f"不支持的目标格式: {to_format}")
            elif from_format == "csv":
                # 从CSV转换到其他格式
                if to_format == "json":
                    return self._csv_to_json(data)
                elif to_format == "text":
                    return data
                else:
                    raise ValueError(f"不支持的目标格式: {to_format}")
            else:
                raise ValueError(f"不支持的源格式: {from_format}")
        except Exception as e:
            logger.error(f"数据格式转换失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _json_to_csv(self, data: Any) -> str:
        """将JSON数据转换为CSV格式"""
        if isinstance(data, list):
            if not data:
                return ""
            # 获取所有可能的字段
            fields = set()
            for item in data:
                if isinstance(item, dict):
                    fields.update(item.keys())
            fields = sorted(fields)
            # 生成CSV header
            header = ",".join(fields)
            # 生成CSV rows
            rows = [header]
            for item in data:
                row = []
                for field in fields:
                    value = item.get(field, "")
                    # 处理包含逗号或引号的值
                    if isinstance(value, str) and ("," in value or '"' in value):
                        value = f'"{value.replace('"', '""')}"'
                    row.append(str(value))
                rows.append(",".join(row))
            return "\n".join(rows)
        elif isinstance(data, dict):
            # 单条JSON对象转换为CSV
            fields = sorted(data.keys())
            header = ",".join(fields)
            row = [str(data.get(field, "")) for field in fields]
            return f"{header}\n{','.join(row)}"
        else:
            raise ValueError("JSON数据必须是对象或数组")
    
    def _csv_to_json(self, csv_data: str) -> List[Dict[str, Any]]:
        """将CSV数据转换为JSON格式"""
        lines = csv_data.strip().split('\n')
        if not lines:
            return []
        
        # 解析header
        header = lines[0].split(',')
        # 解析rows
        result = []
        for line in lines[1:]:
            if not line.strip():
                continue
            # 处理包含逗号或引号的字段
            row = []
            current_field = ""
            in_quotes = False
            for char in line:
                if char == '"':
                    in_quotes = not in_quotes
                elif char == ',' and not in_quotes:
                    row.append(current_field)
                    current_field = ""
                else:
                    current_field += char
            row.append(current_field)
            
            # 创建JSON对象
            item = {}
            for i, field in enumerate(header):
                if i < len(row):
                    item[field.strip()] = row[i].strip()
            result.append(item)
        
        return result
    
    def validate_data(self, data: Any, data_type: str) -> Dict[str, Any]:
        """验证数据格式是否符合要求"""
        try:
            if data_type not in self.data_templates:
                return {
                    "success": False,
                    "error": f"不支持的数据类型: {data_type}"
                }
            
            template = self.data_templates[data_type]
            if not isinstance(data, dict):
                return {
                    "success": False,
                    "error": "数据必须是JSON对象"
                }
            
            # 检查必填字段
            missing_fields = [field for field in template["required_fields"] if field not in data]
            
            if missing_fields:
                return {
                    "success": False,
                    "error": f"缺少必填字段: {missing_fields}",
                    "missing_fields": missing_fields
                }
            
            return {
                "success": True,
                "message": "数据格式验证通过"
            }
        except Exception as e:
            logger.error(f"数据验证失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def batch_process(self, data_list: List[Any], data_type: str, operation: str = "standardize") -> List[Dict[str, Any]]:
        """批量处理数据"""
        results = []
        for data in data_list:
            if operation == "standardize":
                result = self.standardize_data(data, data_type)
            elif operation == "validate":
                result = self.validate_data(data, data_type)
            else:
                result = {
                    "success": False,
                    "error": f"不支持的操作: {operation}"
                }
            results.append(result)
        return results
    
    def extract_key_info(self, data: Any, fields: List[str]) -> Dict[str, Any]:
        """从数据中提取指定字段信息"""
        try:
            if not isinstance(data, dict):
                return {
                    "success": False,
                    "error": "数据必须是JSON对象"
                }
            
            extracted = {field: data.get(field) for field in fields}
            return {
                "success": True,
                "extracted_data": extracted
            }
        except Exception as e:
            logger.error(f"字段提取失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# 创建全局数据处理器实例
data_processor = DataProcessor()
