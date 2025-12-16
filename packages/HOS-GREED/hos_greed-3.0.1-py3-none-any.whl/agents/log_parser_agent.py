from typing import Dict, Any, Optional
from core.deepseek_api import deepseek_api
import logging

# 配置日志
logger = logging.getLogger(__name__)

class LogParserAgent:
    def __init__(self):
        self.system_prompt = """你是一位专业的日志解析专家，负责对各类日志内容进行分析和解读。
请根据提供的日志内容，提取关键信息，分析日志含义，并以结构化方式输出解析结果。

输出格式要求：
1. 日志类型：识别日志的类型（如访问日志、安全日志、系统日志等）
2. 关键信息：提取日志中的时间、IP地址、事件类型、状态码等关键字段
3. 日志含义：解读日志所记录的事件或行为
4. 异常分析：如果日志包含异常信息，分析异常原因和影响
5. 建议行动：基于日志分析结果，提供相应的建议行动

请确保你的解析准确、全面，能够帮助用户快速理解日志内容和含义。"""
    
    def parse_log(self, log_content: str, log_type: Optional[str] = None) -> Dict[str, Any]:
        """解析日志内容"""
        try:
            # 构建提示词
            type_hint = f"日志类型：{log_type}\n" if log_type else ""
            prompt = f"""请解析以下日志内容：
{type_hint}日志内容：{log_content}

请按照要求的格式输出解析结果。"""
            
            # 调用DeepSeek API
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "parsed_result": response,
                "log_content": log_content[:100] + "..." if len(log_content) > 100 else log_content
            }
        except Exception as e:
            logger.error(f"Log parsing error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_key_info(self, log_content: str, fields: list[str]) -> Dict[str, Any]:
        """从日志中提取指定字段信息"""
        try:
            # 构建提示词
            prompt = f"""请从以下日志中提取指定字段的信息：
日志内容：{log_content}
需要提取的字段：{fields}

请以JSON格式输出结果，键为字段名，值为提取的信息。如果某个字段不存在，请返回null。"""
            
            # 调用DeepSeek API
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "extracted_fields": response,
                "log_sample": log_content[:100] + "..." if len(log_content) > 100 else log_content
            }
        except Exception as e:
            logger.error(f"Key info extraction error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_log_trend(self, logs: list[str], time_range: str) -> Dict[str, Any]:
        """分析日志趋势"""
        try:
            # 构建提示词
            prompt = f"""请分析以下日志的趋势：
时间范围：{time_range}
日志内容：{logs}

请输出：
1. 日志数量变化趋势
2. 主要事件类型分布
3. 异常情况统计
4. 潜在问题分析
5. 优化建议"""
            
            # 调用DeepSeek API
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "trend_analysis": response,
                "log_count": len(logs),
                "time_range": time_range
            }
        except Exception as e:
            logger.error(f"Log trend analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
