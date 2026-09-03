# VidInsight — 智影 AI 视频助手

AI 实战项目进阶项目一。面向课程视频、会议录像、访谈和技术分享，实现视频解析、Whisper 转写、混合检索和多轮问答，并返回时间戳证据。

## Day 1 status (2026-09-03)
- [x] 项目立项 / PRD / 技术选型 / 系统架构
- [x] 模块化工程骨架
- [x] FastAPI health baseline + smoke tests
- [x] Git 初始化与 main/develop 分支策略
- [x] Issue / Milestone backlog
- [ ] 在成员开发机安装完整 AI 依赖并运行真实视频 baseline
- [ ] Push 到远程 GitHub 仓库

## Target architecture
Video → FFmpeg → Adaptive Whisper → timestamp transcript → Adaptive Chunk → Dense(BGE/Chroma) + BM25 → RRF → optional rerank → LLM → answer + timestamp evidence

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn backend.api.main:app --reload
```
Open `http://127.0.0.1:8000/health`.

## Test
```bash
pytest -q
```

## GitHub publish
Create an empty repository named `VidInsight`, then:
```bash
git remote add origin https://github.com/<YOUR_ORG_OR_USER>/VidInsight.git
git push -u origin main
git push -u origin develop
```

## Open-source attribution
The project intends to adapt concepts and, where appropriate, MIT-licensed code from P47Parzival/Video-RAG. Keep upstream notices for any copied/adapted code. Major planned modifications: Chinese UI, adaptive ASR, adaptive chunking, BM25 + dense hybrid retrieval, RRF, multi-query, timestamp evidence, multi-turn chat, evaluation framework and persistent storage.
