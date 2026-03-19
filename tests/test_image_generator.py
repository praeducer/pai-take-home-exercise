
from src.pipeline.image_generator import (
    DRY_RUN_PIXEL,
    _cache_key,
    _get_cached,
    _save_cached,
    generate_image,
)


def test_dry_run_returns_placeholder():
    result = generate_image("test prompt", "1:1", "dev", dry_run=True)
    assert result == DRY_RUN_PIXEL


def test_env_dry_run_returns_placeholder(monkeypatch):
    monkeypatch.setenv("PAI_DRY_RUN", "1")
    result = generate_image("test prompt", "1:1", "dev")
    assert result == DRY_RUN_PIXEL


def test_cache_key_is_deterministic():
    k1 = _cache_key("prompt", 1024, 1024, "model")
    k2 = _cache_key("prompt", 1024, 1024, "model")
    assert k1 == k2


def test_cache_key_differs_for_different_prompts():
    k1 = _cache_key("prompt-a", 1024, 1024, "model")
    k2 = _cache_key("prompt-b", 1024, 1024, "model")
    assert k1 != k2


def test_cache_key_differs_for_different_dims():
    k1 = _cache_key("prompt", 1024, 1024, "model")
    k2 = _cache_key("prompt", 576, 1024, "model")
    assert k1 != k2


def test_cache_hit_returns_cached_bytes(tmp_path, monkeypatch):
    monkeypatch.setattr("src.pipeline.image_generator.CACHE_DIR", tmp_path)
    test_bytes = b"fake-image-data"
    key = _cache_key("prompt", 1024, 1024, "model")
    _save_cached(key, test_bytes)
    result = _get_cached(key)
    assert result == test_bytes


def test_cache_miss_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr("src.pipeline.image_generator.CACHE_DIR", tmp_path)
    result = _get_cached("nonexistent-key")
    assert result is None
