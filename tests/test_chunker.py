from ai.preprocessing.chunker import ChunkPolicy, build_chunks, estimate_tokens, policy_for_duration


def _segments(count: int):
    return [
        {"id": i, "start": i * 2.0, "end": i * 2.0 + 1.5, "text": f"第{i}段人工智能课程内容。"}
        for i in range(count)
    ]


def test_duration_policy_scales_up():
    assert policy_for_duration(5 * 60).target_tokens == 350
    assert policy_for_duration(20 * 60).target_tokens == 600
    assert policy_for_duration(45 * 60).target_tokens == 900


def test_estimate_tokens_handles_chinese_and_latin():
    assert estimate_tokens("人工智能") >= 4
    assert estimate_tokens("retrieval augmented generation") > 0


def test_chunks_preserve_timestamp_boundaries():
    chunks = build_chunks(
        _segments(8),
        video_id="demo",
        duration_seconds=60,
        policy=ChunkPolicy(target_tokens=20, max_tokens=30, overlap_segments=1),
    )
    assert len(chunks) >= 2
    assert chunks[0]["start"] == 0.0
    assert chunks[0]["end"] > chunks[0]["start"]
    assert chunks[0]["segment_ids"]
    assert all(item["video_id"] == "demo" for item in chunks)
