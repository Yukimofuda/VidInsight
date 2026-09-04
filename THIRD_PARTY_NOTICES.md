# Third-party references and notices

VidInsight is a course project that uses open-source libraries and studies public reference implementations.

## P47Parzival/Video-RAG
- Repository: https://github.com/P47Parzival/Video-RAG
- Role in VidInsight: reference for the video-RAG baseline and later LangChain/Chroma integration.
- License: MIT (verify the upstream repository at the revision used by the team).

## sunglasses233/LocalVid-Summarizer
- Repository: https://github.com/sunglasses233/LocalVid-Summarizer
- License: MIT.
- Role in the 2026-09-04 design review: engineering reference for separating FastAPI task submission, SQLite-backed task state, background worker processing, Faster-Whisper transcription, timestamped subtitle persistence, progress display, and one-command service startup.
- VidInsight does not vendor or copy LocalVid-Summarizer source files. The Day 2.1 implementation in this repository is independently written around VidInsight's existing FastAPI/Streamlit structure and macOS/Python 3.11 constraints.

Do not commit cookies, user media, API keys, model weights, or generated transcript databases.
