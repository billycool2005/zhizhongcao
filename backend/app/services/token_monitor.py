"""
TokenMonitorService - Token 实时消耗监控系统
实时监控 API 调用、费用估算、异常检测
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Index, func
from sqlalchemy.orm import relationship, declarative_base
from decimal import Decimal

logger = logging.getLogger(__name__)

Base = declarative_base()


@dataclass
class RealtimeStats:
    """实时统计数据"""
    current_hour_tokens: int = 0
    today_tokens: int = 0
    this_month_tokens: int = 0
    
    current_hour_cost: float = 0.0
    today_cost: float = 0.0
    this_month_cost: float = 0.0
    
    user_count_today: int = 0
    request_count_today: int = 0
    
    # 预测
    predicted_daily_cost: float = 0.0
    predicted_monthly_cost: float = 0.0
    
    # 安全阈值
    is_over_budget: bool = False
    alert_level: str = "normal"  # normal, warning, critical


@dataclass
class UserTokenUsage:
    """用户 Token 使用情况"""
    user_id: str
    username: str
    plan: str  # free/pro/enterprise
    
    # 今日使用
    today_tokens: int = 0
    today_limit: int = 500
    today_remaining: int = 500
    today_percentage: float = 0.0
    
    # 本月累计
    month_tokens: int = 0
    month_limit: int = 10000
    month_remaining: int = 10000
    
    # 最近活动
    last_active: Optional[datetime] = None
    
    # 成本
    daily_cost: float = 0.0
    monthly_cost: float = 0.0


# ========== 数据库模型 ==========

class TokenLog(Base):
    """Token 使用日志表"""
    __tablename__ = 'token_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 用户信息
    user_id = Column(Integer, ForeignKey('users.id'))
    plan_type = Column(String(20))  # free/pro/enterprise
    
    # Token 使用情况
    model_name = Column(String(50))  # qwen-turbo/qwen-plus等
    tokens_input = Column(Integer, default=0)
    tokens_output = Column(Integer, default=0)
    tokens_total = Column(Integer, default=0)
    
    # 内容信息
    content_id = Column(Integer)
    content_type = Column(String(20))  # answer/post
    platform = Column(String(20))  # zhihu/xiaohongshu
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 成本计算
    cost_usd = Column(Float, default=0.0)
    
    __table_args__ = (
        Index('idx_token_user_time', 'user_id', 'created_at'),
        Index('idx_token_date', func.date(created_at)),
    )


class DailyBudget(Base):
    """每日预算配置表"""
    __tablename__ = 'daily_budgets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    date = Column(DateTime, default=datetime.utcnow, unique=True)
    budget_limit = Column(Integer, default=5000)  # Token 限额
    actual_usage = Column(Integer, default=0)
    status = Column(String(20), default='active')  # active/blocked
    
    __table_args__ = (
        Index('idx_budget_user_date', 'user_id', 'date'),
    )


class SystemAlert(Base):
    """系统警报表"""
    __tablename__ = 'system_alerts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    alert_type = Column(String(20))  # budget_exceeded, anomaly, rate_limit
    level = Column(String(20))  # info/warning/error/critical
    message = Column(Text)
    
    triggered_by = Column(String(50))  # user_id or system
    related_data = Column(Text)  # JSON string
    
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_alert_created', created_at),
    )


class GlobalDashboardMetrics(Base):
    """全局仪表盘指标"""
    __tablename__ = 'global_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    metric_name = Column(String(50))
    metric_value = Column(Float)
    unit = Column(String(20))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 快照数据
    snapshot_data = Column(Text)  # JSON
    

# ========== 核心服务类 ==========

class TokenMonitorService:
    """Token 监控服务主类"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.token_price_per_1k = {
            'qwen-turbo': {'input': 0.3, 'output': 0.6},  # $/千 token
            'qwen-plus': {'input': 0.8, 'output': 2.0},
            'qwen-max': {'input': 2.0, 'output': 6.0},
        }
        
        # 用户配额设置
        self.user_limits = {
            'free': {'daily': 500, 'monthly': 10000},
            'pro': {'daily': 5000, 'monthly': 100000},
            'enterprise': {'daily': 50000, 'monthly': 1000000},
        }
        
        # 系统级安全阈值
        self.system_thresholds = {
            'cost_warning': 100.0,  # $100/day 警告
            'cost_critical': 300.0,  # $300/day 紧急
            'cost_danger': 500.0,  # $500/day 危险
        }
    
    async def record_token_usage(
        self, 
        user_id: int, 
        model: str,
        tokens_in: int,
        tokens_out: int,
        content_id: int = None,
        content_type: str = None,
        platform: str = None
    ):
        """记录一次 Token 使用"""
        
        total_tokens = tokens_in + tokens_out
        
        # 计算成本
        prices = self.token_price_per_1k.get(model, self.token_price_per_1k['qwen-turbo'])
        cost = (tokens_in * prices['input'] + tokens_out * prices['output']) / 1000
        
        # 保存到数据库
        log = TokenLog(
            user_id=user_id,
            plan_type=self._get_user_plan(user_id),
            model_name=model,
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            tokens_total=total_tokens,
            content_id=content_id,
            content_type=content_type,
            platform=platform,
            cost_usd=cost,
        )
        
        self.db.add(log)
        self.db.commit()
        
        # 检查是否超限
        await self._check_user_quota(user_id, total_tokens)
        
        logger.info(f"User {user_id} used {total_tokens} tokens, cost ${cost:.4f}")
        
        return cost
    
    async def get_realtime_dashboard(self) -> Dict:
        """获取实时仪表盘数据"""
        
        now = datetime.utcnow()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 今日总消耗
        today_logs = self.db.query(TokenLog).filter(
            TokenLog.created_at >= start_of_day
        ).all()
        
        total_tokens_today = sum(log.tokens_total for log in today_logs)
        total_cost_today = sum(log.cost_usd for log in today_logs)
        
        # 当前小时数据
        start_of_hour = now.replace(minute=0, second=0, microsecond=0)
        hourly_logs = self.db.query(TokenLog).filter(
            TokenLog.created_at >= start_of_hour
        ).all()
        
        hourly_tokens = sum(log.tokens_total for log in hourly_logs)
        hourly_cost = sum(log.cost_usd for log in hourly_logs)
        
        # 唯一用户数
        user_ids = set(log.user_id for log in today_logs)
        unique_users = len(user_ids)
        
        # 预测
        hours_elapsed = now.hour + now.minute / 60
        predicted_daily = total_cost_today / max(hours_elapsed, 1) * 24
        predicted_monthly = predicted_daily * 30
        
        # 告警检查
        alert_level = "normal"
        if predicted_daily > self.system_thresholds['cost_danger']:
            alert_level = "critical"
        elif predicted_daily > self.system_thresholds['cost_critical']:
            alert_level = "warning"
        elif predicted_daily > self.system_thresholds['cost_warning']:
            alert_level = "info"
        
        dashboard = {
            "timestamp": now.isoformat(),
            "current_hour": {
                "tokens": hourly_tokens,
                "cost_usd": round(hourly_cost, 4),
            },
            "today": {
                "tokens": total_tokens_today,
                "cost_usd": round(total_cost_today, 4),
                "unique_users": unique_users,
                "requests": len(today_logs),
            },
            "predictions": {
                "daily_cost_usd": round(predicted_daily, 2),
                "monthly_cost_usd": round(predicted_monthly, 2),
            },
            "alerts": {
                "level": alert_level,
                "message": self._get_alert_message(alert_level, predicted_daily),
            },
            "limits": self.system_thresholds,
        }
        
        return dashboard
    
    async def get_user_token_status(self, user_id: int) -> UserTokenUsage:
        """获取用户 Token 使用情况"""
        
        plan = self._get_user_plan(user_id)
        limit = self.user_limits[plan]
        
        now = datetime.utcnow()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 今日使用
        today_logs = self.db.query(TokenLog).filter(
            TokenLog.user_id == user_id,
            TokenLog.created_at >= start_of_day
        ).all()
        
        today_tokens = sum(log.tokens_total for log in today_logs)
        remaining = max(0, limit['daily'] - today_tokens)
        percentage = min(100, (today_tokens / limit['daily']) * 100)
        
        # 本月累计
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_logs = self.db.query(TokenLog).filter(
            TokenLog.user_id == user_id,
            TokenLog.created_at >= start_of_month
        ).all()
        
        month_tokens = sum(log.tokens_total for log in month_logs)
        month_remaining = max(0, limit['monthly'] - month_tokens)
        
        # 计算成本
        daily_cost = sum(log.cost_usd for log in today_logs)
        monthly_cost = sum(log.cost_usd for log in month_logs)
        
        return UserTokenUsage(
            user_id=str(user_id),
            username=f"user_{user_id}",
            plan=plan,
            today_tokens=today_tokens,
            today_limit=limit['daily'],
            today_remaining=remaining,
            today_percentage=percentage,
            month_tokens=month_tokens,
            month_limit=limit['monthly'],
            month_remaining=month_remaining,
            last_active=now,
            daily_cost=daily_cost,
            monthly_cost=monthly_cost,
        )
    
    async def _check_user_quota(self, user_id: int, tokens_used: int):
        """检查用户是否超配额"""
        
        usage = await self.get_user_token_status(user_id)
        
        if usage.today_remaining <= 0:
            logger.warning(f"User {user_id} exceeded daily quota!")
            # TODO: 发送通知，限制访问
            
        if usage.month_remaining <= 0:
            logger.warning(f"User {user_id} exceeded monthly quota!")
            # TODO: 发送通知，强制降级或关闭
            
    async def get_anomaly_detection(self) -> List[Dict]:
        """异常检测"""
        
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        
        # 获取过去一小时的数据
        recent_logs = self.db.query(TokenLog).filter(
            TokenLog.created_at >= one_hour_ago
        ).all()
        
        anomalies = []
        
        # 检测突增
        avg_tokens = sum(log.tokens_total for log in recent_logs) / max(len(recent_logs), 1)
        
        for log in recent_logs:
            if log.tokens_total > avg_tokens * 3:  # 超过平均值 3 倍
                anomalies.append({
                    "type": "spike",
                    "user_id": log.user_id,
                    "tokens": log.tokens_total,
                    "avg": avg_tokens,
                    "reason": "Abnormally high token consumption",
                })
        
        return anomalies
    
    def _get_user_plan(self, user_id: int) -> str:
        """获取用户套餐类型"""
        # 这里应该从数据库查询，简化处理
        return "pro"
    
    def _get_alert_message(self, level: str, predicted_cost: float) -> str:
        """获取告警消息"""
        messages = {
            "normal": "All systems operating within normal parameters",
            "info": f"Daily spending projected at ${predicted_cost:.2f}. Monitor closely.",
            "warning": f"WARNING: Projected daily spend ${predicted_cost:.2f} exceeds threshold of ${self.system_thresholds['cost_warning']}",
            "critical": f"CRITICAL: Projected daily spend ${predicted_cost:.2f} dangerously high!",
        }
        return messages.get(level, "Unknown")


if __name__ == "__main__":
    # 测试代码
    import json
    
    class MockDB:
        def query(self, model):
            return self
        def filter(self, *args):
            return self
        def all(self):
            return []
        def add(self, obj):
            pass
        def commit(self):
            pass
    
    service = TokenMonitorService(MockDB())
    
    async def test():
        dashboard = await service.get_realtime_dashboard()
        print(json.dumps(dashboard, indent=2, ensure_ascii=False))
    
    asyncio.run(test())
