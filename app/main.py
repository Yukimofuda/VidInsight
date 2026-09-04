from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="VidInsight", page_icon="🎬", layout="wide")
st.title("VidInsight — 智影 AI 视频助手")
st.caption("课程视频 / 会议 / 访谈 / 技术分享的本地视频理解与可追溯检索")

st.markdown(
    """
### 当前开发链路

**视频上传 → SQLite Task → Worker → FFmpeg → faster-whisper → Transcript JSON/SRT → Adaptive Chunk → BGE/Chroma → Timestamp Evidence**

左侧页面用于分阶段验证：

- **upload**：提交视频任务、查看处理进度和时间戳 Transcript。
- **workspace**：对已完成 Transcript 建立语义索引并验证 Top-K evidence。
- **chat / history**：后续多轮问答与历史会话入口，当前仍为占位模块。

> 当前版本刻意把视频处理层与 RAG 层解耦：即使 Embedding/Chroma 未安装或模型下载失败，ASR 任务仍可独立完成。
"""
)
