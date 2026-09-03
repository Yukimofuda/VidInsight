def target_chunk_tokens(video_minutes: float) -> tuple[int, int]:
    if video_minutes < 10:
        return (350, 500)
    if video_minutes <= 30:
        return (600, 800)
    return (900, 1200)
