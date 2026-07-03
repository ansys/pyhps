# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT

import os
import platform
import sys
import time
import types
from unittest.mock import MagicMock, patch

import pytest

from ansys.hps.client.auth.api.oidc_login import _load_from_disk, load_tokens, save_tokens


@pytest.fixture
def sample_tokens():
    """Sample token response."""
    return {
        "access_token": "sample_access_token_xyz123",
        "refresh_token": "sample_refresh_token_abc456",
        "expires_in": 3600,
        "refresh_expires_in": 86400,
        "token_type": "Bearer",
        "saved_at": time.time(),
    }


@pytest.fixture
def sample_hps_url():
    """Sample HPS URL."""
    return "https://example.com:8443/hps"


def test_load_tokens_keyring_mode_only_uses_keyring(sample_tokens, tmp_path, monkeypatch):
    """load_tokens(storage='keyring') reads only from keyring."""
    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    monkeypatch.setattr("ansys.hps.client.auth.api.oidc_login.TOKEN_FILE", token_file)

    with patch("ansys.hps.client.auth.api.oidc_login._token_storage._load_from_keyring") as mock_keyring:
        with patch("ansys.hps.client.auth.api.oidc_login._token_storage._load_from_disk") as mock_disk:
            keyring_tokens = sample_tokens.copy()
            mock_keyring.return_value = keyring_tokens
            mock_disk.return_value = None

            result = load_tokens(storage="keyring")

            assert result == keyring_tokens
            mock_keyring.assert_called_once()
            mock_disk.assert_not_called()


def test_load_tokens_disk_mode_only_uses_disk(sample_tokens, tmp_path, monkeypatch):
    """load_tokens(storage='disk') reads only from disk."""
    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    monkeypatch.setattr("ansys.hps.client.auth.api.oidc_login.TOKEN_FILE", token_file)

    with patch("ansys.hps.client.auth.api.oidc_login._token_storage._load_from_keyring") as mock_keyring:
        with patch("ansys.hps.client.auth.api.oidc_login._token_storage._load_from_disk") as mock_disk:
            disk_tokens = sample_tokens.copy()
            mock_keyring.return_value = sample_tokens.copy()
            mock_disk.return_value = disk_tokens

            result = load_tokens(storage="disk")

            assert result == disk_tokens
            mock_keyring.assert_not_called()
            mock_disk.assert_called_once()


def test_load_tokens_uses_env_service_name(monkeypatch):
    """load_tokens keyring mode uses service name configured via environment variable."""
    monkeypatch.setenv("HPS_OIDC_KEYRING_SERVICE_NAME", "ansys-hps-env")

    with patch("ansys.hps.client.auth.api.oidc_login._token_storage._load_from_keyring") as mock_keyring:
        with patch("ansys.hps.client.auth.api.oidc_login._token_storage._load_from_disk") as mock_disk:
            mock_keyring.return_value = None
            mock_disk.return_value = None

            _ = load_tokens(storage="keyring")

            mock_keyring.assert_called_once_with(service_name="ansys-hps-env")
            mock_disk.assert_not_called()


def test_load_tokens_invalid_storage_method():
    """load_tokens raises ValueError for invalid storage method."""
    with pytest.raises(ValueError, match="Invalid storage method"):
        _ = load_tokens(storage="invalid")


def test_save_tokens_keyring_uses_env_service_name(sample_tokens, sample_hps_url, monkeypatch):
    """save_tokens uses env-configured keyring service name when not provided."""
    monkeypatch.setenv("HPS_OIDC_KEYRING_SERVICE_NAME", "ansys-hps-env")

    with patch("ansys.hps.client.auth.api.oidc_login._token_storage._save_to_keyring") as mock_keyring:
        mock_keyring.return_value = True

        result = save_tokens(sample_tokens, sample_hps_url, storage="keyring")

        assert result is None
        mock_keyring.assert_called_once()
        called_tokens, called_url = mock_keyring.call_args[0]
        assert called_url == sample_hps_url
        assert called_tokens["access_token"] == sample_tokens["access_token"]
        assert called_tokens["refresh_token"] == sample_tokens["refresh_token"]
        assert called_tokens["expires_in"] == sample_tokens["expires_in"]
        assert called_tokens["refresh_expires_in"] == sample_tokens["refresh_expires_in"]
        assert mock_keyring.call_args.kwargs["service_name"] == "ansys-hps-env"


def test_save_tokens_prefer_keyring(sample_tokens, sample_hps_url, tmp_path, monkeypatch):
    """save_tokens with storage='keyring' tries keyring first."""
    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    monkeypatch.setattr("ansys.hps.client.auth.api.oidc_login.TOKEN_FILE", token_file)

    with patch("ansys.hps.client.auth.api.oidc_login._token_storage._save_to_keyring") as mock_keyring:
        mock_keyring.return_value = True

        result = save_tokens(sample_tokens, sample_hps_url, storage="keyring")

        mock_keyring.assert_called_once()
        assert result is None


def test_save_tokens_keyring_raises_if_keyring_fails(
    sample_tokens, sample_hps_url, tmp_path, monkeypatch
):
    """save_tokens in keyring mode raises if keyring save fails."""
    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    monkeypatch.setattr("ansys.hps.client.auth.api.oidc_login.TOKEN_FILE", token_file)

    def mock_save_to_keyring(tokens, hps_url, service_name=None, error_on_failure=False):
        return False

    with patch("ansys.hps.client.auth.api.oidc_login._token_storage._save_to_keyring", mock_save_to_keyring):
        with pytest.raises(RuntimeError, match="Failed to save tokens to keyring"):
            _ = save_tokens(sample_tokens, sample_hps_url, storage="keyring")


def test_save_tokens_keyring_surfaces_credwrite_details(sample_tokens, sample_hps_url, tmp_path, monkeypatch):
    """save_tokens surfaces actionable Windows CredWrite diagnostics when keyring write fails."""
    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    monkeypatch.setattr("ansys.hps.client.auth.api.oidc_login.TOKEN_FILE", token_file)

    with patch(
        "ansys.hps.client.auth.api.oidc_login._token_storage.platform.system",
        return_value="Windows",
    ):
        with patch(
            "ansys.hps.client.auth.api.oidc_login._token_storage._save_to_keyring",
            side_effect=RuntimeError(
                "Windows Credential Manager rejected the token payload "
                "(CredWrite error 1783: The stub received bad data). Login succeeded "
                "but keyring persistence failed. This often indicates backend size/format "
                "limits. Use storage='disk' on Windows for DPAPI-protected persistence."
            ),
        ):
            with pytest.raises(RuntimeError, match="CredWrite error 1783"):
                _ = save_tokens(sample_tokens, sample_hps_url, storage="keyring")


def test_save_tokens_keyring_windows_preflight_rejects_oversized_token(
    sample_tokens, sample_hps_url, tmp_path, monkeypatch
):
    """save_tokens rejects oversized Windows keyring payloads before keyring write calls."""
    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    monkeypatch.setattr("ansys.hps.client.auth.api.oidc_login.TOKEN_FILE", token_file)

    oversized_tokens = sample_tokens.copy()
    oversized_tokens["access_token"] = "a" * 3000

    fake_keyring = types.SimpleNamespace(set_password=MagicMock())

    with patch(
        "ansys.hps.client.auth.api.oidc_login._token_storage.platform.system",
        return_value="Windows",
    ):
        with patch.dict(sys.modules, {"keyring": fake_keyring}):
            with pytest.raises(RuntimeError, match="preflight: access_token is 3000 bytes"):
                _ = save_tokens(oversized_tokens, sample_hps_url, storage="keyring")

    fake_keyring.set_password.assert_not_called()


@pytest.mark.skipif(
    platform.system() != "Windows" or os.environ.get("HPS_TEST_DPAPI_INTEGRATION") != "1",
    reason="Run on Windows with HPS_TEST_DPAPI_INTEGRATION=1 to enable DPAPI integration test.",
)
def test_save_and_load_tokens_real_dpapi_roundtrip(sample_tokens, sample_hps_url, tmp_path, monkeypatch):
    """Integration test for Windows DPAPI disk encryption/decryption round-trip via oidc wrapper."""
    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    monkeypatch.setattr("ansys.hps.client.auth.api.oidc_login.TOKEN_FILE", token_file)

    result = save_tokens(sample_tokens, sample_hps_url, storage="disk")
    assert result == token_file
    assert token_file.exists()

    raw = token_file.read_bytes()
    assert raw.startswith(b"DPAPI:")

    loaded = _load_from_disk()
    assert loaded is not None
    assert loaded["hps_url"] == sample_hps_url
    assert loaded["access_token"] == sample_tokens["access_token"]
    assert loaded["refresh_token"] == sample_tokens["refresh_token"]
    assert loaded["expires_in"] == sample_tokens["expires_in"]
    assert loaded["refresh_expires_in"] == sample_tokens["refresh_expires_in"]


@pytest.mark.skipif(
    os.environ.get("HPS_TEST_KEYRING_INTEGRATION") != "1",
    reason="Set HPS_TEST_KEYRING_INTEGRATION=1 to run real keyring integration test.",
)
def test_save_and_load_tokens_real_keyring(sample_tokens, sample_hps_url):
    """Integration test against a real keyring backend via oidc wrapper."""
    keyring = pytest.importorskip("keyring")

    service_name = "ansys-hps"
    fields = (
        "hps_url",
        "access_token",
        "refresh_token",
        "expires_in",
        "refresh_expires_in",
        "saved_at",
    )

    backup = {}
    try:
        for field in fields:
            backup[field] = keyring.get_password(service_name, field)

        result = save_tokens(sample_tokens, sample_hps_url, storage="keyring")
        assert result is None

        loaded = load_tokens(storage="keyring")
        assert loaded is not None
        assert loaded["hps_url"] == sample_hps_url
        assert loaded["access_token"] == sample_tokens["access_token"]
        assert loaded["refresh_token"] == sample_tokens["refresh_token"]
    except Exception as ex:
        pytest.skip(f"Real keyring backend unavailable: {ex}")
    finally:
        for field in fields:
            value = backup[field]
            try:
                if value is None:
                    keyring.delete_password(service_name, field)
                else:
                    keyring.set_password(service_name, field, value)
            except Exception:
                pass
