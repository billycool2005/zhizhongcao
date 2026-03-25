"""
ContentFlow Models - 数据库模型定义
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text, Index, func
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    accounts = relationship("Account", back_populates="user")
    contents = relationship("Content", back_populates="author")
    
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_username', 'username'),
    )


class Account(Base):
    """平台账号表 (知乎/小红书)"""
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    platform = Column(String(20), nullable=False)  # zhihu, xiaohongshu
    account_id = Column(String(100), unique=True)
    username = Column(String(100))
    avatar_url = Column(String(500))
    follower_count = Column(Integer, default=0)
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime)
    is_connected = Column(Boolean, default=False)
    status = Column(String(20), default='pending')  # pending, connected, error
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="accounts")
    contents = relationship("Content", back_populates="account")
    
    __table_args__ = (
        Index('idx_account_platform_uid', 'platform', 'account_id'),
    )


class Content(Base):
    """内容生成记录表"""
    __tablename__ = 'contents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    account_id = Column(Integer, ForeignKey('accounts.id'))
    platform = Column(String(20))
    content_type = Column(String(20))  # answer, post
    title = Column(String(500))
    body = Column(Text)
    tags = Column(Text)  # JSON string
    image_urls = Column(Text)  # JSON string
    
    # 来源
    source_question_id = Column(String(100))
    source_question_title = Column(String(500))
    source_url = Column(String(1000))
    
    # 状态
    status = Column(String(20), default='draft')  # draft, reviewing, published, failed
    publish_status_code = Column(Integer)
    publish_message = Column(Text)
    
    # 数据追踪
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    
    # AI 相关
    prompt_version = Column(String(50))
    model_used = Column(String(50))
    tokens_used = Column(Integer, default=0)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime)
    published_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", backref="contents")
    account = relationship("Account", back_populates="contents")
    
    __table_args__ = (
        Index('idx_content_user_platform', 'user_id', 'platform', 'status'),
    )


class CrawlerQueue(Base):
    """爬虫任务队列"""
    __tablename__ = 'crawler_queue'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    platform = Column(String(20))
    topic_keywords = Column(Text)  # JSON
    max_results = Column(Integer, default=50)
    
    status = Column(String(20), default='pending')  # pending, running, completed, error
    current_page = Column(Integer, default=1)
    total_found = Column(Integer, default=0)
    
    last_crawled_at = Column(DateTime)
    next_retry_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User")
    
    __table_args__ = (
        Index('idx_queue_user_status', 'user_id', 'status'),
    )


class DailyStats(Base):
    """日报统计表"""
    __tablename__ = 'daily_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    date = Column(DateTime, default=datetime.utcnow.date)
    
    platforms = Column(Text)  # JSON: {zhihu: {...}, xiaohongshu: {...}}
    
    total_contents_generated = Column(Integer, default=0)
    total_published = Column(Integer, default=0)
    total_views = Column(Fl