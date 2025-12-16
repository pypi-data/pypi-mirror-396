from fastapi import APIRouter, Depends
from typing import Dict, Any
from .metrics_collector import metrics_collector

router = APIRouter()

@router.get("/metrics", summary="获取所有监控指标")
async def get_metrics() -> Dict[str, Any]:
    """获取系统和服务的所有监控指标"""
    return metrics_collector.collect_all_metrics()

@router.get("/metrics/system", summary="获取系统指标")
async def get_system_metrics() -> Dict[str, Any]:
    """获取系统级监控指标，包括CPU、内存、磁盘、网络等"""
    return metrics_collector.collect_system_metrics()

@router.get("/metrics/service", summary="获取服务指标")
async def get_service_metrics() -> Dict[str, Any]:
    """获取服务级监控指标，包括请求数、响应时间、成功率等"""
    return metrics_collector.collect_service_metrics()

@router.get("/metrics/reset", summary="重置服务指标")
async def reset_service_metrics() -> Dict[str, str]:
    """重置服务级监控指标"""
    metrics_collector.reset_metrics()
    return {
        "message": "服务指标已重置",
        "timestamp": metrics_collector.collect_service_metrics()["timestamp"]
    }
