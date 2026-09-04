# VidInsight 2026-09-04 Day 2.1 — LocalVid-Summarizer 参考后完善方案

## 1. 本次调整原因

在原 Day 2 同步链路 `上传 -> FFmpeg -> faster-whisper -> Transcript` 已经设计完成的基础上，项目组进一步研究 `sunglasses233/LocalVid-Summarizer`。该项目使用 FastAPI、SQLite、后台 Worker、Faster-Whisper、时间戳字幕和一键 Launcher 组织本地视频处理流程。VidInsight 不直接复制其实现，而是吸收其中适合课程项目的软件工程思想，并保持 macOS + Python 3.11 的实现约束。

## 2. 9 月 4 日完善后的主链路

```text
视频/音频上传
    ↓
FastAPI 创建 Task (HTTP 202)
    ↓
SQLite: pending
    ↓
后台 Worker 领取任务
    ↓
FFmpeg → 16 kHz / mono / PCM WAV
    ↓
faster-whisper + Segment timestamp
    ↓
实时回写 progress/status
    ↓
Transcript JSON + SRT + metadata
    ↓
SQLite: completed
    ↓
Streamlit 轮询状态并展示结果
```

## 3. 新增工程能力

- SQLite `video_tasks`：持久化任务状态，不因浏览器刷新丢失处理状态。
- 后台 Worker：长视频转写不再长期占用上传 HTTP 请求。
- Progress：pending / extracting_audio / transcribing / writing_transcript / completed / failed。
- JSON + SRT：JSON 服务后续 RAG，SRT 服务字幕、人工检查和时间戳展示。
- Launcher：`python launcher.py` 同时启动 API、Worker 和 Streamlit。
- 兼容接口：保留 `/api/videos/process`，但新 UI 使用 `/api/tasks` 异步任务接口。
- 隐私与仓库卫生：媒体、字幕、SQLite 数据库、`.env` 均被 `.gitignore` 排除。

## 4. 仍然不在 9 月 4 日实现的内容

- Bilibili/抖音下载、cookies、油猴脚本。
- 人声分离、CUDA 特化。
- LLM 总结。
- Chroma/BM25/RRF/RAG（9 月 5 日起）。

这是主动的范围控制：先形成稳定的视频理解数据入口，避免提前引入平台下载、GPU 与 LLM 依赖。

## 5. 当日分工

| 角色 | 9/4 完善后工作 | 交付 |
|---|---|---|
| 产品/项目经理 | 更新 Day 2 验收标准、任务状态定义、截图证据与风险项 | 日报、验收清单、Issues |
| AI 算法工程师 | faster-whisper、时间戳、进度回调、Mac base/cpu/int8 baseline | `ai/asr/whisper_engine.py` |
| 后端工程师 | SQLite task DB、异步任务 API、Worker、FFmpeg、JSON/SRT | `task_db.py`、`video_worker.py`、API |
| 前端/测试工程师 | 任务提交、进度显示、Transcript UI、端到端测试 | `upload.py`、测试记录 |

## 6. Definition of Done

1. `/health` 返回 `pipeline=sqlite-worker-asr`。
2. 上传 MP4 后 `/api/tasks` 返回 202 和 task_id。
3. Worker 能把 pending 任务推进到 completed。
4. FFmpeg 输出 16000 Hz、单声道 PCM WAV。
5. Transcript JSON 非空并保留 start/end。
6. 同一任务生成 `transcript.srt`。
7. Streamlit 能看到进度和最终时间戳文本。
8. 非法扩展名返回 HTTP 400。
9. `.env`、媒体、字幕和 SQLite DB 不进入 Git。
10. GitHub 保留 feature branch、commits、PR 和测试证据。
