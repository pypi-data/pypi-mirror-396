from typing import Dict, Any, List
from agents import TrafficAgent, EventAgent, LogParserAgent
from agents.product_agents import product_agents

class DetectionResponseScenario:
    """AI检测响应场景"""
    
    description = "AI检测响应场景，实现异常检测、攻击识别、威胁响应等功能"
    
    def __init__(self):
        self.traffic_agent = TrafficAgent()
        self.event_agent = EventAgent()
        self.log_parser_agent = LogParserAgent()
        self.firewall_agent = product_agents.get("firewall")
        self.waf_agent = product_agents.get("waf")
    
    def execute(self, data: Any, **kwargs) -> Dict[str, Any]:
        """执行检测响应场景"""
        detection_type = kwargs.get("detection_type", "traffic")
        
        if detection_type == "traffic_analysis":
            return self.analyze_traffic(data, **kwargs)
        elif detection_type == "attack_detection":
            return self.detect_attack(data, **kwargs)
        elif detection_type == "anomaly_detection":
            return self.detect_anomaly(data, **kwargs)
        elif detection_type == "threat_hunting":
            return self.hunt_threats(data, **kwargs)
        else:
            return {
                "success": False,
                "error": f"不支持的检测类型: {detection_type}"
            }
    
    def analyze_traffic(self, traffic_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """分析网络流量"""
        try:
            product_type = kwargs.get("product_type", "firewall")
            
            if product_type == "firewall" and self.firewall_agent:
                # 使用防火墙专用智能体
                result = self.firewall_agent.analyze_traffic(traffic_data)
            elif product_type == "waf" and self.waf_agent:
                # 使用WAF专用智能体
                result = self.waf_agent.analyze_attack(traffic_data)
            else:
                # 使用通用流量分析智能体
                result = self.traffic_agent.detect_attacks(traffic_data)
            
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def detect_attack(self, attack_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """检测攻击行为"""
        try:
            product_type = kwargs.get("product_type", "firewall")
            
            if product_type == "firewall" and self.firewall_agent:
                # 使用防火墙专用智能体
                result = self.firewall_agent.analyze_traffic(attack_data)
            elif product_type == "waf" and self.waf_agent:
                # 使用WAF专用智能体
                result = self.waf_agent.analyze_attack(attack_data)
            else:
                # 使用通用流量分析智能体
                result = self.traffic_agent.detect_attacks(attack_data)
            
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def detect_anomaly(self, log_data: Any, **kwargs) -> Dict[str, Any]:
        """检测异常行为"""
        try:
            # 解析日志
            parse_result = self.log_parser_agent.parse_log(log_data)
            
            if not parse_result["success"]:
                return parse_result
            
            # 检测异常
            parsed_log = parse_result["parsed_result"]
            
            prompt = f"""请分析以下解析后的日志，检测是否存在异常行为：
{parsed_log}

请输出：
1. 异常检测结果：是否存在异常
2. 异常类型：如果存在异常，说明异常类型
3. 异常特征：描述异常的具体特征
4. 风险等级：高、中、低
5. 处理建议：如何处理该异常

请确保分析专业、准确，能够帮助安全运营人员快速识别和处理异常。"""
            
            result = self.event_agent.analyze_event({"event_data": parsed_log})
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def hunt_threats(self, data: Any, **kwargs) -> Dict[str, Any]:
        """威胁狩猎"""
        try:
            prompt = f"""请对以下数据进行威胁狩猎分析，寻找潜在的安全威胁：
{data}

请输出：
1. 威胁狩猎结果：是否发现潜在威胁
2. 威胁类型：威胁的具体类型
3. 威胁特征：威胁的技术特征和行为模式
4. 影响范围：威胁可能影响的系统和数据
5. 建议措施：如何进一步调查和缓解该威胁

请确保分析专业、全面，能够帮助安全运营人员发现潜在威胁。"""
            
            result = self.event_agent.analyze_event({"event_data": data})
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
