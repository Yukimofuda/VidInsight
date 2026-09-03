from fastapi.testclient import TestClient
from backend.api.main import app
from ai.asr.adaptive_selector import select_asr_plan
from ai.preprocessing.chunker import target_chunk_tokens
from ai.retrieval.rrf import reciprocal_rank_fusion

def test_health():
    r = TestClient(app).get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'

def test_adaptive_asr_cpu_long_video():
    p = select_asr_plan(45, False, 0)
    assert p.segmented is True
    assert p.engine == 'faster-whisper'

def test_chunk_policy():
    assert target_chunk_tokens(5) == (350, 500)
    assert target_chunk_tokens(20) == (600, 800)
    assert target_chunk_tokens(60) == (900, 1200)

def test_rrf():
    out = reciprocal_rank_fusion([['a','b'], ['b','a']])
    assert {x[0] for x in out} == {'a','b'}
