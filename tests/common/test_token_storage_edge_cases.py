# Copyright (C) 2022 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Extended unit tests for token_storage.py covering uncovered code paths and edge cases."""

import os
import platform
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ansys.hps.client.common.token_storage import (
    WINDOWS_KEYRING_MAX_SECRET_BYTES,
    _atomic_write_bytes,
    _check_disk_storage_backend,
    _check_keyring_backend,
    _check_storage_backend,
    _format_keyring_save_error,
    _get_windows_keyring_preflight_error,
    _load_from_disk,
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


# ============================================================================
# Error Formatting Functions Tests
# ============================================================================


class TestFormatKeyringError:
    """Tests for _format_keyring_save_error() function."""

    def test_format_generic_error_non_windows(self):
        """Format generic error on non-Windows platform."""
        error = RuntimeError("Connection timeout to keyring service")
        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Linux"):
            result = _format_keyring_save_error(error)
            assert "Failed to save tokens to keyring" in result
            assert "Connection timeout" in result

    def test_format_windows_error_1783_credwrite(self):
        """Format Windows CredWrite error 1783 (size limit)."""
        error = Exception(1783, "CredWrite", "The buffer is too small")
        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Windows"):
            result = _format_keyring_save_error(error)
            assert "Windows Credential Manager rejected" in result
            assert "1783" in result
            assert "size/format limits" in result
            assert "storage='disk'" in result

    def test_format_windows_error_credwrite_in_message(self):
        """Format Windows error with CredWrite mentioned in message."""
        error = RuntimeError("CredWrite failed with code 1783")
        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Windows"):
            result = _format_keyring_save_error(error)
            assert "Windows Credential Manager rejected" in result
            assert "storage='disk'" in result

    def test_format_error_with_sensitive_token_redaction(self, sample_tokens):
        """Ensure error message redacts sensitive token fragments."""
        error = RuntimeError("Failed with token: bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Linux"):
            result = _format_keyring_save_error(error, sample_tokens)
            assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in result
            assert "***REDACTED***" in result

    def test_format_error_without_tokens_dict(self):
        """Format error without providing tokens dict."""
        error = RuntimeError("Keyring unavailable")
        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Linux"):
            result = _format_keyring_save_error(error, None)
            assert "Keyring unavailable" in result

    def test_format_error_with_empty_args(self):
        """Format error with exception that has no args."""
        error = RuntimeError()
        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Linux"):
            result = _format_keyring_save_error(error)
            assert "Failed to save tokens to keyring" in result

    def test_format_error_with_non_integer_first_arg(self):
        """Format error where first arg is not an integer error code."""
        error = Exception("string_arg", "CredWrite", "some detail")
        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Windows"):
            result = _format_keyring_save_error(error)
            # Should fall back to generic message since first arg is not an int
            assert "Failed to save tokens to keyring" in result


# ============================================================================
# Windows Preflight Checks Tests
# ============================================================================


class TestWindowsKeyringPreflightError:
    """Tests for _get_windows_keyring_preflight_error() function."""

    def test_preflight_returns_none_on_non_windows(self):
        """Preflight check returns None on non-Windows platforms."""
        tokens = {
            "access_token": "a" * (WINDOWS_KEYRING_MAX_SECRET_BYTES + 100),
            "refresh_token": "b" * (WINDOWS_KEYRING_MAX_SECRET_BYTES + 100),
        }
        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Linux"):
            result = _get_windows_keyring_preflight_error(tokens)
            assert result is None

    def test_preflight_access_token_too_large(self):
        """Preflight check detects oversized access_token."""
        oversized_token = "x" * (WINDOWS_KEYRING_MAX_SECRET_BYTES + 100)
        tokens = {
            "access_token": oversized_token,
            "refresh_token": "small_token",
        }
        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Windows"):
            result = _get_windows_keyring_preflight_error(tokens)
            assert result is not None
            assert "access_token" in result
            assert str(WINDOWS_KEYRING_MAX_SECRET_BYTES + 100) in result
            assert "storage='disk'" in result

    def test_preflight_refresh_token_too_large(self):
        """Preflight check detects oversized refresh_token."""
        oversized_token = "y" * (WINDOWS_KEYRING_MAX_SECRET_BYTES + 50)
        tokens = {
            "access_token": "small_token",
            "refresh_token": oversized_token,
        }
        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Windows"):
            result = _get_windows_keyring_preflight_error(tokens)
            assert result is not None
            assert "refresh_token" in result
            assert str(WINDOWS_KEYRING_MAX_SECRET_BYTES + 50) in result

    def test_preflight_both_tokens_acceptable_size(self):
        """Preflight check passes when both tokens are under limit."""
        tokens = {
            "access_token": "small_access",
            "refresh_token": "small_refresh",
        }
        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Windows"):
            result = _get_windows_keyring_preflight_error(tokens)
            assert result is None

    def test_preflight_handles_missing_tokens(self):
        """Preflight check handles tokens dict with missing fields."""
        tokens = {"expires_in": 3600}
        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Windows"):
            result = _get_windows_keyring_preflight_error(tokens)
            assert result is None

    def test_preflight_handles_none_token_values(self):
        """Preflight check skips None token values."""
        tokens = {"access_token": None, "refresh_token": None}
        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Windows"):
            result = _get_windows_keyring_preflight_error(tokens)
            assert result is None

    def test_preflight_handles_empty_string_tokens(self):
        """Preflight check handles empty string tokens."""
        tokens = {"access_token": "", "refresh_token": ""}
        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Windows"):
            result = _get_windows_keyring_preflight_error(tokens)
            assert result is None

    def test_preflight_utf8_encoded_size_matters(self):
        """Preflight check accounts for UTF-8 encoded bytes, not string length."""
        # Multi-byte UTF-8 characters
        token_with_unicode = "€" * 1000  # Euro sign is 3 bytes in UTF-8
        tokens = {
            "access_token": token_with_unicode,
            "refresh_token": "small",
        }
        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Windows"):
            result = _get_windows_keyring_preflight_error(tokens)
            # 1000 Euro signs = 3000 bytes, which exceeds the limit
            assert result is not None
            assert "access_token" in result


# ============================================================================
# Backend Availability Checks Tests
# ============================================================================


class TestCheckDiskStorageBackend:
    """Tests for _check_disk_storage_backend() function."""

    def test_check_disk_backend_success(self, tmp_path, monkeypatch):
        """Disk storage backend check succeeds when directory is writable."""
        token_file = tmp_path / ".ansys" / "hps_tokens.json"
        monkeypatch.setattr("ansys.hps.client.common.token_storage.TOKEN_FILE", token_file)

        result = _check_disk_storage_backend()
        assert result is None

    def test_check_disk_backend_directory_permissions_denied(self, tmp_path, monkeypatch):
        """Disk storage backend check returns error on permission denied."""
        token_file = tmp_path / ".ansys" / "hps_tokens.json"
        token_file.parent.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr("ansys.hps.client.common.token_storage.TOKEN_FILE", token_file)

        if platform.system() != "Windows":
            # Remove write permissions on Unix
            token_file.parent.chmod(0o444)
            try:
                result = _check_disk_storage_backend()
                assert result is not None
                assert "Permission denied" in result or "permission" in result.lower()
            finally:
                # Restore permissions for cleanup
                token_file.parent.chmod(0o755)

    def test_check_disk_backend_read_only_filesystem(self, tmp_path, monkeypatch):
        """Disk storage backend check handles read-only filesystem."""
        token_file = tmp_path / "hps_tokens.json"
        monkeypatch.setattr("ansys.hps.client.common.token_storage.TOKEN_FILE", token_file)

        # Mock mkdir to raise permission error

        def mock_mkdir_error(self, *args, **kwargs):
            raise PermissionError("Read-only file system")

        with patch.object(Path, "mkdir", mock_mkdir_error):
            result = _check_disk_storage_backend()
            assert result is not None
            assert "Read-only" in result


class TestCheckStorageBackend:
    """Tests for _check_storage_backend() function."""

    def test_check_backend_memory_always_available(self):
        """Memory storage backend is always available."""
        result = _check_storage_backend("memory")
        assert result is None

    def test_check_backend_disk_delegates_to_disk_check(self, tmp_path, monkeypatch):
        """Storage backend check for disk delegates to _check_disk_storage_backend."""
        token_file = tmp_path / ".ansys" / "hps_tokens.json"
        monkeypatch.setattr("ansys.hps.client.common.token_storage.TOKEN_FILE", token_file)

        result = _check_storage_backend("disk")
        assert result is None

    def test_check_backend_keyring_delegates_to_keyring_check(self):
        """Storage backend check for keyring delegates to _check_keyring_backend."""
        from unittest.mock import Mock

        from ansys.hps.client.common.token_storage import _CHECK_HANDLERS, TokenStorage

        mock_check = Mock(return_value=None)
        with patch.dict(_CHECK_HANDLERS, {TokenStorage.KEYRING: mock_check}):
            result = _check_storage_backend("keyring")
            assert result is None
            mock_check.assert_called_once()

    def test_check_backend_keyring_error_propagates(self):
        """Storage backend check propagates keyring backend errors."""
        from unittest.mock import Mock

        from ansys.hps.client.common.token_storage import _CHECK_HANDLERS, TokenStorage

        error_msg = "Keyring unavailable"
        mock_check = Mock(return_value=error_msg)
        with patch.dict(_CHECK_HANDLERS, {TokenStorage.KEYRING: mock_check}):
            result = _check_storage_backend("keyring")
            assert result == error_msg

    def test_check_backend_invalid_storage_method(self):
        """Storage backend check raises ValueError for invalid storage method."""
        with pytest.raises(ValueError, match="Invalid storage method"):
            _check_storage_backend("invalid_method")


class TestCheckKeyringBackend:
    """Tests for _check_keyring_backend() function."""

    def test_check_keyring_backend_not_installed(self):
        """Keyring backend check returns error when keyring not installed."""
        with patch.dict(sys.modules, {"keyring": None}):
            with patch("builtins.__import__", side_effect=ImportError("No module keyring")):
                result = _check_keyring_backend()
                assert result is not None
                assert "keyring" in result.lower()
                assert "not installed" in result

    def test_check_keyring_backend_success(self):
        """Keyring backend check succeeds when keyring is available."""
        mock_keyring = MagicMock()
        mock_keyring.set_password = MagicMock()
        mock_keyring.delete_password = MagicMock()

        with patch.dict(sys.modules, {"keyring": mock_keyring}):
            result = _check_keyring_backend()
            assert result is None
            mock_keyring.set_password.assert_called_once()
            mock_keyring.delete_password.assert_called_once()

    def test_check_keyring_backend_set_password_fails(self):
        """Keyring backend check returns error if set_password fails."""
        mock_keyring = MagicMock()
        mock_keyring.set_password.side_effect = RuntimeError("Keyring service unavailable")

        with patch.dict(sys.modules, {"keyring": mock_keyring}):
            result = _check_keyring_backend()
            assert result is not None
            assert "unavailable" in result.lower()


# ============================================================================
# Save Tokens Edge Cases Tests
# ============================================================================


class TestSaveTokensEdgeCases:
    """Tests for edge cases in save_tokens() function."""

    def test_save_tokens_invalid_hps_url_empty_string(self, sample_tokens):
        """save_tokens raises ValueError for empty hps_url."""
        with pytest.raises(ValueError, match="hps_url"):
            save_tokens(sample_tokens, "", storage="memory")

    def test_save_tokens_invalid_hps_url_only_whitespace(self, sample_tokens):
        """save_tokens raises ValueError for whitespace-only hps_url."""
        with pytest.raises(ValueError, match="hps_url"):
            save_tokens(sample_tokens, "   ", storage="memory")

    def test_save_tokens_invalid_hps_url_type(self, sample_tokens):
        """save_tokens raises ValueError for non-string hps_url."""
        with pytest.raises(ValueError, match="hps_url"):
            save_tokens(sample_tokens, 12345, storage="memory")

    def test_save_tokens_invalid_hps_url_none(self, sample_tokens):
        """save_tokens raises ValueError for None hps_url."""
        with pytest.raises(ValueError, match="hps_url"):
            save_tokens(sample_tokens, None, storage="memory")

    def test_save_tokens_disk_with_permission_denied(
        self, sample_tokens, sample_hps_url, tmp_path, monkeypatch
    ):
        """save_tokens to disk handles permission denied errors."""
        token_file = tmp_path / ".ansys" / "hps_tokens.json"
        token_file.parent.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr("ansys.hps.client.common.token_storage.TOKEN_FILE", token_file)

        if platform.system() != "Windows":
            # Set directory to read-only
            token_file.parent.chmod(0o444)
            try:
                with patch(
                    "ansys.hps.client.common.token_storage.platform.system", return_value="Linux"
                ):
                    with pytest.raises(PermissionError):
                        save_tokens(sample_tokens, sample_hps_url, storage="disk")
            finally:
                token_file.parent.chmod(0o755)

    def test_save_tokens_disk_creates_parent_directories(
        self, sample_tokens, sample_hps_url, tmp_path, monkeypatch
    ):
        """save_tokens to disk creates parent directories if they don't exist."""
        deep_path = tmp_path / "deeply" / "nested" / "path" / ".ansys" / "hps_tokens.json"
        monkeypatch.setattr("ansys.hps.client.common.token_storage.TOKEN_FILE", deep_path)

        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Linux"):
            result = save_tokens(sample_tokens, sample_hps_url, storage="disk")

        assert result == deep_path
        assert deep_path.exists()

    def test_save_tokens_missing_access_token_empty_string(self, sample_hps_url):
        """save_tokens raises ValueError for empty access_token."""
        tokens = {"access_token": "", "refresh_token": "token"}
        with pytest.raises(ValueError, match="access_token"):
            save_tokens(tokens, sample_hps_url, storage="memory")

    def test_save_tokens_missing_access_token_completely(self, sample_hps_url):
        """save_tokens raises ValueError when access_token key is missing."""
        tokens = {"refresh_token": "token"}
        with pytest.raises(ValueError, match="Invalid token payload"):
            save_tokens(tokens, sample_hps_url, storage="memory")

    def test_save_tokens_extra_fields_accepted(self, sample_tokens, sample_hps_url):
        """save_tokens accepts and ignores extra fields in tokens dict."""
        tokens = sample_tokens.copy()
        tokens["extra_field"] = "value"
        tokens["another_extra"] = {"nested": "data"}

        # Should not raise
        result = save_tokens(tokens, sample_hps_url, storage="memory")
        assert result is None


# ============================================================================
# Load Tokens Edge Cases Tests
# ============================================================================


class TestLoadTokensEdgeCases:
    """Tests for edge cases in load_tokens() function."""

    def test_load_tokens_corrupted_json_with_partial_data(self, tmp_path, monkeypatch):
        """load_tokens handles JSON file with partial/corrupt data."""
        token_file = tmp_path / ".ansys" / "hps_tokens.json"
        token_file.parent.mkdir(parents=True, exist_ok=True)
        # Write truncated JSON
        token_file.write_bytes(b'{"hps_url": "https://example.com", "refresh_token": "t')

        monkeypatch.setattr("ansys.hps.client.common.token_storage.TOKEN_FILE", token_file)
        result = _load_from_disk()
        assert result is None

    def test_load_tokens_invalid_json_with_comments(self, tmp_path, monkeypatch):
        """load_tokens handles JSON file with comments (invalid JSON)."""
        token_file = tmp_path / ".ansys" / "hps_tokens.json"
        token_file.parent.mkdir(parents=True, exist_ok=True)
        # JSON with comments is not valid
        token_file.write_text('{"refresh_token": "token"} // comment', encoding="utf-8")

        monkeypatch.setattr("ansys.hps.client.common.token_storage.TOKEN_FILE", token_file)
        result = _load_from_disk()
        assert result is None

    def test_load_tokens_memory_mode_always_returns_none(self):
        """load_tokens with storage='memory' always returns None."""
        with patch("ansys.hps.client.common.token_storage._load_from_keyring") as mock_keyring:
            with patch("ansys.hps.client.common.token_storage._load_from_disk") as mock_disk:
                mock_keyring.return_value = {"tokens": "data"}
                mock_disk.return_value = {"tokens": "data"}

                result = load_tokens(storage="memory")

                assert result is None
                mock_keyring.assert_not_called()
                mock_disk.assert_not_called()

    def test_load_tokens_empty_json_file(self, tmp_path, monkeypatch):
        """load_tokens handles empty JSON file."""
        token_file = tmp_path / ".ansys" / "hps_tokens.json"
        token_file.parent.mkdir(parents=True, exist_ok=True)
        token_file.write_text("{}", encoding="utf-8")

        monkeypatch.setattr("ansys.hps.client.common.token_storage.TOKEN_FILE", token_file)
        result = _load_from_disk()
        assert result is None  # Missing required refresh_token

    def test_load_tokens_dpapi_encrypted_corrupted(self, tmp_path, monkeypatch):
        """load_tokens handles corrupted DPAPI-encrypted file."""
        if platform.system() != "Windows":
            pytest.skip("DPAPI test requires Windows")

        token_file = tmp_path / ".ansys" / "hps_tokens.json"
        token_file.parent.mkdir(parents=True, exist_ok=True)
        # Write invalid DPAPI data
        token_file.write_bytes(b"DPAPI:invalid_base64_data!!!")

        monkeypatch.setattr("ansys.hps.client.common.token_storage.TOKEN_FILE", token_file)

        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Windows"):
            result = _load_from_disk()
            assert result is None


# ============================================================================
# Atomic Write Edge Cases Tests
# ============================================================================


class TestAtomicWriteBytesEdgeCases:
    """Tests for edge cases in _atomic_write_bytes() function."""

    def test_atomic_write_overwrites_existing_file(self, tmp_path):
        """atomic_write_bytes overwrites existing file atomically."""
        target = tmp_path / "existing_file.txt"
        target.write_bytes(b"old data")

        new_data = b"new data"
        _atomic_write_bytes(target, new_data)

        assert target.read_bytes() == new_data

    def test_atomic_write_sets_file_permissions_unix(self, tmp_path):
        """atomic_write_bytes sets correct file permissions on Unix."""
        if platform.system() == "Windows":
            pytest.skip("Unix-specific test")

        target = tmp_path / "secure_file.txt"
        data = b"secret data"

        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Linux"):
            _atomic_write_bytes(target, data, mode=0o600)

        mode = target.stat().st_mode & 0o777
        assert mode == 0o600

    def test_atomic_write_large_file(self, tmp_path):
        """atomic_write_bytes handles large files correctly."""
        target = tmp_path / "large_file.bin"
        large_data = b"x" * (1024 * 1024)  # 1MB

        _atomic_write_bytes(target, large_data)

        assert target.read_bytes() == large_data

    def test_atomic_write_empty_data(self, tmp_path):
        """atomic_write_bytes handles empty data correctly."""
        target = tmp_path / "empty_file.txt"

        _atomic_write_bytes(target, b"")

        assert target.exists()
        assert target.read_bytes() == b""

    def test_atomic_write_binary_data_with_nulls(self, tmp_path):
        """atomic_write_bytes handles binary data with null bytes."""
        target = tmp_path / "binary_file.bin"
        data = b"\x00\x01\x02\x03\xff\xfe\xfd\xfc"

        _atomic_write_bytes(target, data)

        assert target.read_bytes() == data

    def test_atomic_write_cleans_up_temp_file_on_error(self, tmp_path):
        """atomic_write_bytes cleans up temporary file if write fails."""
        target = tmp_path / "target.txt"

        # Mock os.replace to fail

        def mock_replace_error(*args, **kwargs):
            raise OSError("Simulated failure")

        with patch("os.replace", side_effect=mock_replace_error):
            with pytest.raises(OSError, match="Simulated failure"):
                _atomic_write_bytes(target, b"data")

        # Check that no .tmp files are left behind
        tmp_files = list(tmp_path.glob(".*tmp*"))
        assert len(tmp_files) == 0

    def test_atomic_write_handles_directory_fsync_failure(self, tmp_path):
        """atomic_write_bytes gracefully handles directory fsync failures."""
        target = tmp_path / "file.txt"

        # Mock os.open for directory to fail
        original_open = os.open
        call_count = [0]

        def mock_open(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 2 and args and args[0] == target.parent:  # Directory open
                raise OSError("Cannot open directory")
            return original_open(*args, **kwargs)

        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Linux"):
            with patch("os.open", side_effect=mock_open):
                # Should complete without raising despite directory fsync failure
                _atomic_write_bytes(target, b"data", mode=0o600)

        assert target.exists()
        assert target.read_bytes() == b"data"


# ============================================================================
# Integration-like Tests
# ============================================================================


class TestSaveAndLoadIntegration:
    """Integration tests for save and load with various edge cases."""

    def test_save_and_load_with_special_characters(self, sample_hps_url, tmp_path, monkeypatch):
        """Save and load tokens with special characters and unicode."""
        if platform.system() == "Windows":
            pytest.skip("Non-DPAPI test")

        tokens = {
            "access_token": "token_with_special_chars_emoji",
            "refresh_token": "refresh_token_with_special_chars",
            "expires_in": 3600,
            "refresh_expires_in": 86400,
        }

        token_file = tmp_path / ".ansys" / "hps_tokens.json"
        monkeypatch.setattr("ansys.hps.client.common.token_storage.TOKEN_FILE", token_file)

        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Linux"):
            save_tokens(tokens, sample_hps_url, storage="disk")
            loaded = _load_from_disk()

        assert loaded is not None
        assert loaded["hps_url"] == sample_hps_url

    def test_save_and_load_with_very_long_tokens(self, sample_hps_url, tmp_path, monkeypatch):
        """Save and load tokens with very long token strings."""
        if platform.system() == "Windows":
            pytest.skip("Non-DPAPI test")

        tokens = {
            "access_token": "a" * 5000,  # Very long token
            "refresh_token": "r" * 3000,
            "expires_in": 3600,
        }

        token_file = tmp_path / ".ansys" / "hps_tokens.json"
        monkeypatch.setattr("ansys.hps.client.common.token_storage.TOKEN_FILE", token_file)

        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Linux"):
            save_tokens(tokens, sample_hps_url, storage="disk")
            loaded = _load_from_disk()

        assert loaded is not None
        assert loaded["hps_url"] == sample_hps_url

    def test_load_tokens_multiple_calls_consistency(
        self, sample_tokens, sample_hps_url, tmp_path, monkeypatch
    ):
        """Multiple load_tokens calls return consistent data."""
        if platform.system() == "Windows":
            pytest.skip("Non-DPAPI test")

        token_file = tmp_path / ".ansys" / "hps_tokens.json"
        monkeypatch.setattr("ansys.hps.client.common.token_storage.TOKEN_FILE", token_file)

        with patch("ansys.hps.client.common.token_storage.platform.system", return_value="Linux"):
            save_tokens(sample_tokens, sample_hps_url, storage="disk")

        # Load multiple times
        loaded1 = load_tokens(storage="disk")
        loaded2 = load_tokens(storage="disk")
        loaded3 = load_tokens(storage="disk")

        assert loaded1 == loaded2
        assert loaded2 == loaded3
        assert loaded1["hps_url"] == sample_hps_url
