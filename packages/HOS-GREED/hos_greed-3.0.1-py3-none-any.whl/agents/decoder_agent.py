from typing import Dict, Any, Optional
from core.deepseek_api import deepseek_api
from core.utils import decode_content
import logging

# 配置日志
logger = logging.getLogger(__name__)

class DecoderAgent:
    def __init__(self):
        self.system_prompt = """你是一位专业的解码专家，负责对各种编码或混淆的内容进行解码和解析。
请根据提供的内容和指定的解码类型，执行解码操作，并输出解码结果和相关分析。

支持的解码类型包括：
- 二进制转ASCII/GBK/UTF8字符
- HTTP请求报文协议解析
- GZip解压缩
- Deflate解压缩
- Base64解码
- URL解码
- 十六进制解码
- 十进制解码
- XML解码
- 字符串转义解码
- Char反混淆

输出格式要求：
1. 原始内容：显示输入的原始内容（截断显示）
2. 解码类型：使用的解码方法
3. 解码结果：显示解码后的内容
4. 解码状态：成功或失败
5. 内容分析：对解码结果的分析和解读

请确保你的解码准确，并提供有价值的分析结果。"""
    
    def decode(self, content: str, decode_type: str) -> Dict[str, Any]:
        """对内容进行解码"""
        try:
            # 首先尝试使用内置工具函数解码
            decoded_result = decode_content(content, decode_type)
            
            # 然后使用AI进行进一步分析
            prompt = f"""请分析以下解码结果：
原始内容：{content[:100]}..." if len(content) > 100 else content
解码类型：{decode_type}
解码结果：{decoded_result}

请提供：
1. 内容类型识别
2. 关键信息提取
3. 安全相关分析（如果有）
4. 进一步处理建议"""
            
            analysis = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "original_content": content[:100] + "..." if len(content) > 100 else content,
                "decode_type": decode_type,
                "decoded_result": decoded_result,
                "analysis": analysis
            }
        except Exception as e:
            logger.error(f"Decoding error: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_content": content[:100] + "..." if len(content) > 100 else content,
                "decode_type": decode_type
            }
    
    def auto_decode(self, content: str) -> Dict[str, Any]:
        """自动识别编码类型并解码"""
        try:
            # 构建提示词
            prompt = f"""请自动识别以下内容的编码类型并进行解码：
内容：{content}

请输出：
1. 识别的编码类型
2. 解码结果
3. 识别依据
4. 内容分析"""
            
            # 调用DeepSeek API
            response = deepseek_api.generate_text(prompt, system_prompt=self.system_prompt)
            
            return {
                "success": True,
                "auto_decode_result": response,
                "original_content": content[:100] + "..." if len(content) > 100 else content
            }
        except Exception as e:
            logger.error(f"Auto decoding error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def batch_decode(self, items: list[dict]) -> Dict[str, Any]:
        """批量解码多个内容"""
        try:
            results = []
            for item in items:
                content = item.get("content", "")
                decode_type = item.get("type", "auto")
                
                if decode_type == "auto":
                    result = self.auto_decode(content)
                else:
                    result = self.decode(content, decode_type)
                
                results.append({
                    "original_item": item,
                    "decode_result": result
                })
            
            return {
                "success": True,
                "batch_results": results,
                "total_items": len(items)
            }
        except Exception as e:
            logger.error(f"Batch decoding error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
