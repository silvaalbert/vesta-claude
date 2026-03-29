"""Tests for config.py — environment variable loading and validation."""

from __future__ import annotations

import pytest

from vesta_claude.config import load_config


class TestLoadConfig:
    def test_dry_run_defaults_to_true(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        monkeypatch.delenv("DRY_RUN", raising=False)
        monkeypatch.delenv("VESTABOARD_API_TOKEN", raising=False)
        config = load_config()
        assert config.dry_run is True

    def test_dry_run_does_not_require_vestaboard_token(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("DRY_RUN", "true")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        monkeypatch.delenv("VESTABOARD_API_TOKEN", raising=False)
        config = load_config()
        assert config.dry_run is True

    def test_no_credentials_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
        monkeypatch.setenv("DRY_RUN", "true")
        with pytest.raises(ValueError, match="No credentials found"):
            load_config()

    def test_bedrock_backend_selected_from_aws_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIAIOSFODNN7EXAMPLE")
        monkeypatch.setenv("DRY_RUN", "true")
        config = load_config()
        assert config.backend == "bedrock"

    def test_anthropic_preferred_when_both_credentials_set(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIAIOSFODNN7EXAMPLE")
        monkeypatch.setenv("DRY_RUN", "true")
        config = load_config()
        assert config.backend == "anthropic"

    def test_bedrock_default_region(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIAIOSFODNN7EXAMPLE")
        monkeypatch.delenv("AWS_DEFAULT_REGION", raising=False)
        monkeypatch.setenv("DRY_RUN", "true")
        config = load_config()
        assert config.aws_region == "us-east-1"

    def test_bedrock_custom_region(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIAIOSFODNN7EXAMPLE")
        monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-1")
        monkeypatch.setenv("DRY_RUN", "true")
        config = load_config()
        assert config.aws_region == "eu-west-1"

    def test_missing_vestaboard_token_raises_when_not_dry_run(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        monkeypatch.delenv("VESTABOARD_API_TOKEN", raising=False)
        monkeypatch.setenv("DRY_RUN", "false")
        with pytest.raises(ValueError, match="VESTABOARD_API_TOKEN"):
            load_config()

    def test_default_model_anthropic(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        monkeypatch.delenv("CLAUDE_MODEL", raising=False)
        config = load_config()
        assert config.model == "claude-sonnet-4-6"

    def test_default_model_bedrock(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIAIOSFODNN7EXAMPLE")
        monkeypatch.delenv("CLAUDE_MODEL", raising=False)
        config = load_config()
        assert config.model == "us.anthropic.claude-sonnet-4-6"

    def test_custom_model(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        monkeypatch.setenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
        config = load_config()
        assert config.model == "claude-haiku-4-5-20251001"

    @pytest.mark.parametrize(  # type: ignore[misc]
        "value", ["1", "true", "True", "TRUE", "yes", "YES"]
    )
    def test_dry_run_truthy_values(
        self, monkeypatch: pytest.MonkeyPatch, value: str
    ) -> None:
        monkeypatch.setenv("DRY_RUN", value)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        config = load_config()
        assert config.dry_run is True

    @pytest.mark.parametrize("value", ["0", "false", "no", ""])  # type: ignore[misc]
    def test_dry_run_falsy_values(
        self, monkeypatch: pytest.MonkeyPatch, value: str
    ) -> None:
        monkeypatch.setenv("DRY_RUN", value)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        monkeypatch.setenv("VESTABOARD_API_TOKEN", "token")
        config = load_config()
        assert config.dry_run is False
