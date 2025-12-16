from fastapi import APIRouter
from .routes_unified import router as unified_router

# 创建主路由器
router = APIRouter()

# 包含统一API路由
router.include_router(unified_router, prefix="/api/v2", tags=["unified"])

# 包含监控路由
from monitoring.monitoring_api import router as monitoring_router
router.include_router(monitoring_router, prefix="/api/monitoring", tags=["monitoring"])
