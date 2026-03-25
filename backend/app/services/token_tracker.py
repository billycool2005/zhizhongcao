"""
TokenTrackerService - 自动 Token 消耗追踪服务
实时监控并记录所有 AI API 调用的真实消耗
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class TokenRecord:
    """单次 Token 使用记录"""
    id: str
    timestamp: datetime
    model_name: str
    
    # Token 用量
    input_tokens: int
    output_tokens: int
    total_tokens: int
    
    # 成本计算
    cost_rmb_input: float
    cost_rmb_output: float
    total_cost_rmb: float
    
    # 上下文信息
    content_id: Optional[int] = None
    user_id: Optional[int] = None
    content_type: Optional[str] = None
    platform: Optional[str] = None


class TokenTrackerService:
    """Token 追踪主服务"""
    
    def __init__(self, storage_dir: str = "stats"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # 定价配置 (人民币)
        self.input_price_per_million = 0.8
        self.output_price_per_million = 1.2
        
        # 当前会话的临时记录
        self.session_records: List[TokenRecord] = []
        
        # 历史统计数据
        self.stats_file = self.storage_dir / "token_stats.json"
        self.daily_files = {}
        
        self._load_history()
    
    def _load_history(self):
        """加载历史统计数据"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    self.current_stats = json.load(f)
            except:
                self.current_stats = self._default_stats()
        else:
            self.current_stats = self._default_stats()
    
    def _default_stats(self) -> dict:
        """默认统计结构"""
        return {
            "total_tokens_today": 0,
            "total_cost_today": 0.0,
            "records_today": [],
            "hourly_breakdown": {},
            "last_updated": None
        }
    
    def record_token_usage(
        self, 
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        user_id: int = None,
        content_id: int = None,
        content_type: str = None,
        platform: str = None
    ) -> TokenRecord:
        """记录一次 Token 使用"""
        
        total_tokens = input_tokens + output_tokens
        
        # 计算成本
        cost_input = (input_tokens * self.input_price_per_million) / 1_000_000
        cost_output = (output_tokens * self.output_price_per_million) / 1_000_000
        
        record = TokenRecord(
            id=f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(self.session_records)}",
            timestamp=datetime.utcnow(),
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_rmb_input=round(cost_input, 6),
            cost_rmb_output=round(cost_output, 6),
            total_cost_rmb=round(cost_input + cost_output, 6),
            user_id=user_id,
            content_id=content_id,
            content_type=content_type,
            platform=platform
        )
        
        self.session_records.append(record)
        self._update_daily_stats(record)
        self._save_session_to_file()
        
        return record
    
    def _update_daily_stats(self, record: TokenRecord):
        """更新当日统计"""
        today_str = datetime.utcnow().date().isoformat()
        hour_key = f"{today_str}_{"{:.2f}".format(record.timestamp.hour)}:00"
        
        # 初始化今日数据
        if not self.current_stats.get("today"):
            self.current_stats["today"] = {
                "tokens": 0,
                "cost": 0.0,
                "hourly": {}
            }
        
        # 累加数据
        self.current_stats["today"]["tokens"] += record.total_tokens
        self.current_stats["today"]["cost"] += record.total_cost_rmb
        
        # 小时分解
        if hour_key not in self.current_stats["today"]["hourly"]:
            self.current_stats["today"]["hourly"][hour_key] = {"tokens": 0, "cost": 0.0}
        
        self.current_stats["today"]["hourly"][hour_key]["tokens"] += record.total_tokens
        self.current_stats["today"]["hourly"][hour_key]["cost"] += record.total_cost_rmb
        
        # 更新时间戳
        self.current_stats["today"]["updated_at"] = datetime.utcnow().isoformat()
        self.current_stats["last_updated"] = datetime.utcnow().isoformat()
        
        # 保存
        self._save_stats()
    
    def _save_session_to_file(self):
        """保存会话记录到文件"""
        session_file = self.storage_dir / f"session_{datetime.utcnow().date().isoformat()}.json"
        
        records_data = [asdict(r) for r in self.session_records]
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.utcnow().isoformat(),
                "records": records_data
            }, f, indent=2, ensure_ascii=False)
    
    def _save_stats(self):
        """保存统计数据"""
        self.stats_file.write_text(json.dumps(self.current_stats, indent=2, ensure_ascii=False))
    
    def get_realtime_stats(self) -> dict:
        """获取实时统计数据"""
        
        now = datetime.utcnow()
        today_str = now.date().isoformat()
        
        stats = self.current_stats.copy()
        
        # 添加汇总信息
        stats["summary"] = {
            "total_tokens": stats["today"]["tokens"],
            "total_cost": round(stats["today"]["cost"], 2),
            "record_count": len(stats["today"].get("records", [])),
            "avg_cost_per_record": round(stats["today"]["cost"] / max(len(stats["today"].get("records", [])), 1), 4),
            "tokens_per_hour_avg": round(
                stats["today"]["tokens"] / max(len(stats["today"]["hourly"]), 1), 1
            )
        }
        
        # 计算告警级别
        budget_threshold = 100.0
        used_percentage = (stats["today"]["cost"] / budget_threshold) * 100
        
        stats["alert_level"] = "normal"
        if used_percentage >= 100:
            stats["alert_level"] = "critical"
        elif used_percentage >= 75:
            stats["alert_level"] = "warning"
        elif used_percentage >= 50:
            stats["alert_level"] = "info"
        
        stats["budget_remaining"] = budget_threshold - stats["today"]["cost"]
        stats["usage_percentage"] = round(used_percentage, 2)
        
        return stats
    
    def export_dashboard_json(self) -> dict:
        """导出 Dashboard 专用格式"""
        stats = self.get_realtime_stats()
        
        hourly_list = []
        for hour_key, data in stats["today"]["hourly"].items():
            hourly_list.append({
                "hour": hour_key.split("_")[1],
                "tokens": data["tokens"],
                "cost": round(data["cost"], 2)
            })
        
        return {
            "timestamp": stats["last_updated"],
            "alert_level": stats["alert_level"],
            "alert_message": self._get_alert_message(stats["alert_level"], stats["budget_remaining"]),
            "current_hour": {
                "tokens": hourly_list[-1]["tokens"] if hourly_list else 0,
                "cost": hourly_list[-1]["cost"] if hourly_list else 0.0
            },
            "today": {
                "tokens": stats["summary"]["total_tokens"],
                "cost": stats["summary"]["total_cost"],
                "percentage": stats["usage_percentage"],
                "remaining": round(stats["budget_remaining"], 2)
            },
            "predictions": {
                "daily_total": stats["today"]["cost"],
                "projected_monthly": round(stats["today"]["cost"] * 5, 2) if stats["today"]["cost"] > 0 else 0
            },
            "hourly_trend": hourly_list
        }
    
    def _get_alert_message(self, level: str, remaining: float) -> str:
        """获取告警消息"""
        messages = {
            "normal": "✅ 运行正常，预算充足",
            "info": "💡 今日已花费 ￥{}, 剩余 ￥{}".format(
                round(100 - remaining, 2), 
                round(remaining, 2)
            ),
            "warning": "⚠️ 今日已超预算 75%，请留意消耗",
            "critical": "🚨 今日预算已耗尽！请立即采取措施！",
        }
        
        if level == "normal" and remaining < 100:
            return messages["info"]
        
        return messages.get(level, "未知状态")
    
    def sync_with_platform_api(self, api_endpoint: str = None):
        """与平台 API 同步数据 (可选扩展)"""
        # TODO: 如果有平台 API 可以定时同步
        pass


# 全局实例
tracker = TokenTrackerService()


if __name__ == "__main__":
    # 测试
    t = TokenTrackerService()
    
    # 模拟一些调用
    t.record_token_usage("qwen-turbo", 1000, 1500, user_id=1)
    t.record_token_usage("qwen-plus", 2000, 3000, user_id=1)
    
    print("实时统计数据:")
    print(json.dumps(t.get_realtime_stats(), indent=2, ensure_ascii=False))
    
    print("\nDashboard JSON:")
    print(json.dumps(t.export_dashboard_json(), indent=2, ensure_ascii=False))
