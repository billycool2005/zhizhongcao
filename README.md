# 🐵 智种草 (Zhizhongcao)

**AI-powered Q&A and Xiaohongshu auto-publishing platform | AI 问答种草自动发文工具**

---

## 🚀 快速启动

```bash
cd team/backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 QWEN_API_KEY

# 启动服务
python -m uvicorn app.main:app --reload

# 访问 API 文档
http://localhost:8000/docs
```

---

## Docker 运行

```bash
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 访问
http://localhost:8000
```

---

## 核心功能

- 🤖 **AI Crawler**: 自动抓取知乎/小红书高流量问题
- ✍️ **AI Writer**: 按模板生成高质量种草文（质量>0.7）
- 📢 **Auto Publish**: 自动排版发布，完全不用管
- 🎯 **Quality Control**: Token 监控 + 风控，避免封号

---

## 项目状态

```
✅ Alpha v0.1 - In Development
🎯 Target Launch: 2026-03-26 22:00 CST
```

---

_由悟空 AI Team 开发 | MIT License_
