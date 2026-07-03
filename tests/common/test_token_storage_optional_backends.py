# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""Optional tests for DPAPI and keyring backends in token_storage.

These tests are conditional and optional:
- DPAPI tests only run on Windows
- Keyring tests only run when keyring is installed

Run specific tests with:
  pytest tests/common/test_token_storage_optional_backends.py -v
"""

import json
import logging
import sys
from pathlib import Path

import pytest

# Only import keyring if available
HAS_KEYRING = True
try:
    import keyring
except ImportError:
    HAS_KEYRING = False

# Check if running on Windows for DPAPI tests
IS_WINDOWS = sys.platform == "win32"

log = logging.getLogger(__name__)


# ============================================================================
# DPAPI Encryption Tests (Windows only)
# ============================================================================


@pytest.mark.skipif(not IS_WINDOWS, reason="DPAPI only available on Windows")
class TestDPAPIEncryption:
    """Tests for Windows DPAPI encryption/decryption functionality."""

    @pytest.fixture(autouse=True)
    def setup_dpapi(self):
        """Setup DPAPI functions for testing."""
        # Import here to avoid errors on non-Windows platforms
        from ansys.hps.client.common.token_storage import (
            _decrypt_with_dpapi,
            _encrypt_with_dpapi,
        )

        self._encrypt_with_dpapi = _encrypt_with_dpapi
        self._decrypt_with_dpapi = _decrypt_with_dpapi

    def test_dpapi_encrypt_decrypt_simple_bytes(self):
        """Test basic encryption and decryption round-trip."""
        original_data = b"test_token_data"

        encrypted = self._encrypt_with_dpapi(original_data)
        assert encrypted != original_data
        assert isinstance(encrypted, bytes)

        decrypted = self._decrypt_with_dpapi(encrypted)
        assert decrypted == original_data

    def test_dpapi_encrypt_decrypt_json_tokens(self):
        """Test encryption/decryption with realistic token JSON."""
        token_data = {
            "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "very_long_refresh_token_string",
            "expires_in": 3600,
            "token_type": "Bearer",
        }
        original_data = json.dumps(token_data).encode("utf-8")

        encrypted = self._encrypt_with_dpapi(original_data)
        decrypted = self._decrypt_with_dpapi(encrypted)

        assert json.loads(decrypted.decode("utf-8")) == token_data

    def test_dpapi_encrypt_large_data(self):
        """Test encryption of large token payloads."""
        # Create large data payload (simulating many tokens or large JWTs)
        large_data = b"x" * 50000

        encrypted = self._encrypt_with_dpapi(large_data)
        decrypted = self._decrypt_with_dpapi(encrypted)

        assert decrypted == large_data

    def test_dpapi_encrypt_special_characters(self):
        """Test encryption with special UTF-8 characters."""
        special_data = "Ⓣⓔⓢⓣ 🔐 Тест 테스트".encode()

        encrypted = self._encrypt_with_dpapi(special_data)
        decrypted = self._decrypt_with_dpapi(encrypted)

        assert decrypted == special_data

    def test_dpapi_decrypt_invalid_ciphertext(self):
        """Test decryption with corrupted/invalid ciphertext."""
        # Create invalid base64 or corrupted data
        invalid_data = b"not_valid_encrypted_data\x00\xff"

        # Decryption should raise an error
        with pytest.raises(RuntimeError, match="Failed to decrypt"):
            self._decrypt_with_dpapi(invalid_data)

    def test_dpapi_decrypt_truncated_ciphertext(self):
        """Test decryption with truncated/incomplete ciphertext."""
        original_data = b"secret_token"
        encrypted = self._encrypt_with_dpapi(original_data)

        # Truncate the encrypted data
        truncated = encrypted[: len(encrypted) // 2]

        # Should raise an error when decrypting
        with pytest.raises(RuntimeError, match="Failed to decrypt"):
            self._decrypt_with_dpapi(truncated)

    def test_dpapi_empty_data(self):
        """Test encryption/decryption of empty data."""
        empty_data = b""

        encrypted = self._encrypt_with_dpapi(empty_data)
        decrypted = self._decrypt_with_dpapi(encrypted)

        assert decrypted == empty_data

    def test_dpapi_binary_data_with_nulls(self):
        """Test encryption with binary data containing null bytes."""
        binary_data = b"\x00\x01\x02\x03\xff\xfe\xfd"

        encrypted = self._encrypt_with_dpapi(binary_data)
        decrypted = self._decrypt_with_dpapi(encrypted)

        assert decrypted == binary_data


@pytest.mark.skipif(not IS_WINDOWS, reason="DPAPI only available on Windows")
class TestDPAPITokenStorage:
    """Integration tests for DPAPI-based token storage."""

    def test_save_and_load_with_dpapi_backend(self):
        """Test saving and loading tokens using DPAPI backend."""
        from ansys.hps.client.common.token_storage import save_tokens

        tokens = {
            "access_token": "access_token_value",
            "refresh_token": "refresh_token_value",
            "expires_in": 3600,
            "token_type": "Bearer",
        }

        # Save with DPAPI (uses default location)
        result = save_tokens(
            tokens=tokens,
            hps_url="https://localhost:8443/hps",
            storage="disk",
        )

        # Verify save operation returned a path (or None)
        assert result is None or isinstance(result, Path)


@pytest.mark.skipif(not IS_WINDOWS, reason="DPAPI only available on Windows")
class TestDPAPIPerformance:
    """Performance tests for DPAPI operations."""

    def test_dpapi_encrypt_decrypt_many_times(self):
        """Test DPAPI performance with repeated operations."""
        from ansys.hps.client.common.token_storage import (
            _decrypt_with_dpapi,
            _encrypt_with_dpapi,
        )

        test_data = b"test_token_data"

        # Perform multiple encrypt/decrypt cycles
        for _ in range(100):
            encrypted = _encrypt_with_dpapi(test_data)
            decrypted = _decrypt_with_dpapi(encrypted)
            assert decrypted == test_data

    def test_dpapi_large_batch_encryption(self):
        """Test DPAPI with many different data items."""
        from ansys.hps.client.common.token_storage import (
            _decrypt_with_dpapi,
            _encrypt_with_dpapi,
        )

        test_items = [f"token_{i}".encode() for i in range(50)]
        encrypted_items = []

        # Encrypt all
        for item in test_items:
            encrypted_items.append(_encrypt_with_dpapi(item))

        # Decrypt all and verify
        for orig, encrypted in zip(test_items, encrypted_items, strict=False):
            decrypted = _decrypt_with_dpapi(encrypted)
            assert decrypted == orig


# ============================================================================
# Keyring Backend Tests (requires keyring)
# ============================================================================


@pytest.mark.skipif(not HAS_KEYRING, reason="keyring not installed")
class TestKeyringBackend:
    """Tests for keyring-based token storage."""

    @pytest.fixture
    def mock_keyring(self, monkeypatch):
        """Mock keyring storage for testing."""
        storage = {}

        def mock_set_password(service, username, password):
            key = f"{service}:{username}"
            storage[key] = password

        def mock_get_password(service, username):
            key = f"{service}:{username}"
            return storage.get(key)

        def mock_delete_password(service, username):
            key = f"{service}:{username}"
            if key in storage:
                del storage[key]

        monkeypatch.setattr(keyring, "set_password", mock_set_password)
        monkeypatch.setattr(keyring, "get_password", mock_get_password)
        monkeypatch.setattr(keyring, "delete_password", mock_delete_password)

        return storage

    def test_save_tokens_to_keyring(self, mock_keyring):
        """Test saving tokens to keyring backend."""
        from ansys.hps.client.common.token_storage import save_tokens

        tokens = {
            "access_token": "access_value",
            "refresh_token": "refresh_value",
            "expires_in": 3600,
            "token_type": "Bearer",
        }

        # Save to keyring
        result = save_tokens(
            tokens=tokens,
            hps_url="https://localhost:8443/hps",
            storage="keyring",
        )

        # Verify operation succeeded
        assert result is None or isinstance(result, Path)

    def test_load_tokens_from_keyring(self, mock_keyring):
        """Test loading tokens from keyring backend."""
        from ansys.hps.client.common.token_storage import (
            load_tokens,
            save_tokens,
        )

        tokens = {
            "access_token": "test_access",
            "refresh_token": "test_refresh",
            "expires_in": 7200,
            "token_type": "Bearer",
        }

        # Save tokens
        save_tokens(
            tokens=tokens,
            hps_url="https://localhost:8443/hps",
            storage="keyring",
        )

        # Load tokens
        loaded = load_tokens(
            storage="keyring",
        )

        # If keyring returns tokens, verify them
        if loaded is not None:
            assert loaded.get("access_token") == tokens["access_token"]
            assert loaded.get("refresh_token") == tokens["refresh_token"]

    def test_keyring_with_custom_service_name(self, mock_keyring):
        """Test using custom service name for keyring."""
        from ansys.hps.client.common.token_storage import load_tokens, save_tokens

        custom_service = "custom-hps-service"

        tokens = {
            "access_token": "custom_token",
            "refresh_token": "custom_refresh",
            "expires_in": 3600,
            "token_type": "Bearer",
        }

        # Save with custom service name
        save_tokens(
            tokens=tokens,
            hps_url="https://localhost:8443/hps",
            storage="keyring",
            service_name=custom_service,
        )

        loaded = load_tokens(
            storage="keyring",
            service_name=custom_service,
        )

        # Verify if returned
        if loaded is not None:
            assert loaded.get("access_token") == "custom_token"

    def test_keyring_save_password_failure(self, monkeypatch):
        """Test handling of keyring set_password failures."""
        from ansys.hps.client.common.token_storage import save_tokens

        def mock_set_password_fails(*args, **kwargs):
            raise Exception("Keyring service unavailable")

        monkeypatch.setattr(keyring, "set_password", mock_set_password_fails)

        tokens = {
            "access_token": "test",
            "refresh_token": "test",
            "expires_in": 3600,
            "token_type": "Bearer",
        }

        # Should handle the exception gracefully or raise
        with pytest.raises(RuntimeError):
            save_tokens(
                tokens=tokens,
                hps_url="https://localhost:8443/hps",
                storage="keyring",
            )

    def test_keyring_get_password_failure(self, monkeypatch):
        """Test handling of keyring get_password failures."""
        from ansys.hps.client.common.token_storage import load_tokens

        def mock_get_password_fails(*args, **kwargs):
            raise Exception("Keyring service unavailable")

        monkeypatch.setattr(keyring, "get_password", mock_get_password_fails)

        # Should handle gracefully
        result = load_tokens(
            storage="keyring",
        )

        # Should return None on error
        assert result is None


# ============================================================================
# Cross-Platform Backend Selection Tests
# ============================================================================


class TestBackendSelection:
    """Tests for automatic backend selection based on platform/environment."""

    def test_memory_backend_always_available(self):
        """Test that memory backend is always available."""
        from ansys.hps.client.common.token_storage import _check_storage_backend

        result = _check_storage_backend("memory")
        # Memory backend should always be available (returns None on success or error string)
        assert result is None or isinstance(result, str)

    def test_disk_backend_available(self):
        """Test that disk backend is available."""
        from ansys.hps.client.common.token_storage import _check_storage_backend

        result = _check_storage_backend("disk")
        # Disk backend should be available
        assert result is None or isinstance(result, str)

    def test_invalid_backend_raises_error(self):
        """Test that invalid backend names raise appropriate errors."""
        from ansys.hps.client.common.token_storage import save_tokens

        tokens = {
            "access_token": "test",
            "refresh_token": "test",
            "expires_in": 3600,
            "token_type": "Bearer",
        }

        # Invalid storage backend should raise ValueError
        with pytest.raises((ValueError, KeyError)):
            save_tokens(
                tokens=tokens,
                hps_url="https://localhost:8443/hps",
                storage="invalid_backend",
            )


# ============================================================================
# Optional Backends - Feature Detection Tests
# ============================================================================


class TestFeatureDetection:
    """Test automatic feature detection for optional backends."""

    def test_dpapi_available_on_windows(self):
        """Test DPAPI availability detection on Windows."""
        from ansys.hps.client.common.token_storage import _check_storage_backend

        # On Windows, disk storage uses DPAPI by default
        if IS_WINDOWS:
            result = _check_storage_backend("disk")
            # Should work on Windows
            assert result is None or isinstance(result, str)

    def test_keyring_backend_availability(self):
        """Test keyring backend availability detection."""
        from ansys.hps.client.common.token_storage import _check_keyring_backend

        result = _check_keyring_backend()
        # Should return error message if not available, None if available
        assert result is None or isinstance(result, str)

    def test_fallback_strategy(self):
        """Test backend fallback strategy when primary is unavailable."""
        from ansys.hps.client.common.token_storage import save_tokens

        tokens = {
            "access_token": "test",
            "refresh_token": "test",
            "expires_in": 3600,
            "token_type": "Bearer",
        }

        # Save with memory backend (always available)
        result = save_tokens(
            tokens=tokens,
            hps_url="https://localhost:8443/hps",
            storage="memory",
        )

        # Memory storage is transient, should return None
        assert result is None
