# Baseline Runbook

Day 1 defines the reproducible baseline procedure. Execute on a member workstation with Internet access.

1. Install Python 3.10/3.11 and FFmpeg.
2. Create venv and install `requirements.txt`.
3. Copy `.env.example` to `.env` and configure one LLM provider.
4. Run `python scripts/check_environment.py`.
5. Run `pytest -q`.
6. Run `uvicorn backend.api.main:app --reload` and verify `/health`.
7. Clone/reference P47Parzival/Video-RAG separately, verify its upstream README, license and baseline behavior before porting any code.
8. Use one 3–5 minute Chinese video on Day 2 for real ASR.

Do not claim the full AI baseline is successful until Whisper + retrieval + LLM is actually executed and screenshots/logs are saved.
