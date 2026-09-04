from __future__ import annotations

import os

import requests
import streamlit as st

API_URL = os.getenv("VIDINSIGHT_API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="VidInsight Workspace", page_icon="🔎", layout="wide")
st.title("VidInsight · 检索工作区")
st.caption("Day 3 starter：Transcript → Adaptive Chunk → BGE Embedding → Chroma → Semantic Search")

video_id = st.text_input(
    "Video / Task ID",
    value=st.session_state.get("vidinsight_task_id", ""),
    help="完成视频转写后，使用同一个 task_id 建立检索索引。",
)

left, right = st.columns([1, 2])
with left:
    if st.button("建立/刷新语义索引", type="primary", use_container_width=True, disabled=not bool(video_id.strip())):
        try:
            response = requests.post(f"{API_URL}/api/videos/{video_id.strip()}/index", timeout=3600)
            response.raise_for_status()
            result = response.json()
        except requests.RequestException as exc:
            st.error(f"索引失败：{exc}")
        else:
            st.success(f"索引完成：{result['chunk_count']} chunks")
            st.json(result)

with right:
    query = st.text_input("语义检索问题", placeholder="例如：视频中什么时候解释了 RAG？")
    top_k = st.slider("Top-K", 1, 10, 5)
    if st.button("检索证据", use_container_width=True, disabled=not bool(video_id.strip() and query.strip())):
        try:
            response = requests.get(
                f"{API_URL}/api/videos/{video_id.strip()}/search",
                params={"q": query, "top_k": top_k},
                timeout=120,
            )
            response.raise_for_status()
            result = response.json()
        except requests.RequestException as exc:
            st.error(f"检索失败：{exc}")
        else:
            hits = result.get("hits", [])
            if not hits:
                st.info("没有检索到结果。")
            for index, hit in enumerate(hits, start=1):
                distance = hit.get("distance")
                distance_text = f" · distance={distance:.4f}" if isinstance(distance, (float, int)) else ""
                with st.container(border=True):
                    st.markdown(
                        f"**#{index} · [{hit['start']:.2f}s - {hit['end']:.2f}s]**{distance_text}"
                    )
                    st.write(hit["text"])
