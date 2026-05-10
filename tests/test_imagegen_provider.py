from unittest.mock import patch

from providers.imagegen.factory import get_imagegen_provider
from providers.imagegen.mflux import MfluxProvider


def test_factory_disabled_by_default(monkeypatch):
    monkeypatch.delenv("IMAGEGEN_ENABLED", raising=False)
    monkeypatch.delenv("IMAGEGEN_PROVIDER", raising=False)
    assert get_imagegen_provider() is None


def test_factory_truthy_env_enables(monkeypatch):
    monkeypatch.setenv("IMAGEGEN_ENABLED", "true")
    monkeypatch.delenv("IMAGEGEN_PROVIDER", raising=False)
    monkeypatch.setattr(MfluxProvider, "is_available", lambda self: True)
    p = get_imagegen_provider()
    assert p is not None
    assert p.name == "mflux"


def test_factory_returns_none_when_provider_unavailable(monkeypatch):
    monkeypatch.setenv("IMAGEGEN_ENABLED", "true")
    monkeypatch.setattr(MfluxProvider, "is_available", lambda self: False)
    assert get_imagegen_provider() is None


def test_factory_explicit_override_implies_enabled(monkeypatch):
    monkeypatch.delenv("IMAGEGEN_ENABLED", raising=False)
    monkeypatch.setenv("IMAGEGEN_PROVIDER", "mflux")
    monkeypatch.setattr(MfluxProvider, "is_available", lambda self: True)
    p = get_imagegen_provider()
    assert p is not None and p.name == "mflux"


def test_factory_unknown_provider_returns_none(monkeypatch):
    monkeypatch.setenv("IMAGEGEN_ENABLED", "true")
    monkeypatch.setenv("IMAGEGEN_PROVIDER", "nonsense")
    assert get_imagegen_provider() is None


def test_mflux_disabled_off_apple_silicon(monkeypatch):
    with patch("utils.is_mac_fast_path_available", return_value=False):
        assert MfluxProvider().is_available() is False


def test_mflux_resolves_model_alias_default(monkeypatch):
    monkeypatch.delenv("MFLUX_MODEL", raising=False)
    p = MfluxProvider()
    assert p._model_alias() == "schnell"


def test_mflux_quantize_default(monkeypatch):
    monkeypatch.delenv("MFLUX_QUANTIZE", raising=False)
    p = MfluxProvider()
    assert p._quantize() == 4


def test_mflux_quantize_off(monkeypatch):
    monkeypatch.setenv("MFLUX_QUANTIZE", "none")
    p = MfluxProvider()
    assert p._quantize() is None


def test_mflux_steps_schnell_default(monkeypatch):
    monkeypatch.setenv("MFLUX_MODEL", "schnell")
    monkeypatch.delenv("MFLUX_STEPS", raising=False)
    assert MfluxProvider()._steps() == 4


def test_mflux_steps_dev_default(monkeypatch):
    monkeypatch.setenv("MFLUX_MODEL", "dev")
    monkeypatch.delenv("MFLUX_STEPS", raising=False)
    assert MfluxProvider()._steps() == 20


def test_mflux_steps_explicit_override(monkeypatch):
    monkeypatch.setenv("MFLUX_STEPS", "10")
    assert MfluxProvider()._steps() == 10
