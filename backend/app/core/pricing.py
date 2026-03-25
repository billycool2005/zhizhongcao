"""
Pricing Configuration - 智种草定价配置
更新时间：2026-03-26 00:09
版本：v1.1
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass(frozen=True)
class PricingConfig:
    """价格配置"""
    # Qwen API 价格 (人民币)
    INPUT_PRICE_PER_MILLION: Decimal = Decimal("0.8")  # 输入：¥0.8/百万 tokens
    OUTPUT_PRICE_PER_MILLION: Decimal = Decimal("1.2")  # 输出：¥1.2/百万 tokens
    
    # 换算为每 token 的成本
    INPUT_PRICE_PER_TOKEN: Decimal = Decimal("0.8") / Decimal("1_000_000")
    OUTPUT_PRICE_PER_TOKEN: Decimal = Decimal("1.2") / Decimal("1_000_000")
    
    # 安全阈值 (人民币/天)
    DAILY_WARNING_THRESHOLD: Decimal = Decimal("100.00")  # ￥100
    DAILY_CRITICAL_THRESHOLD: Decimal = Decimal("300.00")  # ￥300
    DANGER_THRESHOLD: Decimal = Decimal("500.00")  # ￥500
    
    # 用户套餐配额和价格 (人民币/月)
    USER_PLANS = {
        "free": {
            "daily_limit": 500,      # Tokens/天
            "monthly_limit": 10000,  # Tokens/月
            "price": 0.0,             # 免费
        },
        "pro": {
            "daily_limit": 5000,     # Tokens/天
            "monthly_limit": 100000,  # Tokens/月
            "price": Decimal("299.00"), # ¥299/月
        },
        "enterprise": {
            "daily_limit": 50000,    # Tokens/天
            "monthly_limit": 1000000, # Tokens/月
            "price": Decimal("999.00"), # ¥999/月
        }
    }
    
    def calculate_cost(self, tokens_input: int, tokens_output: int) -> Decimal:
        """
        计算 Token 使用成本
        
        Args:
            tokens_input: 输入 token 数量
            tokens_output: 输出 token 数量
            
        Returns:
            总成本 (人民币)
        """
        input_cost = Decimal(tokens_input) * self.INPUT_PRICE_PER_TOKEN
        output_cost = Decimal(tokens_output) * self.OUTPUT_PRICE_PER_TOKEN
        
        total = (input_cost + output_cost).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        
        return total
    
    def get_plan_price(self, plan: str) -> Decimal:
        """获取套餐价格"""
        return self.USER_PLANS[plan]["price"]
    
    def get_daily_limit(self, plan: str) -> int:
        """获取每日配额"""
        return self.USER_PLANS[plan]["daily_limit"]
    
    def get_monthly_limit(self, plan: str) -> int:
        """获取每月配额"""
        return self.USER_PLANS[plan]["monthly_limit"]
    
    def check_alert_level(self, daily_cost: float) -> str:
        """检查告警级别"""
        cost_decimal = Decimal(str(daily_cost))
        
        if cost_decimal >= self.DANGER_THRESHOLD:
            return "danger"  # 危险
        elif cost_decimal >= self.DAILY_CRITICAL_THRESHOLD:
            return "critical"  # 紧急
        elif cost_decimal >= self.DAILY_WARNING_THRESHOLD:
            return "warning"  # 警告
        else:
            return "normal"  # 正常


# 全局配置实例
PRICING = PricingConfig()


if __name__ == "__main__":
    # 测试示例
    print("=" * 60)
    print("智种草 Token 定价配置 v1.1")
    print("=" * 60)
    
    # 测试不同规模的消耗
    test_cases = [
        (1000, 1500),           # 一篇回答的消耗
        (50000, 75000),         # Pro 版日限额
        (500000, 750000),       # Enterprise 版日限额
    ]
    
    for inp, out in test_cases:
        cost = PRICING.calculate_cost(inp, out)
        print(f"\n输入：{inp:,} tokens | 输出：{out:,} tokens")
        print(f"成本：￥{cost:.4f}")
    
    print("\n" + "=" * 60)
    print("安全阈值:")
    print(f"  警告阈值：￥{float(PRICING.DAILY_WARNING_THRESHOLD):.2f}/天")
    print(f"  紧急阈值：￥{float(PRICING.DAILY_CRITICAL_THRESHOLD):.2f}/天")
    print(f"  危险阈值：￥{float(PRICING.DANGER_THRESHOLD):.2f}/天")
    print("=" * 60)
