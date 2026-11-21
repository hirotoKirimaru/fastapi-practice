"""SECRET の既定値の扱い（以前はプロセスごとの乱数で、複数プロセスでトークンが通らなかった）"""

import pytest

from src.helper.config import Settings


def test_secret_required_outside_local(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SECRET", raising=False)
    with pytest.raises(ValueError, match="SECRET"):
        Settings(_env_file=None, ENV="prod")  # type: ignore[call-arg]


def test_secret_is_random_with_warning_on_local(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SECRET", raising=False)
    with pytest.warns(UserWarning, match="SECRET"):
        settings = Settings(_env_file=None, ENV="local")  # type: ignore[call-arg]
    assert len(settings.SECRET) >= 32


def test_secret_from_environment_is_used(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SECRET", "a-fixed-secret-for-all-processes")
    monkeypatch.setenv("FIRST_SUPERUSER_PASSWORD", "a-real-admin-password")
    settings = Settings(_env_file=None, ENV="prod")  # type: ignore[call-arg]
    assert settings.SECRET == "a-fixed-secret-for-all-processes"


def test_default_superuser_password_rejected_outside_local(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SECRET", "a-fixed-secret-for-all-processes")
    monkeypatch.delenv("FIRST_SUPERUSER_PASSWORD", raising=False)
    with pytest.raises(ValueError, match="FIRST_SUPERUSER_PASSWORD"):
        Settings(_env_file=None, ENV="prod")  # type: ignore[call-arg]
