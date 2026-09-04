from __future__ import annotations

import os
import time

import requests
import streamlit as st

API_URL = os.getenv("VIDINSIGHT_API_URL", "http://127.0.0.1:8000")
POLL_SECONDS = 1.2

st.set_page_config(page_title="VidInsight", page_icon="🎬", layout="wide")
st.title("VidInsight")
st.subheader("智影 AI 视频助手 · Day 2 异步视频转写")
st.caption(
    "上传后创建后台任务：SQLite 任务队列 → Worker → FFmpeg → faster-whisper → JSON/SRT 时间戳字幕。"
)

uploaded_file = st.file_uploader(
    "上传视频或音频",
    type=["mp4", "mov", "mkv", "avi", "webm", "mp3", "wav", "m4a"],
)

if uploaded_file is not None:
    if uploaded_file.type and uploaded_file.type.startswith("video/"):
        st.video(uploaded_file)
    else:
        st.audio(uploaded_file)

    if st.button("提交 AI 解析任务", type="primary", use_container_width=True):
        try:
            response = requests.post(
                f"{API_URL}/api/tasks",
                files={
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type or "application/octet-stream",
                    )
                },
                timeout=120,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            st.error(f"任务创建失败：{exc}")
        else:
            task = response.json()
            task_id = task["task_id"]
            st.session_state["vidinsight_task_id"] = task_id
            st.success(f"任务已提交：{task_id}")

if task_id := st.session_state.get("vidinsight_task_id"):
    st.divider()
    st.subheader("后台处理进度")
    progress_bar = st.progress(0)
    stage_box = st.empty()
    details_box = st.empty()

    terminal = {"completed", "failed"}
    latest = None
    for _ in range(3600):
        try:
            status_response = requests.get(f"{API_URL}/api/tasks/{task_id}", timeout=15)
            status_response.raise_for_status()
            latest = status_response.json()
        except requests.RequestException as exc:
            stage_box.error(f"读取任务状态失败：{exc}")
            break

        progress = int(latest.get("progress", 0))
        progress_bar.progress(max(0, min(progress, 100)))
        stage_box.info(
            f"{latest['status']} · {progress}% · {latest.get('stage_message') or ''}"
        )
        if latest["status"] in terminal:
            break
        time.sleep(POLL_SECONDS)

    if latest and latest["status"] == "failed":
        st.error(latest.get("error_message") or "后台任务失败")
    elif latest and latest["status"] == "completed":
        try:
            transcript_response = requests.get(
                f"{API_URL}/api/videos/{task_id}/transcript", timeout=30
            )
            transcript_response.raise_for_status()
            data = transcript_response.json()
        except requests.RequestException as exc:
            st.error(f"读取 Transcript 失败：{exc}")
        else:
            st.success("视频解析完成")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("语言", data["language"])
            col2.metric("语言置信度", f"{data['language_probability']:.2%}")
            col3.metric("视频/音频时长", f"{data['duration_seconds']:.1f}s")
            col4.metric("ASR 耗时", f"{data['processing_seconds']:.1f}s")
            details_box.caption(
                f"ASR model: {data['asr_model']} · task/video id: {data['video_id']}"
            )

            st.subheader("完整 Transcript")
            st.write(data["text"] or "（未识别到文本）")

            st.subheader("时间戳 Transcript")
            for segment in data["segments"]:
                st.markdown(
                    f"**[{segment['start']:.2f}s – {segment['end']:.2f}s]**  {segment['text']}"
                )

            st.caption("同一结果同时保存为 transcript.json、transcript.srt 和 metadata.json。")
