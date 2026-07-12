import pytest

from intellicrawl.settings import LiveSettings

BASE = {
    "FIRECRAWL_API_KEY": "fc-test",
    "OPENAI_API_KEY": "sk-test",
}


def test_settings_load_defaults_without_exposing_keys(tmp_path) -> None:
    settings = LiveSettings.from_environment({**BASE, "INTELLICRAWL_CACHE_DIR": str(tmp_path)})
    assert settings.openai_model == "gpt-5.4-mini"
    assert settings.cache_dir == tmp_path
    assert settings.max_tools == 4
    assert "fc-test" not in repr(settings)


def test_explicit_empty_environment_does_not_fall_back_to_process(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-process")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-process")
    with pytest.raises(ValueError, match="FIRECRAWL_API_KEY, OPENAI_API_KEY"):
        LiveSettings.from_environment({})


@pytest.mark.parametrize(
    ("name", "value"),
    (
        ("INTELLICRAWL_CACHE_TTL", "-1"),
        ("INTELLICRAWL_TIMEOUT", "0"),
        ("INTELLICRAWL_MAX_TOOLS", "7"),
        ("INTELLICRAWL_CONCURRENCY", "9"),
        ("INTELLICRAWL_TIMEOUT", "not-a-number"),
        ("INTELLICRAWL_OPENAI_MODEL", ""),
    ),
)
def test_invalid_settings_fail_fast(name: str, value: str) -> None:
    with pytest.raises(ValueError):
        LiveSettings.from_environment({**BASE, name: value})
