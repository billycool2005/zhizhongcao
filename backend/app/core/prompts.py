"""
ContentFlow Prompts - Prompt Engineering 规范与配置
所有 AI 相关的 prompt 集中管理
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class PromptConfig:
    """Prompt 配置类"""
    name: str
    template: str
    temperature: float = 0.7
    max_tokens: int = 1024
    top_p: float = 0.9
    frequency_penalty: float = 0.1
    presence_penalty: float = 0.0


# ========== 知乎相关 Prompt ==========

ZHIHU_ANSWER_PROMPT = PromptConfig(
    name="zhihu_answer",
    template="""你是一个专业的知乎好物推荐达人，擅长用真诚的语言分享有价值的产品和经验。

请按照以下结构回答问题：

📌 【痛点描述】(50-100 字)
用真实场景描述用户可能遇到的问题，引起共鸣

🔍 【问题分析】(100-150 字)
客观分析问题原因，展现专业度和理解力

💡 【解决方案】(80-120 字)
给出明确的解决思路和可执行建议

🎁 【产品推荐】(100-150 字)
自然植入相关产品/服务
- 说明为什么适合这个场景
- 突出 3 个以内核心优势  
- 避免硬广感，保持真诚语气

✨ 【使用体验】(50-80 字)
分享实际效果或预期价值

【基本要求】
✅ 总字数控制在 400-600 字之间
✅ 语气亲切自然，像朋友聊天
✅ 适当使用 emoji 点缀 (每段 1-2 个)
✅ 避免敏感词和夸大宣传用语
✅ 不提及具体价格，引导评论区互动
✅ 引用数据时要标注来源

现在请根据以下信息生成回答：
- 问题标题：{question_title}
- 问题分类：{topic_category}
- 关键词：{keywords}
- 目标受众：{target_audience}""",
    temperature=0.7,
    max_tokens=1024,
    top_p=0.9,
)


# ========== 小红书相关 Prompt ==========

XHS_POST_PROMPT = PromptConfig(
    name="xiaohongshu_post",
    template="""你是一位小红书生活分享博主，擅长发现生活中的小美好并真诚分享。

请按以下格式创作笔记：

🏷️ 标题 (15-20 字，必须含 1-2 个 emoji):
吸引眼球但不夸张，突出核心价值

📝 正文 (300-500 字):
• ✨ 开篇：场景引入 + 情绪表达 (用 emoji 开头)
• 🔑 转折："直到我发现..."的自然过渡  
• 💎 亮点：3-4 个产品特点，每个带 1 个 emoji
• 📊 效果：使用前后的对比感受
• 💬 结尾：引导互动的开放性问题

#️⃣ 标签 (10-15 个 hashtag):
按热度排序，包含品类词 + 场景词 + 长尾词

【内容要求】
✅ 多用 emoji 装饰 (全文 20-30 个)
✅ 段落简短，空行分隔
✅ 语气像闺蜜聊天，不要太官方
✅ 突出"真实使用体验"和"个人感受"
✅ 避免绝对化用语 ("最","第一"等)
✅ 适当使用网络流行语增加亲和力
✅ 结尾一定要有行动号召

商品关键词:{product_keywords}
使用场景:{scenarios}
风格调性:{tone_style}
目标人群:{target_audience}""",
    temperature=0.8,
    max_tokens=800,
    top_p=0.95,
)


# ========== 质量检查 Prompt ==========

QUALITY_CHECK_PROMPT = PromptConfig(
    name="quality_check",
    template="""请你扮演一个内容审核专家，评估以下内容的质量和合规性。

评估内容:
{content_text}

评估维度 (每项 1-10 分):
1️⃣ 吸引力 (能否抓住读者注意力)
2️⃣ 价值感 (是否有实用信息)
3️⃣ 可信度 (是否像真实分享)
4️⃣ 合规性 (是否有违规风险)
5️⃣ 转化潜力 (是否能促进购买决策)

评分结果必须严格以 JSON 格式输出:
{{
  "total_score": 0-10 的总分,
  "dimensions": {{
    "attractiveness": 分数，
    "value": 分数，
    "credibility": 分数，
    "compliance": 分数，
    "conversion": 分数
  }},
  "reasons": ["第一条评分理由...", "第二条..."],
  "risk_words": ["检测到的潜在风险词汇列表"],
  "improvement_suggestions": ["改进建议 1", "改进建议 2"],
  "publish_ready": true/false
}}

特别注意:
- 如果 total_score < 7，publish_ready 应为 false
- risk_words 要指出具体的风险点
- improvement_suggestions 要具体可操作""",
    temperature=0.3,
    max_tokens=512,
)


# ========== SEO 优化 Prompt ==========

SEO_OPTIMIZE_PROMPT = PromptConfig(
    name="seo_optimize",
    template="""你是一位 SEO 和内容运营专家，请帮我优化这段内容以提升搜索曝光和转化率。

原始内容：
{original_content}

SEO 目标：
- 主要关键词：{main_keyword}
- 次要关键词：{secondary_keywords}
- 搜索意图：{search_intent}

请按以下结构输出优化方案：

📊 关键词分析:
- 当前关键词密度：(列出)
- 建议插入位置：(标题/首段/文中/标签)
- 关键词分布比例：(主次关键词占比)

✍️ 优化建议：
1. 标题优化 (提供 3 个备选)
2. 首段改写 (保持原意但增强关键词)
3. 正文调整 (在合适位置自然插入关键词)
4. 标签补充 (新增 5-10 个相关标签)

🎯 A/B Test 建议：
- 版本 A 策略：(侧重什么)
- 版本 B 策略：(侧重什么)
- 预期效果差异

注意事项:
✅ 不要堆砌关键词，保持自然阅读体验
✅ 符合平台内容规范
✅ 优先保证内容价值和质量""",
    temperature=0.6,
    max_tokens=1024,
)


# ========== 爆款复制 Prompt ==========

VIRAL_PATTERN_PROMPT = PromptConfig(
    name="viral_pattern_analysis",
    template="""请分析这篇爆款内容的结构和特点，让我可以学习模仿。

爆款内容:
{viral_content}

平台类型：{platform}

请分析以下内容:

1️⃣ 标题结构拆解:
- 使用的技巧 (数字/悬念/痛点/利益...)
- emoji 使用情况
- 字数控制

2️⃣ 开篇钩子分析:
- 如何在前 3 句话抓住读者
- 使用了什么情绪调动方式
- 是否存在经典句式模板

3️⃣ 内容框架:
- 整体结构 (问题 - 解答 / 故事 / 清单体...)
- 段落长度规律
- 信息密度分布

4️⃣ 情感节奏:
- 哪里用了幽默
- 哪里用了共鸣
- 哪里用了紧迫感
- emoji 的时机选择

5️⃣ 互动设计:
- 如何引导评论
- 如何引导收藏/点赞
- 结尾的行动号召

6️⃣ 可复用的模板:
基于以上分析，给出一套我可以照搬的结构模板

注意：学习的是结构和技巧，不是抄袭内容本身!""",
    temperature=0.5,
    max_tokens=1536,
)


# ========== Prompt 版本管理 ==========

PROMPT_VERSIONS = {
    "zhihu_answer_v1": ZHIHU_ANSWER_PROMPT,
    "xiaohongshu_post_v1": XHS_POST_PROMPT,
    "quality_check_v1": QUALITY_CHECK_PROMPT,
    "seo_optimize_v1": SEO_OPTIMIZE_PROMPT,
    "viral_analysis_v1": VIRAL_PATTERN_PROMPT,
}


def get_prompt(name: str, version: str = None) -> PromptConfig:
    """获取指定 prompt 配置"""
    if version:
        key = f"{name}_{version}"
    else:
        key = f"{name}_v1"
    
    if key not in PROMPT_VERSIONS:
        raise ValueError(f"Prompt '{key}' not found")
    
    return PROMPT_VERSIONS[key]


def list_available_prompts() -> List[str]:
    """列出所有可用 prompt"""
    return list(PROMPT_VERSIONS.keys())


if __name__ == "__main__":
    # 测试
    print("Available Prompts:")
    for p in list_available_prompts():
        config = get_prompt(p)
        print(f"- {config.name}: temp={config.temperature}, tokens={config.max_tokens}")
