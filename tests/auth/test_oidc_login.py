# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT

import json
import platform
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from ansys.hps.client.auth.api.oidc_login import (
    _is_token_expired,
    _load_from_disk,
    _load_from_keyring,
    _save_to_keyring,
    load_tokens,
    save_tokens,
)


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


# ---------------------------------------------------------------------------
# Token Expiration Tests
# ---------------------------------------------------------------------------


def test_is_token_expired_with_valid_token(sample_tokens):
    """Token is not expired if elapsed time is less than expires_in."""
    tokens = sample_tokens.copy()
    tokens["saved_at"] = time.time()
    tokens["expires_in"] = 3600
    assert not _is_token_expired(tokens)


def test_is_token_expired_with_expired_token(sample_tokens):
    """Token is expired if elapsed time exceeds expires_in."""
    tokens = sample_tokens.copy()
    tokens["saved_at"] = time.time() - 4000  # 4000 seconds ago
    tokens["expires_in"] = 3600  # expires in 3600 seconds from save
    assert _is_token_expired(tokens)


def test_is_token_expired_with_buffer(sample_tokens):
    """Token is considered expired when approaching expiry (buffer)."""
    tokens = sample_tokens.copy()
    tokens["saved_at"] = time.time() - 3550  # 3550 seconds elapsed
    tokens["expires_in"] = 3600  # only 50 seconds left
    # With default 60s buffer, should be considered expired
    assert _is_token_expired(tokens, buffer_seconds=60)


def test_is_token_expired_missing_fields():
    """Token without expires_in or saved_at is considered expired."""
    assert _is_token_expired({})
    assert _is_token_expired({"expires_in": 3600})
    assert _is_token_expired({"saved_at": time.time()})


# ---------------------------------------------------------------------------
# Keyring Tests
# ---------------------------------------------------------------------------


def test_save_to_keyring_success(sample_tokens, sample_hps_url):
    """Saving tokens to keyring succeeds with keyring available."""
    import sys
    from unittest.mock import MagicMock

    mock_keyring = MagicMock()
    with patch.dict(sys.modules, {"keyring": mock_keyring}):
        result = _save_to_keyring(sample_tokens, sample_hps_url)

        assert result is True
        # Verify all token fields were saved
        assert mock_keyring.set_password.call_count >= 6
        calls = [call[0] for call in mock_keyring.set_password.call_args_list]
        service_names = [call[0] for call in calls]
        assert all(s == "ansys-hps" for s in service_names)


def test_save_to_keyring_keyring_not_installed(sample_tokens, sample_hps_url):
    """Saving to keyring returns False if keyring module not available."""
    with patch.dict("sys.modules", {"keyring": None}):
        with patch("builtins.__import__", side_effect=ImportError("No module named 'keyring'")):
            result = _save_to_keyring(sample_tokens, sample_hps_url)
            assert result is False


def test_save_to_keyring_handles_errors(sample_tokens, sample_hps_url):
    """Keyring save gracefully handles exceptions."""
    import sys

    mock_keyring = MagicMock()
    mock_keyring.set_password.side_effect = RuntimeError("Keyring error")
    with patch.dict(sys.modules, {"keyring": mock_keyring}):
        result = _save_to_keyring(sample_tokens, sample_hps_url)
        assert result is False


def test_load_from_keyring_success(sample_tokens, sample_hps_url):
    """Loading tokens from keyring succeeds."""
    import sys

    mock_keyring = MagicMock()
    mock_keyring.get_password.side_effect = lambda service, key: {
        "hps_url": sample_hps_url,
        "access_token": sample_tokens["access_token"],
        "refresh_token": sample_tokens["refresh_token"],
        "expires_in": str(sample_tokens["expires_in"]),
        "refresh_expires_in": str(sample_tokens["refresh_expires_in"]),
        "saved_at": str(sample_tokens["saved_at"]),
    }.get(key)

    with patch.dict(sys.modules, {"keyring": mock_keyring}):
        result = _load_from_keyring()

        assert result is not None
        assert result["access_token"] == sample_tokens["access_token"]
        assert result["hps_url"] == sample_hps_url


def test_load_from_keyring_no_tokens():
    """Loading from keyring returns None if no tokens exist."""
    import sys

    mock_keyring = MagicMock()
    mock_keyring.get_password.return_value = None
    with patch.dict(sys.modules, {"keyring": mock_keyring}):
        result = _load_from_keyring()
        assert result is None


def test_load_from_keyring_not_installed():
    """Loading from keyring returns None if keyring not available."""
    with patch.dict("sys.modules", {"keyring": None}):
        result = _load_from_keyring()
        assert result is None


# ---------------------------------------------------------------------------
# Disk Storage Tests
# ---------------------------------------------------------------------------


def test_save_to_disk_unix(sample_tokens, sample_hps_url, tmp_path, monkeypatch):
    """Tokens saved to disk with 0o600 permissions on Unix."""
    if platform.system() == "Windows":
        pytest.skip("Unix-specific test")

    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    monkeypatch.setattr(
        "ansys.hps.client.auth.api.oidc_login.TOKEN_FILE",
        token_file,
    )

    with patch("ansys.hps.client.auth.api.oidc_login.platform.system", return_value="Linux"):
        result = save_tokens(sample_tokens, sample_hps_url, persist=True, use_keyring=False)

    assert result == token_file
    assert token_file.exists()
    # Check file permissions
    mode = token_file.stat().st_mode & 0o777
    assert mode == 0o600


def test_save_to_disk_and_load(sample_tokens, sample_hps_url, tmp_path, monkeypatch):
    """Tokens can be saved and loaded from disk."""
    if platform.system() == "Windows":
        pytest.skip("Non-DPAPI test")

    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    monkeypatch.setattr(
        "ansys.hps.client.auth.api.oidc_login.TOKEN_FILE",
        token_file,
    )

    with patch("ansys.hps.client.auth.api.oidc_login.platform.system", return_value="Linux"):
        # Save tokens
        save_tokens(sample_tokens, sample_hps_url, persist=True, use_keyring=False)

        # Load tokens
        loaded = _load_from_disk()

    assert loaded is not None
    assert loaded["access_token"] == sample_tokens["access_token"]
    assert loaded["hps_url"] == sample_hps_url


def test_load_from_disk_file_not_exist(tmp_path, monkeypatch):
    """Loading from non-existent file returns None."""
    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    monkeypatch.setattr(
        "ansys.hps.client.auth.api.oidc_login.TOKEN_FILE",
        token_file,
    )
    result = _load_from_disk()
    assert result is None


def test_load_from_disk_invalid_json(tmp_path, monkeypatch):
    """Loading invalid JSON returns None with warning."""
    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_bytes(b"invalid json {{{")

    monkeypatch.setattr(
        "ansys.hps.client.auth.api.oidc_login.TOKEN_FILE",
        token_file,
    )

    result = _load_from_disk()
    assert result is None


# ---------------------------------------------------------------------------
# Combined Token Loading Tests
# ---------------------------------------------------------------------------


def test_load_tokens_prefers_keyring(sample_tokens, sample_hps_url, tmp_path, monkeypatch):
    """load_tokens() prefers keyring over disk."""
    # Set up disk storage
    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    monkeypatch.setattr(
        "ansys.hps.client.auth.api.oidc_login.TOKEN_FILE",
        token_file,
    )

    with patch("ansys.hps.client.auth.api.oidc_login._load_from_keyring") as mock_keyring:
        with patch("ansys.hps.client.auth.api.oidc_login._load_from_disk") as mock_disk:
            keyring_tokens = sample_tokens.copy()
            mock_keyring.return_value = keyring_tokens
            mock_disk.return_value = None

            result = load_tokens()

            assert result == keyring_tokens
            mock_keyring.assert_called_once()
            mock_disk.assert_not_called()


def test_load_tokens_fallback_to_disk(sample_tokens, sample_hps_url, tmp_path, monkeypatch):
    """load_tokens() falls back to disk if keyring unavailable."""
    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    monkeypatch.setattr(
        "ansys.hps.client.auth.api.oidc_login.TOKEN_FILE",
        token_file,
    )

    with patch("ansys.hps.client.auth.api.oidc_login._load_from_keyring") as mock_keyring:
        with patch("ansys.hps.client.auth.api.oidc_login._load_from_disk") as mock_disk:
            disk_tokens = sample_tokens.copy()
            mock_keyring.return_value = None
            mock_disk.return_value = disk_tokens

            result = load_tokens()

            assert result == disk_tokens
            mock_keyring.assert_called_once()
            mock_disk.assert_called_once()


# ---------------------------------------------------------------------------
# save_tokens Integration Tests
# ---------------------------------------------------------------------------


def test_save_tokens_keep_in_memory(sample_tokens, sample_hps_url):
    """save_tokens with storage="memory" returns None (in-memory)."""
    result = save_tokens(sample_tokens, sample_hps_url, storage="memory")
    assert result is None


def test_save_tokens_disk_storage(sample_tokens, sample_hps_url, tmp_path, monkeypatch):
    """save_tokens with storage="disk" saves to disk."""
    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    monkeypatch.setattr(
        "ansys.hps.client.auth.api.oidc_login.TOKEN_FILE",
        token_file,
    )

    with patch("ansys.hps.client.auth.api.oidc_login.platform.system", return_value="Linux"):
        result = save_tokens(sample_tokens, sample_hps_url, storage="disk")

        assert result == token_file
        assert token_file.exists()


def test_save_tokens_prefer_keyring(sample_tokens, sample_hps_url, tmp_path, monkeypatch):
    """save_tokens with storage="keyring" tries keyring first."""
    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    monkeypatch.setattr(
        "ansys.hps.client.auth.api.oidc_login.TOKEN_FILE",
        token_file,
    )

    with patch("ansys.hps.client.auth.api.oidc_login._save_to_keyring") as mock_keyring:
        mock_keyring.return_value = True  # Keyring save succeeds

        result = save_tokens(sample_tokens, sample_hps_url, storage="keyring")

        mock_keyring.assert_called_once()
        assert result is None  # Keyring returns None for path


def test_save_tokens_fallback_to_disk_if_keyring_fails(
    sample_tokens, sample_hps_url, tmp_path, monkeypatch
):
    """save_tokens falls back to disk if keyring save fails."""
    if platform.system() == "Windows":
        pytest.skip("Test requires mocking platform.system() on non-Windows")

    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    monkeypatch.setattr(
        "ansys.hps.client.auth.api.oidc_login.TOKEN_FILE",
        token_file,
    )

    # Create a custom _save_to_keyring that returns False
    def mock_save_to_keyring(tokens, hps_url):
        return False

    with patch("ansys.hps.client.auth.api.oidc_login._save_to_keyring", mock_save_to_keyring):
        with patch("ansys.hps.client.auth.api.oidc_login.platform.system", return_value="Linux"):
            result = save_tokens(sample_tokens, sample_hps_url, storage="keyring")

            assert result == token_file
            assert token_file.exists()


def test_save_tokens_invalid_storage_method(sample_tokens, sample_hps_url):
    """save_tokens raises ValueError for invalid storage method."""
    with pytest.raises(ValueError, match="Invalid storage method"):
        save_tokens(sample_tokens, sample_hps_url, storage="invalid")

