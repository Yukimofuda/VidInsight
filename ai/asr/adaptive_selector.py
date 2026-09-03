from dataclasses import dataclass

@dataclass(frozen=True)
class ASRPlan:
    model: str
    engine: str
    segmented: bool

def select_asr_plan(video_minutes: float, cuda_available: bool=False, vram_gb: float=0.0) -> ASRPlan:
    if cuda_available and vram_gb >= 6:
        model = "small"
    elif cuda_available:
        model = "base"
    else:
        model = "base" if video_minutes <= 30 else "tiny"
    engine = "faster-whisper" if video_minutes > 10 else "whisper"
    return ASRPlan(model=model, engine=engine, segmented=video_minutes > 30)
