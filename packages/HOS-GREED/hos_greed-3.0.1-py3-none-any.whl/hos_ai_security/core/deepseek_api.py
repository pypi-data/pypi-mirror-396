import requests
import time
import logging
from typing import Optional, List, Dict, Any
from requests.exceptions import RequestException, Timeout, HTTPError
from config.config import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepSeekAPI:
    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.api_url = settings.deepseek_api_url
        self.model = settings.deepseek_model
        self.max_retries = settings.max_retries
        self.timeout = settings.timeout
        self.retry_delay = settings.retry_delay
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """执行API请求，包含重试机制"""
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except HTTPError as e:
                if response.status_code == 429:
                    logger.warning(f"API rate limited, retrying in {self.retry_delay}s... (Attempt {attempt+1}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                    self.retry_delay *= 2  # 指数退避
                else:
                    logger.error(f"HTTP error occurred: {e} (Attempt {attempt+1}/{self.max_retries})")
                    if attempt == self.max_retries - 1:
                        raise
            except Timeout as e:
                logger.error(f"Request timed out: {e} (Attempt {attempt+1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    raise
            except RequestException as e:
                logger.error(f"Request exception occurred: {e} (Attempt {attempt+1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    raise
        
        raise Exception("All retry attempts failed")
    
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       model: Optional[str] = None,
                       temperature: float = 0.7,
                       max_tokens: int = 2048,
                       top_p: float = 0.95,
                       frequency_penalty: float = 0.0,
                       presence_penalty: float = 0.0,
                       stop: Optional[List[str]] = None) -> str:
        """生成对话补全"""
        payload = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty
        }
        
        if stop:
            payload["stop"] = stop
        
        try:
            response = self._make_request(payload)
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Failed to get chat completion: {e}")
            raise
    
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """生成文本，简化版API"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        # 从kwargs中移除system_prompt，因为chat_completion方法不接受这个参数
        kwargs.pop('system_prompt', None)
        return self.chat_completion(messages, **kwargs)
    
    def create_chat_session(self, system_prompt: Optional[str] = None) -> List[Dict[str, str]]:
        """创建新的对话会话"""
        session = []
        if system_prompt:
            session.append({"role": "system", "content": system_prompt})
        return session
    
    def add_message(self, session: List[Dict[str, str]], role: str, content: str) -> List[Dict[str, str]]:
        """向对话会话添加消息"""
        session.append({"role": role, "content": content})
        return session
    
    def get_session_history(self, session: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """获取会话历史"""
        return session.copy()

# 创建全局API实例
deepseek_api = DeepSeekAPI()
