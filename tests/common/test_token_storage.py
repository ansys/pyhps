# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#

import json
import logging
import os
import platform
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ansys.hps.client.common.token_storage import (
    _atomic_write_bytes,
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


def test_is_token_expired_with_valid_token(sample_tokens):
    """Token is not expired if elapsed time is less than expires_in."""
    tokens = sample_tokens.copy()
    tokens["saved_at"] = time.time()
    tokens["expires_in"] = 3600
    assert not _is_token_expired(tokens)


def test_is_token_expired_with_expired_token(sample_tokens):
    """Token is expired if elapsed time exceeds expires_in."""
    tokens = sample_tokens.copy()
    tokens["saved_at"] = time.time() - 4000
    tokens["expires_in"] = 3600
    assert _is_token_expired(tokens)


def test_is_token_expired_with_buffer(sample_tokens):
    """Token is considered expired when approaching expiry (buffer)."""
    tokens = sample_tokens.copy()
    tokens["saved_at"] = time.time() - 3550
    tokens["expires_in"] = 3600
    assert _is_token_expired(tokens, buffer_seconds=60)


def test_is_token_expired_missing_fields():
    """Token without expires_in or saved_at is considered expired."""
    assert _is_token_expired({})
    assert _is_token_expired({"expires_in": 3600})
    assert _is_token_expired({"saved_at": time.time()})


def test_save_to_keyring_success(sample_tokens, sample_hps_url):
    """Saving tokens to keyring succeeds with keyring available."""
    mock_keyring = MagicMock()
    with patch.dict(sys.modules, {"keyring": mock_keyring}):
        result = _save_to_keyring(sample_tokens, sample_hps_url)

        assert result is True
        assert mock_keyring.set_password.call_count >= 6
        calls = [call[0] for call in mock_keyring.set_password.call_args_list]
        service_names = [call[0] for call in calls]
        assert all(s == "ansys-hps" for s in service_names)


def test_save_to_keyring_with_custom_service_name(sample_tokens, sample_hps_url):
    """Saving to keyring uses explicitly provided service name."""
    mock_keyring = MagicMock()
    custom_service_name = "ansys-hps-dev"
    with patch.dict(sys.modules, {"keyring": mock_keyring}):
        result = _save_to_keyring(sample_tokens, sample_hps_url, service_name=custom_service_name)

        assert result is True
        calls = [call[0] for call in mock_keyring.set_password.call_args_list]
        service_names = [call[0] for call in calls]
        assert all(s == custom_service_name for s in service_names)


def test_save_to_keyring_keyring_not_installed(sample_tokens, sample_hps_url):
    """Saving to keyring returns False if keyring module not available."""
    with patch.dict("sys.modules", {"keyring": None}):
        with patch("builtins.__import__", side_effect=ImportError("No module named 'keyring'")):
            result = _save_to_keyring(sample_tokens, sample_hps_url)
            assert result is False


def test_save_to_keyring_handles_errors(sample_tokens, sample_hps_url):
    """Keyring save gracefully handles exceptions."""
    mock_keyring = MagicMock()
    mock_keyring.set_password.side_effect = RuntimeError("Keyring error")
    with patch.dict(sys.modules, {"keyring": mock_keyring}):
        result = _save_to_keyring(sample_tokens, sample_hps_url)
        assert result is False


def test_save_to_keyring_logs_redacted_error(sample_tokens, sample_hps_url, caplog):
    """Keyring save errors are logged with redacted sensitive fragments."""
    mock_keyring = MagicMock()
    mock_keyring.set_password.side_effect = RuntimeError("Authorization bearer abc.def.ghi")

    with patch.dict(sys.modules, {"keyring": mock_keyring}):
        with caplog.at_level(logging.WARNING, logger="ansys.hps.client.common.token_storage"):
            result = _save_to_keyring(sample_tokens, sample_hps_url)

    assert result is False
    assert "abc.def.ghi" not in caplog.text
    assert "bearer ***REDACTED***" in caplog.text


def test_load_from_keyring_success(sample_tokens, sample_hps_url):
    """Loading tokens from keyring succeeds."""
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


def test_load_from_keyring_with_custom_service_name(sample_tokens, sample_hps_url):
    """Loading from keyring uses explicitly provided service name."""
    custom_service_name = "ansys-hps-stage"
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
        result = _load_from_keyring(service_name=custom_service_name)

        assert result is not None
        assert result["access_token"] == sample_tokens["access_token"]
        get_calls = [call[0] for call in mock_keyring.get_password.call_args_list]
        service_names = [call[0] for call in get_calls]
        assert all(s == custom_service_name for s in service_names)


def test_load_from_keyring_no_tokens():
    """Loading from keyring returns None if no tokens exist."""
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


def test_load_from_keyring_invalid_numeric_fields(sample_tokens, sample_hps_url):
    """Loading from keyring returns None if numeric fields are malformed."""
    mock_keyring = MagicMock()
    mock_keyring.get_password.side_effect = lambda service, key: {
        "hps_url": sample_hps_url,
        "access_token": sample_tokens["access_token"],
        "refresh_token": sample_tokens["refresh_token"],
        "expires_in": "not-an-int",
        "refresh_expires_in": str(sample_tokens["refresh_expires_in"]),
        "saved_at": str(sample_tokens["saved_at"]),
    }.get(key)

    with patch.dict(sys.modules, {"keyring": mock_keyring}):
        result = _load_from_keyring()
        assert result is None


def test_load_tokens_keyring_mode_only_uses_keyring(sample_tokens):
    """token_storage.load_tokens(storage='keyring') reads only from keyring."""
    with patch("ansys.hps.client.common.token_storage._load_from_keyring") as mock_keyring:
        with patch("ansys.hps.client.common.token_storage._load_from_disk") as mock_disk:
            keyring_tokens = sample_tokens.copy()
            mock_keyring.return_value = keyring_tokens
            mock_disk.return_value = None

            result = load_tokens(storage="keyring")

            assert result == keyring_tokens
            mock_keyring.assert_called_once()
            mock_disk.assert_not_called()


def test_load_tokens_disk_mode_only_uses_disk(sample_tokens):
    """token_storage.load_tokens(storage='disk') reads only from disk."""
    with patch("ansys.hps.client.common.token_storage._load_from_keyring") as mock_keyring:
        with patch("ansys.hps.client.common.token_storage._load_from_disk") as mock_disk:
            disk_tokens = sample_tokens.copy()
            mock_keyring.return_value = sample_tokens.copy()
            mock_disk.return_value = disk_tokens

            result = load_tokens(storage="disk")

            assert result == disk_tokens
            mock_keyring.assert_not_called()
            mock_disk.assert_called_once()


def test_load_tokens_uses_env_service_name(monkeypatch):
    """token_storage.load_tokens keyring mode uses service name from env var."""
    monkeypatch.setenv("HPS_OIDC_KEYRING_SERVICE_NAME", "ansys-hps-env")

    with patch("ansys.hps.client.common.token_storage._load_from_keyring") as mock_keyring:
        with patch("ansys.hps.client.common.token_storage._load_from_disk") as mock_disk:
            mock_keyring.return_value = None
            mock_disk.return_value = None

            _ = load_tokens(storage="keyring")

            mock_keyring.assert_called_once_with(service_name="ansys-hps-env")
            mock_disk.assert_not_called()


def test_load_tokens_invalid_storage_method():
    """token_storage.load_tokens raises ValueError for invalid storage method."""
    with pytest.raises(ValueError, match="Invalid storage method"):
        _ = load_tokens(storage="invalid")


def test_save_tokens_keep_in_memory(sample_tokens, sample_hps_url):
    """save_tokens with storage='memory' returns None."""
    result = save_tokens(sample_tokens, sample_hps_url, storage="memory")
    assert result is None


def test_save_tokens_disk_storage(sample_tokens, sample_hps_url, tmp_path, monkeypatch):
    """save_tokens with storage='disk' saves to disk."""
    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    monkeypatch.setattr("ansys.hps.client.common.token_storage.TOKEN_FILE", token_file)

    with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Linux"):
        result = save_tokens(sample_tokens, sample_hps_url, storage="disk")

        assert result == token_file
        assert token_file.exists()


def test_save_to_disk_unix(sample_tokens, sample_hps_url, tmp_path, monkeypatch):
    """Tokens saved to disk with 0o600 permissions on Unix."""
    if platform.system() == "Windows":
        pytest.skip("Unix-specific test")

    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    monkeypatch.setattr("ansys.hps.client.common.token_storage.TOKEN_FILE", token_file)

    with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Linux"):
        result = save_tokens(sample_tokens, sample_hps_url, storage="disk")

    assert result == token_file
    assert token_file.exists()
    mode = token_file.stat().st_mode & 0o777
    assert mode == 0o600


def test_save_to_disk_and_load(sample_tokens, sample_hps_url, tmp_path, monkeypatch):
    """Tokens can be saved and loaded from disk."""
    if platform.system() == "Windows":
        pytest.skip("Non-DPAPI test")

    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    monkeypatch.setattr("ansys.hps.client.common.token_storage.TOKEN_FILE", token_file)

    with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Linux"):
        save_tokens(sample_tokens, sample_hps_url, storage="disk")
        loaded = _load_from_disk()

    assert loaded is not None
    assert loaded["access_token"] == sample_tokens["access_token"]
    assert loaded["hps_url"] == sample_hps_url


def test_load_from_disk_file_not_exist(tmp_path, monkeypatch):
    """Loading from non-existent file returns None."""
    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    monkeypatch.setattr("ansys.hps.client.common.token_storage.TOKEN_FILE", token_file)
    result = _load_from_disk()
    assert result is None


def test_load_from_disk_invalid_json(tmp_path, monkeypatch):
    """Loading invalid JSON returns None with warning."""
    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_bytes(b"invalid json {{{")

    monkeypatch.setattr("ansys.hps.client.common.token_storage.TOKEN_FILE", token_file)

    result = _load_from_disk()
    assert result is None


def test_load_from_disk_logs_redacted_error(tmp_path, monkeypatch, caplog):
    """Disk load errors are logged with redacted sensitive fragments."""
    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text("{}", encoding="utf-8")

    monkeypatch.setattr("ansys.hps.client.common.token_storage.TOKEN_FILE", token_file)

    with patch(
        "ansys.hps.client.common.token_storage.json.loads",
        side_effect=RuntimeError("Authorization header bearer abc.def.ghi"),
    ):
        with caplog.at_level(logging.WARNING, logger="ansys.hps.client.common.token_storage"):
            result = _load_from_disk()

    assert result is None
    assert "abc.def.ghi" not in caplog.text
    assert "bearer ***REDACTED***" in caplog.text


def test_atomic_write_bytes_fsyncs_parent_directory_on_unix(tmp_path):
    """Atomic write fsyncs the parent directory on Unix-like platforms."""
    target = tmp_path / "hps_tokens.json"
    directory_fd = 424242
    real_os_open = os.open
    real_os_close = os.close

    def open_side_effect(path, flags, *args):
        if Path(path) == target.parent and flags == os.O_RDONLY:
            return directory_fd
        return real_os_open(path, flags, *args)

    def close_side_effect(fd):
        if fd == directory_fd:
            return None
        return real_os_close(fd)

    with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Linux"):
        with patch("ansys.hps.client.common.token_storage.os.open", side_effect=open_side_effect):
            with patch(
                "ansys.hps.client.common.token_storage.os.close", side_effect=close_side_effect
            ):
                with patch("ansys.hps.client.common.token_storage.os.fsync") as mock_fsync:
                    _atomic_write_bytes(target, b"{}", mode=0o600)

    assert target.read_bytes() == b"{}"
    assert any(call.args and call.args[0] == directory_fd for call in mock_fsync.call_args_list)


def test_load_from_disk_invalid_schema_missing_access_token(tmp_path, monkeypatch):
    """Loading token payload without required access_token returns None."""
    token_file = tmp_path / ".ansys" / "hps_tokens.json"
    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text(json.dumps({"hps_url": "https://example.com:8443/hps"}), encoding="utf-8")

    monkeypatch.setattr("ansys.hps.client.common.token_storage.TOKEN_FILE", token_file)

    result = _load_from_disk()
    assert result is None


def test_save_tokens_invalid_storage_method(sample_tokens, sample_hps_url):
    """save_tokens raises ValueError for invalid storage method."""
    with pytest.raises(ValueError, match="Invalid storage method"):
        save_tokens(sample_tokens, sample_hps_url, storage="invalid")


def test_save_tokens_missing_required_access_token(sample_hps_url):
    """save_tokens raises ValueError when required access_token is missing."""
    with pytest.raises(ValueError, match="access_token"):
        save_tokens({"refresh_token": "abc"}, sample_hps_url, storage="memory")


def test_save_tokens_invalid_numeric_field(sample_tokens, sample_hps_url):
    """save_tokens raises ValueError when numeric fields are malformed."""
    bad_tokens = sample_tokens.copy()
    bad_tokens["expires_in"] = "bad-int"

    with pytest.raises(ValueError, match="expires_in"):
        save_tokens(bad_tokens, sample_hps_url, storage="memory")


def test_save_tokens_keyring_raises_when_keyring_unavailable(sample_tokens, sample_hps_url):
    """save_tokens in keyring mode raises when keyring persistence fails."""
    with patch("ansys.hps.client.common.token_storage._save_to_keyring", return_value=False):
        with pytest.raises(RuntimeError, match="Keyring storage requested"):
            _ = save_tokens(sample_tokens, sample_hps_url, storage="keyring")
