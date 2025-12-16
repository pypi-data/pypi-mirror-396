from typing import Dict, Any, List
from agents import SecurityQAAgent

class KnowledgeQAScenario:
    """知识问答场景"""
    
    description = "知识问答场景，实现安全知识查询、专家咨询、安全策略建议等功能"
    
    def __init__(self):
        self.security_qa_agent = SecurityQAAgent()
    
    def execute(self, data: Any, **kwargs) -> Dict[str, Any]:
        """执行知识问答场景"""
        qa_type = kwargs.get("qa_type", "security_knowledge")
        
        if qa_type == "security_knowledge":
            return self.query_security_knowledge(data, **kwargs)
        elif qa_type == "expert_consult":
            return self.expert_consult(data, **kwargs)
        elif qa_type == "policy_suggestion":
            return self.policy_suggestion(data, **kwargs)
        else:
            return {
                "success": False,
                "error": f"不支持的问答类型: {qa_type}"
            }
    
    def query_security_knowledge(self, query: str, **kwargs) -> Dict[str, Any]:
        """查询安全知识"""
        try:
            result = self.security_qa_agent.answer_question(query)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def expert_consult(self, question: str, **kwargs) -> Dict[str, Any]:
        """专家咨询"""
        try:
            result = self.security_qa_agent.answer_question(question)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def policy_suggestion(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """安全策略建议"""
        try:
            # 优化降噪评分推荐机制，支持人工通过加减分配置来调整推荐结果
            # 支持多种高可信、高风险模版切换
            prompt = f"""请根据以下数据提供安全策略建议：
{data}

请输出：
1. 推荐策略：具体的安全策略建议
2. 评分调整：支持人工通过加减分配置来调整推荐结果
3. 模版建议：支持多种高可信、高风险模版切换
4. 风险等级：评估的风险等级
5. 建议措施：具体的建议措施"""
            
            result = self.security_qa_agent.answer_question(prompt)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }