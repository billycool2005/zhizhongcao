"""
Token Tracking API - Token 追踪接口
自动统计真实 Token 消耗，无需人工查询平台
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from datetime import datetime

router = APIRouter(prefix="/token-track", tags=["Token 追踪"])


@router.get("/realtime")
async def get_realtime_stats():
    """获取实时统计数据 (来自本地自动追踪)"""
    
    try:
        from app.services.token_tracker import tracker
        
        stats = tracker.export_dashboard_json()
        
        return {
            "success": True,
            "data": stats,
            "source": "local_auto_tracking"
        }
        
    except Exception as e:
        # 如果服务还没启动，返回空数据
        return {
            "success": False,
            "data": {
                "timestamp": datetime.utcnow().isoformat(),
                "alert_level": "normal",
                "today": {"tokens": 0, "cost": 0.0, "percentage": 0},
                "message": "Token 追踪服务未初始化"
            }
        }


@router.get("/history")
async def get_history(
    days: int = 7,
    user_id: int = None
):
    """获取历史记录"""
    
    try:
        from app.services.token_tracker import tracker
        
        # TODO: 实现历史查询逻辑
        return {
            "success": True,
            "message": "历史记录功能待完善"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/sync")
async def sync_platform_data():
    """手动同步平台数据 (可选)"""
    
    try:
        from app.services.token_tracker import tracker
        
        # TODO: 对接大模型平台 API
        tracker.sync_with_platform_api()
        
        return {
            "success": True,
            "message": "数据同步成功"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/export/json")
async def export_stats():
    """导出完整统计数据"""
    
    try:
        from app.services.token_tracker import tracker
        
        return {
            "success": True,
            "stats": tracker.current_stats
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# 测试端点
@router.get("/test/record")
async def test_record_token(
    input_tokens: int = 1000,
    output_tokens: int = 1500
):
    """测试记录 Token 使用"""
    
    try:
        from app.services.token_tracker import tracker
        
        record = tracker.record_token_usage(
            model_name="qwen-turbo",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            user_id=999,
            content_type="test"
        )
        
        return {
            "success": True,
            "record": {
                "id": record.id,
                "tokens": f"{input_tokens}+{output_tokens}",
                "cost": record.total_cost_rmb
            }
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
