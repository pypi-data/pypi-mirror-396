from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # DeepSeek API 配置
    deepseek_api_key: str = "your-api-key-here"
    deepseek_api_url: str = "https://api.deepseek.com/v1/chat/completions"
    deepseek_model: str = "deepseek-chat"
    
    # API 调用配置
    max_retries: int = 3
    timeout: int = 30
    retry_delay: int = 1
    
    # 降噪评分配置
    noise_reduction_threshold: float = 0.5
    allow_manual_adjustment: bool = True
    
    # 白名单配置
    whitelist_events: List[str] = []
    skip_ai_for_whitelist: bool = True
    
    # 应用配置
    app_name: str = "安全智能体系统"
    app_version: str = "1.0.0"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# 创建全局配置实例
settings = Settings()
