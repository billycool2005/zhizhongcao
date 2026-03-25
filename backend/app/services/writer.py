"""
ContentFlow Writer Service - AI 内容创作引擎
按固定模板自动生成高质量种草文
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GeneratedContent:
    """生成的内容结构"""
    id: str
    title: str
    content: str
    hashtags: List[str]
    structure: Dict[str, Any]
    platform: str
    quality_score: float
    
    @property
    def is_publish_ready(self) -> bool:
        return self.quality_score >= 0.7


class PromptEngineer:
    """Prompt 工程模块"""
    
    # 知乎回答模板
    ZHIHU_ANSWER_PROMPT = """
你是一个专业的知乎好物推荐达人。请按照以下结构回答问题：

【痛点描述】(50-100 字)
详细描述用户可能遇到的具体问题，引起共鸣

【问题分析】(100-150 字)
分析问题产生的原因，展现专业度

【解决方案】(80-120 字)
给出明确的解决思路和结论

【产品推荐】(100-150 字)
顺势推荐相关产品/服务，自然植入
- 说明为什么适合这个问题场景
- 突出核心优势 (不超过 3 个)
- 避免硬广感，保持真诚推荐语气

【使用体验】(50-80 字)
分享实际使用效果或预期效果

要求:
1. 总字数控制在 400-600 字之间
2. 语气真诚自然，不要太营销感
3. 适当使用表情符号增加亲和力 😊
4. 避免敏感词和夸大宣传用语
5. 不要提及具体价格，留到评论区互动

上下文信息:
- 问题标题：{question_title}
- 问题分类：{topic}
- 推荐产品关键词：{keywords}
- 目标受众：{target_audience}
"""

    # 小红书笔记模板
    XHS_POST_PROMPT = """
你是一个小红书家居/美妆/母婴种草博主。请按以下格式发布笔记:

📝 标题 (必须包含 emoji，不超过 20 字):
用吸引眼球但不夸张的方式表达核心价值

✨ 正文结构:
• 第一段：场景引入 + 痛点共鸣 (用 emoji 开头)
• 第二段：我的发现过程 (真实感)
• 第三段：产品特点介绍 (3-4 个亮点)
• 第四段：使用前后对比 (如果有)
• 第五段：总结推荐 + 行动号召

#️⃣ 标签 (底部，10-15 个):
#话题 1 #话题 2 #话题 3...

要求:
1. 全文多用 emoji 点缀 🌟💡✅
2. 每段不要太长，空行分隔
3. 语气像朋友聊天，不要太官方
4. 突出"真实使用体验"
5. 结尾引导互动："评论区告诉我你的想法~"

商品关键词:{product_keywords}
场景标签:{scene_tags}
风格定位:{tone_style}
"""

    # 通用质量评分 Prompt
    QUALITY_CHECK_PROMPT = """
请评估以下内容的质量 (1-10 分):

内容类型:{content_type}
平台:{platform}
内容文本:{content_text}

评分维度:
1. 吸引力 (是否让人想继续读)
2. 价值感 (是否有实用信息)
3. 可信度 (是否像真实分享)
4. 合规性 (是否有违规风险)
5. 转化潜力 (是否能促进购买决策)

输出 JSON:
{{
  "score": 0-10 的数字，
  "reasons": ["第一条评分理由", "第二条...", ...],
  "suggestions": ["改进建议 1", "改进建议 2"],
  "risk_words": ["检测到的高风险词汇列表"]
}}
"""

    def get_zhihu_prompt(self, context: Dict) -> str:
        """生成知乎回答 Prompt"""
        return self.ZHIHU_ANSWER_PROMPT.format(
            question_title=context.get("title", ""),
            topic=context.get("tags", [])[0] if context.get("tags") else "",
            keywords=",".join(context.get("keywords", [])),
            target_audience=context.get("audience", "年轻人"),
        )
    
    def get_xhs_prompt(self, context: Dict) -> str:
        """生成小红书笔记 Prompt"""
        return self.XHS_POST_PROMPT.format(
            product_keywords=",".join(context.get("keywords", [])),
            scene_tags=",".join(context.get("scenes", [])),
            tone_style=context.get("style", "温馨生活风"),
        )
    
    def get_quality_check_prompt(self, content: str, content_type: str, platform: str) -> str:
        """生成质量检查 Prompt"""
        return self.QUALITY_CHECK_PROMPT.format(
            content_type=content_type,
            platform=platform,
            content_text=content[:2000],  # 限制长度
        )


class ContentGenerator:
    """AI 内容生成器"""
    
    def __init__(self, model_provider: str = "qwen"):
        """
        Args:
            model_provider: "qwen"(通义千问), "openai", "anthropic" 等
        """
        self.model_provider = model_provider
        self.prompt_engineer = PromptEngineer()
        
        # TODO: 初始化对应的 API client
        # self.api_client = QwenClient() or OpenAIClient()
    
    async def generate_zhihu_answer(
        self, 
        question: Dict, 
        context: Dict
    ) -> GeneratedContent:
        """生成知乎回答"""
        
        logger.info(f"Generating zhihu answer for: {question['title']}")
        
        prompt = self.prompt_engineer.get_zhihu_prompt({
            **context,
            **question
        })
        
        # TODO: 调用 AI API
        # response = await self.api_client.generate(prompt)
        
        # 示例返回
        sample_content = GeneratedContent(
            id=f"zhihu_{datetime.now().timestamp()}",
            title=f"如何高效学习 Python？——我的实战经验总结",
            content="""
【痛点描述】
很多想学 Python 的朋友都卡在入门阶段😅 看着简单的语法，一动手就出错；看教程一个个都会，离开视频就不会了...这种"眼高手低"的困境是不是特别熟悉？

【问题分析】
这主要是三个原因造成的：①缺少系统性学习计划 ②练习量不够 ③遇到问题没人及时解决。自学最大的障碍就是不知道"下一步该做什么"。

【解决方案】
建立"学 - 练 - 反馈"闭环是关键！每天保证 1-2 小时专注练习，遇到 error 不要怕，记录下来自己搜索解答，这就是成长的过程。

【产品推荐】
说到辅助工具，我强烈推荐这款在线编程学习平台✨ 它的特点是真适合小白：有完整的项目式课程体系、代码即时批改、还有大佬答疑社区。我之前卡壳的问题，在这里半小时就搞定了！

【使用体验】
学了两个月，现在已经能独立做小项目了。最开心的是看到自己的代码被 run 起来的那一刻，成就感满满💪

如果你也在为学 Python 纠结，不妨试试这个方法，祝你早日入门成功！🚀
            """,
            hashtags=["Python", "编程学习", "自学指南", "程序员"],
            structure={
                "pain_points": "learned in intro",
                "analysis": "systematic learning gap",
                "solution": "learn-practice-feedback loop",
                "recommendation": "online learning platform",
                "experience": "2 months progress"
            },
            platform="zhihu",
            quality_score=0.85,
        )
        
        return sample_content
    
    async def generate_xhs_post(
        self, 
        topic: Dict, 
        product_keywords: List[str],
        context: Dict
    ) -> GeneratedContent:
        """生成小红书笔记"""
        
        logger.info(f"Generating xhs post for: {topic['name']}")
        
        prompt = self.prompt_engineer.get_xhs_post_prompt({
            **context,
            "product_keywords": ",".join(product_keywords)
        })
        
        # TODO: 调用 AI API
        
        # 示例返回
        sample_content = GeneratedContent(
            id=f"xhs_{datetime.now().timestamp()}",
            title="🏠9 ㎡卧室改造!这些小物太香了✨",
            content="""
🌙下班回到这个温暖的小窝，一天的疲惫都消失了～

之前租房的时候，总觉得房间太小东西放不下😭
直到我发现了这几样收纳神器!

✨ 首先是这个床底收纳箱，能装太多啦!
衣服换季全塞进去，空间瞬间多了 30%
而且带滚轮的设计推拉超方便～

✨ 墙面置物架也绝绝子!
不用打孔的那种，出租房友好
放绿植香薰超好看，随手拍都出片📸

✨ 还有个折叠衣架
挂满衣服也不占地儿
晾完收起来就变成隐形人哈哈

用了这些东西之后，感觉房间变大了两倍!
关键是都超级便宜，几十块搞定一个小角落💰

姐妹们有什么提升幸福感的小物?
评论区安利给我呀~💕

#卧室收纳 #租房改造 #小户型 #家居好物 #提升幸福感
            """,
            hashtags=[
                "#卧室收纳", "#租房改造", "#小户型", 
                "#家居好物", "#提升幸福感", "#收纳神器",
                "#租房党必备", "#我的小窝", "#软装搭配", "#改造日记"
            ],
            structure={
                "opening": "emotional scene setting",
                "problem": "small room storage issue",
                "discovery": "found storage solutions",
                "products": ["under-bed box", "wall shelf", "folding rack"],
                "result": "room feels twice bigger",
                "call_to_action": "ask comments for more recommendations"
            },
            platform="xiaohongshu",
            quality_score=0.92,
        )
        
        return sample_content
    
    async def check_content_quality(
        self, 
        content: str, 
        platform: str,
        content_type: str = "post"
    ) -> Dict:
        """检查内容质量"""
        
        prompt = self.prompt_engineer.get_quality_check_prompt(
            content, content_type, platform
        )
        
        # TODO: 调用 AI API
        
        # 示例返回
        return {
            "score": 8.5,
            "reasons": [
                "开场有情感共鸣",
                "产品卖点清晰",
                "语气亲切自然",
                "有适当的 emoji 装饰",
                "结尾引导互动良好"
            ],
            "suggestions": [
                "可以再增加一点使用前后的对比",
                "可以考虑添加更多图片描述"
            ],
            "risk_words": [],
        }


async def auto_optimize_content(content: GeneratedContent) -> GeneratedContent:
    """根据历史数据自动优化内容"""
    
    # TODO: 加载用户历史数据
    # historical_posts = load_user_history(user_id)
    
    # 基于历史表现调整风格参数
    if content.quality_score < 0.7:
        # 如果质量不高，尝试多种版本
        logger.warning(f"Low quality score: {content.quality_score}, regenerating...")
        # ...再生成逻辑
        
    return content


if __name__ == "__main__":
    # 测试
    import asyncio
    
    async def test_generator():
        generator = ContentGenerator()
        
        # 测试知乎
        zh_question = {"title": "如何高效学习 Python?"}
        zh_context = {"keywords": ["学习资源", "编程语言"], "audience": "职场新人"}
        zh_result = await generator.generate_zhihu_answer(zh_question, zh_context)
        print(f"Zhihu Quality: {zh_result.quality_score}")
        
        # 测试小红书
        xhs_topic = {"name": "家居好物分享"}
        xhs_keywords = ["收纳箱", "置物架", "衣架"]
        xhs_context = {"scenes": ["卧室", "书房"], "style": "温馨生活风"}
        xhs_result = await generator.generate_xhs_post(xhs_topic, xhs_keywords, xhs_context)
        print(f"XHS Quality: {xhs_result.quality_score}")
    
    asyncio.run(test_generator())
