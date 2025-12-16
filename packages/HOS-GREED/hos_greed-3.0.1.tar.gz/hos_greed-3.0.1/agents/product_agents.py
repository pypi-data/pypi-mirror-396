from typing import Dict, Any, List, Optional
from core.deepseek_api import deepseek_api
import logging

# 配置日志
logger = logging.getLogger(__name__)

class BaseProductAgent:
    """基础产品智能体类"""
    def __init__(self, product_type: str):
        self.product_type = product_type
        self.system_prompt = f"""你是一位专业的{product_type}安全产品AI助手，负责分析{product_type}产生的数据，
提供智能分析、检测、预测和建议。请根据提供的数据，生成准确、专业的分析结果。"""
    
    def analyze(self, data: Any, **kwargs) -> Dict[str, Any]:
        """基础分析方法，子类需重写"""
        raise NotImplementedError("子类必须实现analyze方法")



class VulnerabilityScannerAgent(BaseProductAgent):
    """漏洞扫描系统专用智能体"""
    def __init__(self):
        super().__init__("漏洞扫描系统")
        self.system_prompt = f"""你是一位专业的漏洞扫描系统AI助手，负责：
1. 分析漏洞扫描结果，评估漏洞风险
2. 提供漏洞修复建议
3. 生成漏洞报告
4. 预测漏洞被利用的可能性

请根据提供的漏洞扫描数据，生成准确、专业的分析结果。"""
    
    def analyze_vulnerability(self, vulnerability_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析漏洞数据"""
        try:
            prompt = f"""请分析以下漏洞数据：
{vulnerability_data}

请输出：
1. 漏洞评级：高危、中危、低危
2. 影响评估：受影响的系统、组件和数据
3. 利用难度：简单、中等、复杂
4. 修复建议：具体的修复步骤和优先级
5. 验证方法：如何验证漏洞是否已修复
6. 风险预测：该漏洞被利用的可能性

请确保分析专业、准确，符合漏洞管理的最佳实践。"""
            
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "analysis": response,
                "vuln_id": vulnerability_data.get("vuln_id", "")
            }
        except Exception as e:
            logger.error(f"Vulnerability analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

class FirewallAgent(BaseProductAgent):
    """防火墙专用智能体"""
    def __init__(self):
        super().__init__("防火墙")
        self.system_prompt = f"""你是一位专业的防火墙AI助手，负责：
1. 分析防火墙日志和流量数据
2. 检测异常流量和攻击行为
3. 优化防火墙规则
4. 提供安全策略建议

请根据提供的防火墙数据，生成准确、专业的分析结果。"""
    
    def analyze_traffic(self, traffic_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析防火墙流量数据"""
        try:
            prompt = f"""请分析以下防火墙流量数据：
{traffic_data}

请输出：
1. 流量分析：主要流量类型、来源和目标
2. 异常检测：是否存在异常流量或攻击行为
3. 攻击类型：如果检测到攻击，说明攻击类型和特征
4. 规则优化：是否需要调整防火墙规则
5. 安全建议：提供具体的安全策略建议

请确保分析专业、准确，符合防火墙管理的最佳实践。"""
            
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "analysis": response,
                "traffic_summary": traffic_data.get("summary", "")
            }
        except Exception as e:
            logger.error(f"Firewall traffic analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

class WAFAgent(BaseProductAgent):
    """Web应用防火墙专用智能体"""
    def __init__(self):
        super().__init__("Web应用防火墙")
        self.system_prompt = f"""你是一位专业的Web应用防火墙AI助手，负责：
1. 分析WAF日志和攻击数据
2. 检测Web攻击和异常请求
3. 优化WAF规则
4. 提供Web应用安全建议

请根据提供的WAF数据，生成准确、专业的分析结果。"""
    
    def analyze_attack(self, attack_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析WAF攻击数据"""
        try:
            prompt = f"""请分析以下WAF攻击数据：
{attack_data}

请输出：
1. 攻击分析：攻击类型、特征和目标
2. 威胁评估：攻击的严重程度和可能的影响
3. 规则优化：是否需要调整WAF规则
4. 防护建议：提供具体的Web应用防护措施
5. 溯源分析：攻击来源和可能的攻击者

请确保分析专业、准确，符合Web应用安全的最佳实践。"""
            
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "analysis": response,
                "attack_id": attack_data.get("attack_id", "")
            }
        except Exception as e:
            logger.error(f"WAF attack analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

class BastionHostAgent(BaseProductAgent):
    """堡垒机专用智能体"""
    def __init__(self):
        super().__init__("堡垒机")
        self.system_prompt = f"""你是一位专业的堡垒机AI助手，负责：
1. 分析堡垒机访问日志
2. 检测异常访问和操作行为
3. 提供身份认证和授权建议
4. 生成合规审计报告

请根据提供的堡垒机数据，生成准确、专业的分析结果。"""
    
    def analyze_access(self, access_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析堡垒机访问数据"""
        try:
            prompt = f"""请分析以下堡垒机访问数据：
{access_data}

请输出：
1. 访问分析：主要访问模式、用户和资源
2. 异常检测：是否存在异常访问或操作行为
3. 风险评估：访问行为的风险等级
4. 合规建议：是否符合安全合规要求
5. 优化建议：提供身份认证和授权优化建议

请确保分析专业、准确，符合堡垒机管理的最佳实践。"""
            
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "analysis": response,
                "access_id": access_data.get("access_id", "")
            }
        except Exception as e:
            logger.error(f"Bastion host access analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

class DLPAgent(BaseProductAgent):
    """数据防泄漏系统专用智能体"""
    def __init__(self):
        super().__init__("数据防泄漏系统")
        self.system_prompt = f"""你是一位专业的数据防泄漏系统AI助手，负责：
1. 分析数据传输和存储行为
2. 检测敏感数据泄漏风险
3. 优化数据分类和保护策略
4. 提供数据安全建议

请根据提供的DLP数据，生成准确、专业的分析结果。"""
    
    def analyze_data_flow(self, data_flow: Dict[str, Any]) -> Dict[str, Any]:
        """分析数据流转数据"""
        try:
            prompt = f"""请分析以下数据流转数据：
{data_flow}

请输出：
1. 数据分类：识别敏感数据类型和级别
2. 风险评估：数据流转的泄漏风险
3. 异常检测：是否存在异常数据传输行为
4. 保护建议：提供数据分类和保护策略
5. 合规建议：是否符合数据保护法规要求

请确保分析专业、准确，符合数据安全的最佳实践。"""
            
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "analysis": response,
                "flow_id": data_flow.get("flow_id", "")
            }
        except Exception as e:
            logger.error(f"DLP data flow analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# 产品智能体映射
product_agents = {
    "vulnerability_scanner": VulnerabilityScannerAgent(),
    "firewall": FirewallAgent(),
    "waf": WAFAgent(),
    "bastion": BastionHostAgent(),
    "dlp": DLPAgent()
}
