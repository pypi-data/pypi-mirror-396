from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from agents import (
    EventAgent,
    LogParserAgent,
    DecoderAgent,
    ReportAgent,
    TrafficAgent,
    IntelAgent,
    SecurityQAAgent
)
from agents.product_agents import product_agents

# 初始化智能体
agents = {
    "event": EventAgent(),
    "log_parser": LogParserAgent(),
    "decoder": DecoderAgent(),
    "report": ReportAgent(),
    "traffic": TrafficAgent(),
    "intel": IntelAgent(),
    "security_qa": SecurityQAAgent()
}

router = APIRouter()

# 基础模型定义
class BaseRequest(BaseModel):
    product_type: str  # 安全产品类型：data_aggregation_platform, vulnerability_scanner, firewall, waf, bastion, dlp, etc.
    data_type: str      # 数据类型：event, log, vulnerability, traffic, alert, etc.
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# 分析请求模型
class AnalysisRequest(BaseRequest):
    data: Any           # 原始数据，可以是单个对象或数组
    analysis_type: Optional[str] = None  # 分析类型：detection, classification, prediction, etc.
    parameters: Optional[Dict[str, Any]] = None  # 额外参数

# 报告生成请求模型
class ReportRequest(BaseRequest):
    data: List[Any]     # 报告数据，通常是多个对象
    report_type: str    # 报告类型：event, statistical, trend, compliance, etc.
    time_range: Optional[str] = None
    format: Optional[str] = "text"  # 报告格式：text, html, pdf, etc.

# 响应模型
class AnalysisResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    result: Any
    confidence: Optional[float] = None  # 置信度，0-1
    recommendations: Optional[List[str]] = None  # 建议措施
    processing_time: Optional[float] = None  # 处理时间（秒）
    request_id: Optional[str] = None

# 事件分析接口
@router.post("/analyze/event", summary="事件分析与研判", response_model=AnalysisResponse)
async def analyze_event(request: AnalysisRequest):
    """分析安全事件，适用于数据汇总平台、防火墙、WAF等产品"""
    try:
        # 根据产品类型选择合适的智能体
        if request.product_type in product_agents:
            # 使用产品专用智能体
            product_agent = product_agents[request.product_type]
            if hasattr(product_agent, "analyze_event"):
                result = product_agent.analyze_event(request.data)
            else:
                # 使用通用事件分析智能体
                result = agents["event"].analyze_event(request.data)
        else:
            # 使用通用事件分析智能体
            result = agents["event"].analyze_event(request.data)
        
        return AnalysisResponse(
            success=result["success"],
            result=result["analysis"] if "analysis" in result else result,
            confidence=0.9 if result["success"] else 0.0,
            recommendations=["建议进一步验证事件真实性", "检查相关系统日志"],
            message="事件分析完成"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 日志分析接口
@router.post("/analyze/log", summary="日志解析与分析", response_model=AnalysisResponse)
async def analyze_log(request: AnalysisRequest):
    """分析各类安全日志，适用于所有安全产品"""
    try:
        result = agents["log_parser"].parse_log(request.data, request.parameters.get("log_type") if request.parameters else None)
        return AnalysisResponse(
            success=result["success"],
            result=result["parsed_result"] if "parsed_result" in result else result,
            confidence=0.85 if result["success"] else 0.0,
            recommendations=["定期分析日志趋势", "关注异常日志模式"],
            message="日志分析完成"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 漏洞分析接口
@router.post("/analyze/vulnerability", summary="漏洞分析与评级", response_model=AnalysisResponse)
async def analyze_vulnerability(request: AnalysisRequest):
    """分析漏洞信息，适用于漏洞扫描系统"""
    try:
        # 使用安全知识问答智能体进行漏洞分析
        prompt = f"请分析以下漏洞信息：{request.data}\n请提供漏洞评级、影响范围、利用难度和修复建议"
        result = agents["security_qa"].answer_question(prompt)
        return AnalysisResponse(
            success=result["success"],
            result=result["answer"],
            confidence=0.92 if result["success"] else 0.0,
            recommendations=["优先修复高危漏洞", "定期进行漏洞扫描"],
            message="漏洞分析完成"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 流量分析接口
@router.post("/analyze/traffic", summary="流量检测与分析", response_model=AnalysisResponse)
async def analyze_traffic(request: AnalysisRequest):
    """分析网络流量，适用于防火墙、WAF等产品"""
    try:
        result = agents["traffic"].detect_attacks(request.data)
        return AnalysisResponse(
            success=result["success"],
            result=result["detection_result"] if "detection_result" in result else result,
            confidence=0.88 if result["success"] else 0.0,
            recommendations=["检查网络设备配置", "监控异常流量源"],
            message="流量分析完成"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 响应处置建议接口
@router.post("/respond", summary="响应处置建议", response_model=AnalysisResponse)
async def respond_to_incident(request: AnalysisRequest):
    """提供安全事件响应处置建议，适用于所有安全产品"""
    try:
        result = agents["event"].respond_to_incident(request.data)
        return AnalysisResponse(
            success=result["success"],
            result=result["response_strategy"],
            confidence=0.95 if result["success"] else 0.0,
            recommendations=result.get("recommendations", []),
            message="响应建议生成完成"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 知识问答接口
@router.post("/query", summary="安全知识问答", response_model=AnalysisResponse)
async def security_query(request: AnalysisRequest):
    """提供安全知识问答服务，适用于所有安全产品"""
    try:
        result = agents["security_qa"].answer_question(request.data)
        return AnalysisResponse(
            success=result["success"],
            result=result["answer"],
            confidence=0.9 if result["success"] else 0.0,
            message="知识查询完成"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 报告生成接口
@router.post("/generate/report", summary="报告生成", response_model=AnalysisResponse)
async def generate_report(request: ReportRequest):
    """生成安全报告，适用于数据汇总平台、漏洞扫描系统等"""
    try:
        if request.report_type == "event":
            result = agents["report"].generate_event_report(request.data[0] if request.data else {})
        else:
            result = agents["report"].generate_statistical_report(request.data, request.time_range)
        
        return AnalysisResponse(
            success=result["success"],
            result=result["report_content"],
            confidence=0.93 if result["success"] else 0.0,
            recommendations=["定期生成安全报告", "关注报告中的趋势变化"],
            message="报告生成完成"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 内容解码接口
@router.post("/decode", summary="内容解码", response_model=AnalysisResponse)
async def decode_content(request: AnalysisRequest):
    """解码各类编码内容，适用于所有安全产品"""
    try:
        decode_type = request.parameters.get("decode_type", "auto") if request.parameters else "auto"
        
        if decode_type == "auto":
            result = agents["decoder"].auto_decode(request.data)
        else:
            result = agents["decoder"].decode(request.data, decode_type)
        
        return AnalysisResponse(
            success=result["success"],
            result=result["decoded_result"] if "decoded_result" in result else result,
            confidence=0.98 if result["success"] else 0.0,
            message="内容解码完成"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 场景化应用接口
class ScenarioRequest(BaseModel):
    scenario_name: str
    data: Any
    parameters: Optional[Dict[str, Any]] = None

@router.post("/scenario/execute", summary="执行场景化应用", response_model=AnalysisResponse)
async def execute_scenario(request: ScenarioRequest):
    """执行指定的场景化应用"""
    try:
        from scenarios.scenario_manager import ScenarioManager
        
        manager = ScenarioManager()
        result = manager.execute_scenario(
            request.scenario_name,
            request.data,
            **request.parameters
        )
        
        return AnalysisResponse(
            success=result["success"],
            result=result["analysis"] if "analysis" in result else result,
            confidence=0.9 if result["success"] else 0.0,
            message="场景执行完成" if result["success"] else f"场景执行失败: {result.get('error', '未知错误')}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scenario/list", summary="列出可用场景", response_model=Dict[str, Any])
async def list_scenarios():
    """列出所有可用的场景化应用"""
    try:
        from scenarios.scenario_manager import ScenarioManager
        
        manager = ScenarioManager()
        scenarios = manager.list_scenarios()
        scenario_descriptions = {
            scenario: manager.get_scenario_description(scenario)
            for scenario in scenarios
        }
        
        return {
            "success": True,
            "scenarios": scenario_descriptions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 健康检查端点
@router.get("/health", summary="健康检查", response_model=Dict[str, Any])
async def health_check():
    return {
        "status": "healthy",
        "service": "AI安全赋能平台",
        "version": "2.0.0",
        "timestamp": "2025-12-10T22:30:00Z"
    }
