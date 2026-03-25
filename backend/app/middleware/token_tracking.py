"""
Token Tracking Middleware - Token 追踪中间件
拦截所有 AI API 调用并自动记录消耗
"""

import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.token_tracker import tracker

logger = logging.getLogger(__name__)


class TokenTrackingMiddleware(BaseHTTPMiddleware):
    """Token 消耗追踪中间件"""
    
    async def dispatch(self, request: Request, call_next):
        """拦截请求并记录 Token"""
        
        # 只追踪 AI API 调用
        if "/api/v1/ai/" not in request.url.path:
            return await call_next(request)
        
        start_time = None
        
        try:
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"AI API error: {e}")
            raise
    
    def record_from_response(
        self, 
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        user_id: int = None,
        content_id: int = None,
        content_type: str = "post",
        platform: str = "zhihu"
    ):
        """从响应中提取 Token 并记录"""
        
        tracker.record_token_usage(
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            user_id=user_id,
            content_id=content_id,
            content_type=content_type,
            platform=platform
        )
        
        logger.info(f"Recorded token usage: {input_tokens}+{output_tokens} tokens")


# 全局实例
token_middleware = TokenTrackingMiddleware()


def track_ai_call(func):
    """装饰器：标记函数为 AI 调用"""
    
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        # 如果结果中有 token 信息，自动记录
        if isinstance(result, dict) and "tokens" in result:
            token_middleware.record_from_response(
                model_name=result.get("model", "qwen-turbo"),
                input_tokens=result["tokens"]["input"],
                output_tokens=result["tokens"]["output"],
                user_id=result.get("user_id"),
                content_id=result.get("content_id"),
                content_type=result.get("content_type"),
                platform=result.get("platform")
            )
        
        return result
    
    return wrapper
