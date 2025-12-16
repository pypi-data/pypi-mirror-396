# HOS AI Security Package
__version__ = "3.0.0"
__author__ = "HOS Team"
__email__ = "admin@example.com"
__description__ = "轻量化AI安全赋能平台，适合中小型企业"

# 导出主要组件
from .agents.unified_agent import unified_agent
from .main import app

__all__ = ["unified_agent", "app"]