import importlib

import config
import src.services.ai_generator as ai_generator


def test_supabase_compat_aliases(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://demo.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-key")
    importlib.reload(config)

    assert config.SUPABASE_URL == "https://demo.supabase.co"
    assert config.SUPABASE_KEY == "service-role-key"
    assert config.SUPABASE_SERVICE_ROLE_KEY == "service-role-key"


def test_openai_key_aliases(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("OPEN_AI_API_KEY", "legacy-openai-key")
    importlib.reload(ai_generator)
    assert ai_generator.get_openai_api_key() == "test-openai-key"

    monkeypatch.setenv("OPENAI_API_KEY", "priority-openai-key")
    monkeypatch.setenv("OPEN_AI_API_KEY", "legacy-openai-key")
    importlib.reload(ai_generator)
    assert ai_generator.get_openai_api_key() == "priority-openai-key"
