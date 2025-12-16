from typing import Dict, Any, Optional, List
from core.deepseek_api import deepseek_api
import logging

# 配置日志
logger = logging.getLogger(__name__)

class SecurityQAAgent:
    def __init__(self):
        self.system_prompt = """你是一位资深的安全领域专家，负责回答用户关于安全领域的各种问题。
请根据你的专业知识，提供准确、全面、易于理解的答案。

支持的问题类型包括：
- 安全运营相关问题
- 安全工具使用问题
- 漏洞相关问题
- 安全政策和合规问题
- 威胁情报相关问题
- 安全架构和设计问题
- 安全事件响应问题

输出格式要求：
1. 问题复述：重述用户的问题
2. 答案内容：详细回答用户问题，包含必要的技术细节
3. 相关建议：提供相关的建议或最佳实践
4. 参考资料：如有必要，提供相关的参考资料或标准

请确保你的回答专业、准确，并能帮助用户解决实际问题。"""
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """回答安全领域问题"""
        try:
            # 构建提示词
            prompt = f"""请回答以下安全领域问题：
问题：{question}

请按照要求的格式输出回答结果。"""
            
            # 调用DeepSeek API
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "question": question,
                "answer": response
            }
        except Exception as e:
            logger.error(f"Security QA error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def explain_concept(self, concept: str, depth: str = "medium") -> Dict[str, Any]:
        """解释安全概念"""
        try:
            # 构建提示词
            depth_map = {
                "basic": "请用通俗易懂的语言，简要解释",
                "medium": "请详细解释",
                "advanced": "请从专业角度深入解释，包括技术细节和相关标准"
            }
            
            depth_prompt = depth_map.get(depth, depth_map["medium"])
            
            prompt = f"""{depth_prompt}以下安全概念：
概念：{concept}

请按照要求的格式输出解释结果。"""
            
            # 调用DeepSeek API
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "concept": concept,
                "depth": depth,
                "explanation": response
            }
        except Exception as e:
            logger.error(f"Concept explanation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def provide_best_practices(self, topic: str) -> Dict[str, Any]:
        """提供安全最佳实践"""
        try:
            # 构建提示词
            prompt = f"""请提供关于{topic}的安全最佳实践：

输出要求：
1. 列出具体的最佳实践条目
2. 每个条目包含详细说明和实施建议
3. 如有相关标准或框架，提供参考
4. 说明实施这些最佳实践的好处

请按照要求的格式输出结果。"""
            
            # 调用DeepSeek API
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "topic": topic,
                "best_practices": response
            }
        except Exception as e:
            logger.error(f"Best practices error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
