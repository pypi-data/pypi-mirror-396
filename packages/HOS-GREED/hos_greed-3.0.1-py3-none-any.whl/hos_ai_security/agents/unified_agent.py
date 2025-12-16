from typing import Dict, Any, List, Optional
import logging
from ..core.deepseek_api import deepseek_api
from ..core.cache import api_cache

# 配置日志
logger = logging.getLogger(__name__)

class UnifiedAgent:
    """统一智能体，整合所有智能体功能，轻量化设计"""
    
    def __init__(self):
        # 简化的任务类型与处理函数的映射，整合为3大模块
        self.task_handlers = {
            # 安全分析模块：整合事件、日志、流量、攻击检测
            "security_analysis": self.analyze_security,
            # 安全知识模块：整合安全问答、情报检索、概念解释
            "security_knowledge": self.query_knowledge,
            # 报告生成模块：整合各类报告生成
            "report_generation": self.generate_report
        }
        
        # 简化的提示词模板库，添加产品智能体模板
        self.prompt_templates = {
            # 安全分析模块模板
            "security_analysis": """你是一位专业的安全分析师，请处理以下安全数据：
{data}

请根据数据类型，选择合适的分析方法：
1. 事件分析：判断是否为真实攻击，攻击类型，提供处置建议
2. 日志分析：识别日志类型，提取关键信息，分析异常
3. 流量分析：分析流量特征，检测异常，提供防护建议
4. 攻击检测：检测攻击行为，分析攻击类型和特征

请输出专业、准确的分析结果。""",
            
            # 安全知识模块模板
            "security_knowledge": """你是一位安全领域专家，请回答以下问题或查询：
{data}

请根据内容类型，选择合适的回答方式：
1. 安全问答：回答安全领域专业问题
2. 情报检索：提供威胁情报相关信息
3. 概念解释：解释安全概念，确保通俗易懂

请输出专业、准确、全面的回答。""",
            
            # 报告生成模块模板
            "report_generation": """请生成以下数据的安全报告：
{data}

报告要求：
1. 标题：清晰描述报告内容
2. 摘要：简要概括主要内容
3. 详细内容：按照逻辑结构组织
4. 结论与建议：总结结论并提供建议

请确保报告专业、全面、易于理解。""",
            
            # 产品智能体通用模板
            "product_analysis": """你是一位专业的{product_type}安全产品AI助手，请分析以下{product_type}数据：
{data}

请输出：
1. 数据分析：对数据进行全面分析
2. 异常检测：识别异常行为或事件
3. 风险评估：评估风险等级和影响范围
4. 优化建议：提供具体的优化和防护建议
5. 合规建议：确保符合安全合规要求

请确保分析专业、准确，符合{product_type}的最佳实践。""" 
        }
    
    def handle_request(self, task_type: str, data: Any, **kwargs) -> Dict[str, Any]:
        """处理请求，根据任务类型调用相应处理函数"""
        try:
            if task_type not in self.task_handlers:
                # 尝试意图识别
                task_type = self.recognize_intent(data)
            
            if task_type in self.task_handlers:
                handler = self.task_handlers[task_type]
                result = handler(data, **kwargs)
                return {
                    "success": True,
                    "result": result,
                    "task_type": task_type
                }
            else:
                # 通用处理，使用简化的通用模板
                result = self.general_processing(data, **kwargs)
                return {
                    "success": True,
                    "result": result,
                    "task_type": "general"
                }
        except Exception as e:
            logger.error(f"处理请求失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def recognize_intent(self, data: Any) -> str:
        """意图识别，根据数据内容判断任务类型，简化为3大类"""
        data_str = str(data).lower()
        
        # 简化的意图识别规则，将所有需求映射到3大类
        if any(keyword in data_str for keyword in ["事件", "攻击", "告警", "日志", "流量", "解码", "降噪", "检测"]):
            return "security_analysis"
        elif any(keyword in data_str for keyword in ["查询", "问答", "知识", "情报", "概念", "漏洞", "ip", "域名"]):
            return "security_knowledge"
        elif any(keyword in data_str for keyword in ["报告", "统计", "生成"]):
            return "report_generation"
        else:
            # 默认使用通用处理
            return "general"
    
    def get_prompt_template(self, task_type: str) -> str:
        """获取提示词模板"""
        return self.prompt_templates.get(task_type, "请处理以下内容：\n{data}")
    
    def general_processing(self, data: Any, **kwargs) -> str:
        """通用处理函数，带缓存支持"""
        # 尝试从缓存获取结果
        cache_key = str(data) + str(kwargs)
        cached_result = api_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # 缓存未命中，调用API
        prompt = f"请处理以下内容：\n{data}"
        result = deepseek_api.generate_text(prompt)
        
        # 将结果存入缓存
        api_cache.set(cache_key, result)
        
        return result
    
    def analyze_security(self, data: Any, **kwargs) -> str:
        """整合的安全分析模块，处理事件、日志、流量、攻击检测等"""
        # 尝试从缓存获取结果
        cache_key = f"security_analysis_{str(data)}{str(kwargs)}"
        cached_result = api_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        prompt = self.get_prompt_template("security_analysis").format(data=data)
        result = deepseek_api.generate_text(prompt)
        
        # 将结果存入缓存
        api_cache.set(cache_key, result)
        
        return result
    
    def query_knowledge(self, data: Any, **kwargs) -> str:
        """整合的安全知识模块，处理安全问答、情报检索、概念解释等"""
        # 尝试从缓存获取结果
        cache_key = f"knowledge_query_{str(data)}{str(kwargs)}"
        cached_result = api_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        prompt = self.get_prompt_template("security_knowledge").format(data=data)
        result = deepseek_api.generate_text(prompt)
        
        # 将结果存入缓存
        api_cache.set(cache_key, result)
        
        return result
    
    def generate_report(self, data: Any, **kwargs) -> str:
        """整合的报告生成模块，处理各类安全报告生成"""
        # 尝试从缓存获取结果
        cache_key = f"report_gen_{str(data)}{str(kwargs)}"
        cached_result = api_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        prompt = self.get_prompt_template("report_generation").format(data=data)
        result = deepseek_api.generate_text(prompt)
        
        # 将结果存入缓存
        api_cache.set(cache_key, result)
        
        return result
    
    def analyze_product(self, product_type: str, data: Any, **kwargs) -> str:
        """产品智能体通用分析方法"""
        # 尝试从缓存获取结果
        cache_key = f"product_analysis_{product_type}_{str(data)}{str(kwargs)}"
        cached_result = api_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        prompt = self.get_prompt_template("product_analysis").format(product_type=product_type, data=data)
        result = deepseek_api.generate_text(prompt)
        
        # 将结果存入缓存
        api_cache.set(cache_key, result)
        
        return result

# 创建全局统一智能体实例
unified_agent = UnifiedAgent()
