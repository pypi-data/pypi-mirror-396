from typing import Dict, Any, List
from agents import SecurityQAAgent
from agents.product_agents import product_agents

class DataSecurityScenario:
    """数据安全场景"""
    
    description = "数据安全场景，实现数据分类分级、数据防泄漏监控、异常行为检测等功能"
    
    def __init__(self):
        self.security_qa_agent = SecurityQAAgent()
        self.dlp_agent = product_agents.get("dlp")
    
    def execute(self, data: Any, **kwargs) -> Dict[str, Any]:
        """执行数据安全场景"""
        security_type = kwargs.get("security_type", "classification")
        
        if security_type == "data_classification":
            return self.classify_data(data, **kwargs)
        elif security_type == "dlp_monitoring":
            return self.monitor_dlp(data, **kwargs)
        elif security_type == "anomaly_detection":
            return self.detect_data_anomaly(data, **kwargs)
        elif security_type == "compliance_assessment":
            return self.assess_compliance(data, **kwargs)
        else:
            return {
                "success": False,
                "error": f"不支持的数据安全类型: {security_type}"
            }
    
    def classify_data(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """数据分类分级"""
        try:
            prompt = f"""请对以下数据进行分类分级：
{data}

请输出：
1. 数据分类：数据的类别（如个人信息、财务数据、技术文档等）
2. 数据分级：数据的敏感级别（如绝密、机密、秘密、公开等）
3. 保护措施：针对该级别数据的保护措施
4. 合规要求：相关的合规法规要求
5. 处理建议：数据的存储、传输和处理建议"""
            
            result = self.security_qa_agent.answer_question(prompt)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def monitor_dlp(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """数据防泄漏监控"""
        try:
            if self.dlp_agent and hasattr(self.dlp_agent, "analyze_data_flow"):
                # 使用DLP专用智能体
                result = self.dlp_agent.analyze_data_flow(data)
            else:
                # 使用通用安全知识智能体
                prompt = f"""请分析以下数据传输和存储行为，检测敏感数据泄漏风险：
{data}

请输出：
1. 风险检测：是否存在敏感数据泄漏风险
2. 风险等级：评估的风险等级
3. 风险描述：具体的风险点和原因
4. 保护建议：如何防止数据泄漏
5. 监控建议：如何监控数据传输和存储"""
                result = self.security_qa_agent.answer_question(prompt)
            
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def detect_data_anomaly(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """数据访问异常检测"""
        try:
            prompt = f"""请分析以下数据访问行为，检测异常情况：
{data}

请输出：
1. 异常检测：是否存在异常数据访问行为
2. 异常类型：异常的具体类型（如越权访问、异常时间访问、异常频率访问等）
3. 风险评估：异常行为的风险等级
4. 原因分析：可能导致异常的原因
5. 处置建议：如何处理和防范此类异常"""
            
            result = self.security_qa_agent.answer_question(prompt)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def assess_compliance(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """数据合规评估"""
        try:
            prompt = f"""请评估以下数据处理行为的合规性：
{data}

请输出：
1. 合规性评估：是否符合相关法规要求
2. 适用法规：适用的数据保护法规（如GDPR、CCPA、个人信息保护法等）
3. 合规差距：存在的合规差距和问题
4. 整改建议：如何整改以符合合规要求
5. 合规证明：如何证明数据处理的合规性"""
            
            result = self.security_qa_agent.answer_question(prompt)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
