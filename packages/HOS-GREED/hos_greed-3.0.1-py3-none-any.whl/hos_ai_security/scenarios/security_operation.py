from typing import Dict, Any, List
from ..agents import EventAgent, ReportAgent, SecurityQAAgent
from ..agents.product_agents import product_agents

class SecurityOperationScenario:
    """AI安全运营场景"""
    
    description = "AI安全运营场景，实现事件分析、报告生成、趋势预测等功能"
    
    def __init__(self):
        self.event_agent = EventAgent()
        self.report_agent = ReportAgent()
        self.security_qa_agent = SecurityQAAgent()
    
    def execute(self, data: Any, **kwargs) -> Dict[str, Any]:
        """执行安全运营场景"""
        operation_type = kwargs.get("operation_type", "analysis")
        
        if operation_type == "event_analysis":
            return self.analyze_event(data, **kwargs)
        elif operation_type == "report_generation":
            return self.generate_report(data, **kwargs)
        elif operation_type == "trend_analysis":
            return self.analyze_trend(data, **kwargs)
        elif operation_type == "incident_response":
            return self.respond_to_incident(data, **kwargs)
        else:
            return {
                "success": False,
                "error": f"不支持的操作类型: {operation_type}"
            }
    
    def analyze_event(self, event_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """分析安全事件"""
        try:
            # 使用通用事件分析智能体
            result = self.event_agent.analyze_event(event_data)
            
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_report(self, report_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """生成安全报告"""
        try:
            report_type = kwargs.get("report_type", "event")
            
            if report_type == "event":
                result = self.report_agent.generate_event_report(report_data)
            else:
                result = self.report_agent.generate_statistical_report(
                    report_data.get("events", []),
                    report_data.get("time_range", "")
                )
            
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_trend(self, trend_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """分析安全趋势"""
        try:
            events = trend_data.get("events", [])
            time_range = trend_data.get("time_range", "")
            
            # 构建趋势分析提示词
            prompt = f"""请分析以下安全事件的趋势：
时间范围：{time_range}
事件数据：{events}

请输出：
1. 事件数量变化趋势
2. 主要攻击类型分布
3. 关键威胁趋势
4. 安全状况评估
5. 改进建议

请确保分析专业、准确，能够帮助安全运营人员了解安全态势。"""
            
            # 使用安全问答智能体进行趋势分析
            result = self.security_qa_agent.answer_question(prompt)
            
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def respond_to_incident(self, incident_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """响应安全事件"""
        try:
            # 使用事件智能体生成响应策略
            result = self.event_agent.respond_to_incident(incident_data)
            
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
