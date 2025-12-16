import logging
import json
import base64
import urllib.parse
from typing import Any, Dict, List, Optional
import gzip
import zlib

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_input(data: Any, expected_type: type) -> bool:
    """验证输入数据类型"""
    try:
        return isinstance(data, expected_type)
    except Exception as e:
        logger.error(f"Input validation error: {e}")
        return False

def format_response(data: Any, success: bool = True, message: str = "") -> Dict[str, Any]:
    """格式化API响应"""
    return {
        "success": success,
        "message": message,
        "data": data
    }

def decode_content(content: str, decode_type: str) -> str:
    """解码内容，支持多种解码类型"""
    try:
        if decode_type == "base64":
            return base64.b64decode(content).decode('utf-8')
        elif decode_type == "url":
            return urllib.parse.unquote(content)
        elif decode_type == "hex":
            return bytes.fromhex(content).decode('utf-8')
        elif decode_type == "gzip":
            return gzip.decompress(base64.b64decode(content)).decode('utf-8')
        elif decode_type == "deflate":
            return zlib.decompress(base64.b64decode(content)).decode('utf-8')
        elif decode_type == "ascii":
            return ''.join(chr(int(c)) for c in content.split())
        else:
            return content
    except Exception as e:
        logger.error(f"Decoding error: {e}")
        return f"Decoding failed: {str(e)}"

def calculate_noise_score(features: Dict[str, float]) -> float:
    """计算降噪评分"""
    try:
        # 简单的加权平均，可根据实际需求调整权重
        weights = {
            "attack_pattern_match": 0.3,
            "severity_level": 0.2,
            "source_reliability": 0.2,
            "historical_false_positive": 0.15,
            "contextual_analysis": 0.15
        }
        
        score = 0.0
        total_weight = 0.0
        
        for feature, weight in weights.items():
            if feature in features:
                score += features[feature] * weight
                total_weight += weight
        
        return score / total_weight if total_weight > 0 else 0.0
    except Exception as e:
        logger.error(f"Noise score calculation error: {e}")
        return 0.0

def is_whitelist_event(event_type: str, whitelist: List[str]) -> bool:
    """检查事件是否在白名单中"""
    return event_type in whitelist

def sanitize_input(input_str: str) -> str:
    """清理输入，防止注入攻击"""
    # 简单的清理，可根据实际需求扩展
    return input_str.strip()

def parse_json_safe(json_str: str) -> Optional[Dict[str, Any]]:
    """安全解析JSON"""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        logger.error("Invalid JSON format")
        return None
