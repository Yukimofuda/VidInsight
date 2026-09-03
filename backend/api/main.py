from fastapi import FastAPI

app = FastAPI(title="VidInsight API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok", "project": "VidInsight", "day": "2026-09-03"}
