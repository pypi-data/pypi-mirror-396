from typing import Dict, Any, Optional
from core.deepseek_api import deepseek_api
from core.utils import calculate_noise_score, is_whitelist_event
from config.config import settings
import logging

# 配置日志
logger = logging.getLogger(__name__)

class EventAgent:
    def __init__(self):
        self.system_prompt = """你是一位资深的安全事件运营专家，负责事件研判分析、告警降噪研判、响应处置和报告总结。
请根据提供的事件信息，以自然语言方式输出研判结论、依据以及关联攻击过程解读、溯源调查、响应处置策略。

输出格式要求：
1. 研判结论：明确说明事件是否为真实攻击，攻击类型是什么
2. 研判依据：列出支持结论的关键证据
3. 攻击过程：描述攻击的完整流程和技术细节
4. 溯源分析：分析攻击来源和相关情报
5. 响应策略：提供具体的处置建议和防护措施

请确保你的分析专业、准确、全面，能够帮助安全运营人员快速理解和处置事件。"""
    
    def analyze_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析安全事件"""
        try:
            # 检查是否为白名单事件
            event_type = event_data.get("event_type", "")
            if is_whitelist_event(event_type, settings.whitelist_events):
                if settings.skip_ai_for_whitelist:
                    return {
                        "conclusion": "白名单事件，跳过AI研判",
                        "reason": "事件类型在白名单中",
                        "priority": "低",
                        "is_attack": False
                    }
            
            # 构建提示词
            prompt = f"""请分析以下安全事件：
{event_data}

请按照要求的格式输出分析结果。"""
            
            # 调用DeepSeek API
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "analysis": response,
                "event_id": event_data.get("event_id", "")
            }
        except Exception as e:
            logger.error(f"Event analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def reduce_noise(self, alert_data: Dict[str, Any], manual_adjustment: float = 0.0) -> Dict[str, Any]:
        """告警降噪研判"""
        try:
            # 构建提示词进行降噪分析
            prompt = f"""请对以下告警进行降噪研判，评估其真实性和风险级别：
{alert_data}

请输出：
1. 降噪评分（0-1，1表示高风险，0表示低风险）
2. 风险级别（高、中、低）
3. 降噪理由
4. 是否为误报"""
            
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            # 提取降噪评分（这里简化处理，实际应从AI响应中提取）
            noise_score = 0.7  # 示例值，实际应从AI响应中解析
            
            # 应用人工调整
            if settings.allow_manual_adjustment:
                noise_score += manual_adjustment
                noise_score = max(0.0, min(1.0, noise_score))  # 确保在0-1范围内
            
            # 确定风险级别
            if noise_score >= 0.7:
                risk_level = "高"
            elif noise_score >= 0.3:
                risk_level = "中"
            else:
                risk_level = "低"
            
            return {
                "success": True,
                "noise_score": noise_score,
                "risk_level": risk_level,
                "ai_analysis": response,
                "manual_adjustment": manual_adjustment
            }
        except Exception as e:
            logger.error(f"Noise reduction error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def respond_to_incident(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """响应处置建议"""
        try:
            prompt = f"""请针对以下安全事件提供详细的响应处置策略：
{incident_data}

请输出：
1. 立即处置措施
2. 短期修复方案
3. 长期防护建议
4. 责任部门和人员
5. 预期效果评估"""
            
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "response_strategy": response,
                "incident_id": incident_data.get("incident_id", "")
            }
        except Exception as e:
            logger.error(f"Incident response error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_summary(self, events: list[Dict[str, Any]]) -> Dict[str, Any]:
        """生成事件总结报告"""
        try:
            prompt = f"""请对以下一系列安全事件进行总结分析：
{events}

请输出：
1. 事件总体概述
2. 主要攻击类型统计
3. 关键威胁趋势
4. 安全状况评估
5. 改进建议"""
            
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "summary_report": response,
                "event_count": len(events)
            }
        except Exception as e:
            logger.error(f"Summary generation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
