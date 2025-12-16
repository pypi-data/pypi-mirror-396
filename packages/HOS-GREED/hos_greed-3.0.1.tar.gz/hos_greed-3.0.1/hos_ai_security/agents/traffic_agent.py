from typing import Dict, Any, Optional
from core.deepseek_api import deepseek_api
import logging

# 配置日志
logger = logging.getLogger(__name__)

class TrafficAgent:
    def __init__(self):
        self.system_prompt = """你是一位专业的网络流量分析专家，负责对PCAP包进行检测和分析，识别其中的攻击行为。
请根据提供的PCAP包分析结果或相关流量信息，检测是否存在攻击行为，并对攻击行为进行详细解读。

支持的分析类型包括：
- PCAP包文件分析
- 网络流量特征分析
- 攻击行为检测
- 异常流量识别

输出格式要求：
1. 分析概述：简要说明分析的范围和方法
2. 流量统计：提供流量的基本统计信息
3. 攻击检测结果：列出检测到的攻击行为
4. 攻击详情：详细描述每个攻击的技术细节和影响
5. 证据链：提供支持攻击检测的证据
6. 建议措施：提供针对检测结果的处置建议

请确保你的分析专业、准确，并能为安全运营提供有价值的参考。"""
    
    def analyze_pcap(self, pcap_info: Dict[str, Any]) -> Dict[str, Any]:
        """分析PCAP包"""
        try:
            # 构建提示词
            prompt = f"""请分析以下PCAP包信息，检测是否存在攻击行为：
PCAP包信息：{pcap_info}

分析要求：
- 检测是否存在攻击行为
- 识别攻击类型和技术细节
- 分析攻击的影响范围
- 提供攻击的证据链
- 给出处置建议

请按照要求的格式输出分析结果。"""
            
            # 调用DeepSeek API
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "analysis_type": "PCAP包分析",
                "analysis_result": response,
                "pcap_id": pcap_info.get("pcap_id", "")
            }
        except Exception as e:
            logger.error(f"PCAP analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def detect_attacks(self, traffic_data: Dict[str, Any]) -> Dict[str, Any]:
        """检测网络流量中的攻击行为"""
        try:
            # 构建提示词
            prompt = f"""请检测以下网络流量数据中的攻击行为：
流量数据：{traffic_data}

检测要求：
- 识别所有可能的攻击行为
- 分类攻击类型（如DDoS、SQL注入、XSS等）
- 评估攻击的严重程度
- 提供攻击的特征描述
- 建议相应的防护措施

请按照要求的格式输出检测结果。"""
            
            # 调用DeepSeek API
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "detection_type": "流量攻击检测",
                "detection_result": response,
                "traffic_summary": traffic_data.get("summary", "")
            }
        except Exception as e:
            logger.error(f"Attack detection error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_traffic_pattern(self, traffic_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """分析流量模式"""
        try:
            # 构建提示词
            prompt = f"""请分析以下网络流量模式，识别异常情况：
流量模式数据：{traffic_patterns}

分析要求：
- 识别异常流量模式
- 分析异常的可能原因
- 评估异常的影响
- 提供监控和防护建议

请按照要求的格式输出分析结果。"""
            
            # 调用DeepSeek API
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "analysis_type": "流量模式分析",
                "analysis_result": response
            }
        except Exception as e:
            logger.error(f"Traffic pattern analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
