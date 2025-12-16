from typing import Dict, Any, Optional, List
from core.deepseek_api import deepseek_api
import logging

# 配置日志
logger = logging.getLogger(__name__)

class IntelAgent:
    def __init__(self):
        self.system_prompt = """你是一位专业的安全情报检索专家，负责检索和分析各类安全情报信息。
请根据提供的查询条件，检索相关的安全情报，并以结构化方式输出检索结果。

支持的情报类型包括：
- IP情报：IP地址的地理位置、归属信息、威胁情报等
- 域名情报：域名的注册信息、关联IP、威胁情报等
- 攻击组织情报：黑客组织的背景、攻击手法、历史活动等
- 漏洞情报：漏洞的详细信息、影响范围、修复建议等
- 恶意软件情报：恶意软件的特征、行为、传播方式等

输出格式要求：
1. 查询信息：显示查询的对象和类型
2. 检索结果：详细的情报信息
3. 威胁评估：评估该情报对象的威胁程度
4. 相关关联：相关的其他情报对象
5. 建议措施：基于情报的建议措施

请确保你的检索结果准确、全面，并能为安全决策提供有价值的参考。"""
    
    def search_ip(self, ip_address: str) -> Dict[str, Any]:
        """检索IP地址情报"""
        try:
            # 构建提示词
            prompt = f"""请检索以下IP地址的安全情报：
IP地址：{ip_address}

检索要求：
- 地理位置信息
- 归属信息（ISP、组织等）
- 威胁情报（是否为恶意IP、历史攻击记录等）
- 相关关联（关联域名、攻击活动等）
- 威胁评估和建议措施

请按照要求的格式输出检索结果。"""
            
            # 调用DeepSeek API
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "intel_type": "IP情报",
                "search_term": ip_address,
                "intel_result": response
            }
        except Exception as e:
            logger.error(f"IP intel search error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_domain(self, domain: str) -> Dict[str, Any]:
        """检索域名情报"""
        try:
            # 构建提示词
            prompt = f"""请检索以下域名的安全情报：
域名：{domain}

检索要求：
- 注册信息（注册商、注册人、注册时间等）
- 关联IP地址
- 威胁情报（是否为恶意域名、历史活动等）
- 相关关联（关联组织、攻击活动等）
- 威胁评估和建议措施

请按照要求的格式输出检索结果。"""
            
            # 调用DeepSeek API
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "intel_type": "域名情报",
                "search_term": domain,
                "intel_result": response
            }
        except Exception as e:
            logger.error(f"Domain intel search error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_attack_group(self, group_name: str) -> Dict[str, Any]:
        """检索攻击组织情报"""
        try:
            # 构建提示词
            prompt = f"""请检索以下攻击组织的安全情报：
攻击组织名称：{group_name}

检索要求：
- 组织背景和历史
- 常用攻击手法和技术
- 历史攻击活动
- 关联的其他组织或个人
- 防护建议

请按照要求的格式输出检索结果。"""
            
            # 调用DeepSeek API
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "intel_type": "攻击组织情报",
                "search_term": group_name,
                "intel_result": response
            }
        except Exception as e:
            logger.error(f"Attack group intel search error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_vulnerability(self, vuln_id: str) -> Dict[str, Any]:
        """检索漏洞情报"""
        try:
            # 构建提示词
            prompt = f"""请检索以下漏洞的安全情报：
漏洞ID：{vuln_id}

检索要求：
- 漏洞详细描述
- 影响范围和系统
- 漏洞利用方式
- 修复建议和补丁信息
- 威胁评估

请按照要求的格式输出检索结果。"""
            
            # 调用DeepSeek API
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "intel_type": "漏洞情报",
                "search_term": vuln_id,
                "intel_result": response
            }
        except Exception as e:
            logger.error(f"Vulnerability intel search error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
