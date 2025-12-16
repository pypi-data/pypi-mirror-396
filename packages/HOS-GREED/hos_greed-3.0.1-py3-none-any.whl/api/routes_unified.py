from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel
from agents.unified_agent import unified_agent

router = APIRouter()

# 统一请求模型 - 简化设计
class UnifiedRequest(BaseModel):
    task_type: Optional[str] = None  # 可选，自动识别
    data: Any  # 统一数据字段
    product_type: Optional[str] = None  # 可选产品类型，用于产品智能体

# 统一响应模型 - 简化设计
class UnifiedResponse(BaseModel):
    success: bool
    result: Any
    task_type: str
    message: Optional[str] = None

# 单一主接口，处理所有请求 - 轻量化设计核心
@router.post("/ai-security", summary="统一AI安全接口", response_model=UnifiedResponse)
async def ai_security(request: UnifiedRequest):
    """统一AI安全接口，处理所有安全相关请求
    
    支持场景：
    - 安全分析：事件分析、日志解析、流量分析、攻击检测
    - 安全知识：安全问答、情报检索、概念解释
    - 报告生成：各类安全报告生成
    - 产品分析：数据汇总平台、防火墙、WAF、堡垒机、DLP等产品数据
    
    特点：
    - 自动意图识别，无需指定具体任务类型
    - 简化请求格式，降低使用门槛
    - 统一响应格式，便于集成
    - 轻量化设计，适合中小型企业
    """
    try:
        # 处理产品智能体请求
        if request.product_type:
            result = unified_agent.analyze_product(
                request.product_type,
                request.data
            )
            return UnifiedResponse(
                success=True,
                result=result,
                task_type="product_analysis",
                message=f"Successfully analyzed {request.product_type} data"
            )
        
        # 处理普通请求
        result = unified_agent.handle_request(
            request.task_type or "",
            request.data
        )
        return UnifiedResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 健康检查端点
@router.get("/health", summary="健康检查")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "AI安全赋能平台",
        "version": "3.0.0",
        "timestamp": "2025-12-10T23:00:00Z"
    }
