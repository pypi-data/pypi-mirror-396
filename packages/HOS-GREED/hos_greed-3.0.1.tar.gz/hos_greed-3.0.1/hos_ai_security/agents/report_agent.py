from typing import Dict, Any, Optional, List
from core.deepseek_api import deepseek_api
import logging

# 配置日志
logger = logging.getLogger(__name__)

class ReportAgent:
    def __init__(self):
        self.system_prompt = """你是一位专业的安全报告生成专家，负责生成各类安全事件报告和统计报告。
请根据提供的数据和报告类型，生成结构清晰、内容全面、专业规范的报告。

支持的报告类型包括：
- 单一事件报告：详细分析单个安全事件的发生、影响、处置过程等
- 统计报告：对指定时间周期内的安全事件进行统计分析
- 趋势报告：分析安全事件的发展趋势和规律
- 处置报告：记录安全事件的响应和处置过程

输出格式要求：
1. 报告标题：清晰描述报告内容和时间范围
2. 报告摘要：简要概括报告的主要内容和结论
3. 目录：列出报告的主要章节
4. 详细内容：按照逻辑结构组织报告内容
5. 结论和建议：总结报告的主要结论，并提供相关建议
6. 附录：包含相关的原始数据或补充信息

请确保你的报告专业、全面、易于理解，并能为安全运营决策提供有价值的参考。"""
    
    def generate_event_report(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成单一事件报告"""
        try:
            # 构建提示词
            prompt = f"""请生成以下安全事件的详细报告：
事件数据：{event_data}

报告要求：
- 详细描述事件的发生过程
- 分析事件的影响范围和严重程度
- 记录事件的响应和处置过程
- 总结事件的教训和改进建议

请按照要求的格式输出报告。"""
            
            # 调用DeepSeek API
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "report_type": "单一事件报告",
                "report_content": response,
                "event_id": event_data.get("event_id", "")
            }
        except Exception as e:
            logger.error(f"Event report generation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_statistical_report(self, events: List[Dict[str, Any]], time_range: str) -> Dict[str, Any]:
        """生成统计报告"""
        try:
            # 构建提示词
            prompt = f"""请生成指定时间范围内的安全事件统计报告：
时间范围：{time_range}
事件数据：{events}

报告要求：
- 统计事件的数量和类型分布
- 分析事件的严重程度分布
- 总结主要的攻击类型和趋势
- 评估安全状况和改进建议

请按照要求的格式输出报告。"""
            
            # 调用DeepSeek API
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "report_type": "统计报告",
                "report_content": response,
                "time_range": time_range,
                "event_count": len(events)
            }
        except Exception as e:
            logger.error(f"Statistical report generation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_trend_report(self, events: List[Dict[str, Any]], time_range: str, comparison_period: Optional[str] = None) -> Dict[str, Any]:
        """生成趋势报告"""
        try:
            # 构建提示词
            comparison_text = f"对比周期：{comparison_period}\n" if comparison_period else ""
            prompt = f"""请生成指定时间范围内的安全事件趋势报告：
时间范围：{time_range}
{comparison_text}事件数据：{events}

报告要求：
- 分析事件数量的变化趋势
- 比较不同攻击类型的变化情况
- 识别新兴的攻击趋势和模式
- 预测未来可能的威胁方向
- 提供相应的防护建议

请按照要求的格式输出报告。"""
            
            # 调用DeepSeek API
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "report_type": "趋势报告",
                "report_content": response,
                "time_range": time_range,
                "comparison_period": comparison_period,
                "event_count": len(events)
            }
        except Exception as e:
            logger.error(f"Trend report generation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
