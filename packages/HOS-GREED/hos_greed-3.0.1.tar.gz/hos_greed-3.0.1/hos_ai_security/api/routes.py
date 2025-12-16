from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from ..agents import (
    EventAgent,
    LogParserAgent,
    DecoderAgent,
    ReportAgent,
    TrafficAgent,
    IntelAgent,
    SecurityQAAgent
)

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

# 请求模型定义
class EventAnalysisRequest(BaseModel):
    event_data: Dict[str, Any]

class NoiseReductionRequest(BaseModel):
    alert_data: Dict[str, Any]
    manual_adjustment: float = 0.0

class LogParseRequest(BaseModel):
    log_content: str
    log_type: Optional[str] = None

class LogExtractRequest(BaseModel):
    log_content: str
    fields: List[str]

class DecodeRequest(BaseModel):
    content: str
    decode_type: str

class AutoDecodeRequest(BaseModel):
    content: str

class BatchDecodeRequest(BaseModel):
    items: List[Dict[str, str]]



class EventReportRequest(BaseModel):
    event_data: Dict[str, Any]

class StatisticalReportRequest(BaseModel):
    events: List[Dict[str, Any]]
    time_range: str

class PCAPAnalysisRequest(BaseModel):
    pcap_info: Dict[str, Any]

class AttackDetectionRequest(BaseModel):
    traffic_data: Dict[str, Any]

class IPIntelRequest(BaseModel):
    ip_address: str

class DomainIntelRequest(BaseModel):
    domain: str

class AttackGroupIntelRequest(BaseModel):
    group_name: str

class VulnerabilityIntelRequest(BaseModel):
    vuln_id: str

class SecurityQuestionRequest(BaseModel):
    question: str

class SecurityConceptRequest(BaseModel):
    concept: str
    depth: str = "medium"

class SecurityBestPracticesRequest(BaseModel):
    topic: str

# 事件运营智能体 API
@router.post("/event/analyze", summary="分析安全事件")
async def analyze_event(request: EventAnalysisRequest):
    result = agents["event"].analyze_event(request.event_data)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "分析失败"))
    return result

@router.post("/event/reduce_noise", summary="告警降噪研判")
async def reduce_noise(request: NoiseReductionRequest):
    result = agents["event"].reduce_noise(request.alert_data, request.manual_adjustment)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "降噪失败"))
    return result

# 日志解析智能体 API
@router.post("/log/parse", summary="解析日志内容")
async def parse_log(request: LogParseRequest):
    result = agents["log_parser"].parse_log(request.log_content, request.log_type)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "解析失败"))
    return result

@router.post("/log/extract", summary="从日志中提取指定字段")
async def extract_log_fields(request: LogExtractRequest):
    result = agents["log_parser"].extract_key_info(request.log_content, request.fields)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "提取失败"))
    return result

# 解码智能体 API
@router.post("/decode", summary="对内容进行解码")
async def decode_content(request: DecodeRequest):
    result = agents["decoder"].decode(request.content, request.decode_type)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "解码失败"))
    return result

@router.post("/decode/auto", summary="自动识别编码并解码")
async def auto_decode(request: AutoDecodeRequest):
    result = agents["decoder"].auto_decode(request.content)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "自动解码失败"))
    return result

@router.post("/decode/batch", summary="批量解码多个内容")
async def batch_decode(request: BatchDecodeRequest):
    result = agents["decoder"].batch_decode(request.items)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "批量解码失败"))
    return result



# 报告生成智能体 API
@router.post("/report/event", summary="生成单一事件报告")
async def generate_event_report(request: EventReportRequest):
    result = agents["report"].generate_event_report(request.event_data)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "报告生成失败"))
    return result

@router.post("/report/statistical", summary="生成统计报告")
async def generate_statistical_report(request: StatisticalReportRequest):
    result = agents["report"].generate_statistical_report(request.events, request.time_range)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "统计报告生成失败"))
    return result

# 流量检测智能体 API
@router.post("/traffic/analyze_pcap", summary="分析PCAP包")
async def analyze_pcap(request: PCAPAnalysisRequest):
    result = agents["traffic"].analyze_pcap(request.pcap_info)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "PCAP分析失败"))
    return result

@router.post("/traffic/detect_attacks", summary="检测流量攻击")
async def detect_attacks(request: AttackDetectionRequest):
    result = agents["traffic"].detect_attacks(request.traffic_data)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "攻击检测失败"))
    return result

# 情报检索智能体 API
@router.post("/intel/ip", summary="检索IP情报")
async def search_ip_intel(request: IPIntelRequest):
    result = agents["intel"].search_ip(request.ip_address)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "IP情报检索失败"))
    return result

@router.post("/intel/domain", summary="检索域名情报")
async def search_domain_intel(request: DomainIntelRequest):
    result = agents["intel"].search_domain(request.domain)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "域名情报检索失败"))
    return result

@router.post("/intel/attack_group", summary="检索攻击组织情报")
async def search_attack_group_intel(request: AttackGroupIntelRequest):
    result = agents["intel"].search_attack_group(request.group_name)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "攻击组织情报检索失败"))
    return result

@router.post("/intel/vulnerability", summary="检索漏洞情报")
async def search_vulnerability_intel(request: VulnerabilityIntelRequest):
    result = agents["intel"].search_vulnerability(request.vuln_id)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "漏洞情报检索失败"))
    return result

# 安全知识问答智能体 API
@router.post("/security/question", summary="回答安全领域问题")
async def answer_security_question(request: SecurityQuestionRequest):
    result = agents["security_qa"].answer_question(request.question)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "安全问题回答失败"))
    return result

@router.post("/security/explain", summary="解释安全概念")
async def explain_security_concept(request: SecurityConceptRequest):
    result = agents["security_qa"].explain_concept(request.concept, request.depth)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "概念解释失败"))
    return result

@router.post("/security/best_practices", summary="提供安全最佳实践")
async def provide_security_best_practices(request: SecurityBestPracticesRequest):
    result = agents["security_qa"].provide_best_practices(request.topic)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "最佳实践提供失败"))
    return result

# 健康检查端点
@router.get("/health", summary="健康检查")
async def health_check():
    return {
        "status": "healthy",
        "service": "安全智能体系统",
        "version": "1.0.0"
    }
