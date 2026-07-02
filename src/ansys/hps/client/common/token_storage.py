# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT

"""Shared token persistence helpers for auth workflows.

These utilities are storage-backend oriented and can be used by OIDC or
other authentication flows that need token load/save behavior.

Disk token path:
- Windows: `%USERPROFILE%\\.ansys\\hps_tokens.json`
- Unix/Linux: `~/.ansys/hps_tokens.json`
"""

import base64
import json
import logging
import os
import platform
import secrets
import time
import uuid
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .redaction import redact_sensitive_values

TOKEN_FILE = Path.home() / ".ansys" / "hps_tokens.json"
DEFAULT_KEYRING_SERVICE_NAME = "ansys-hps"
KEYRING_SERVICE_ENV_VAR = "HPS_OIDC_KEYRING_SERVICE_NAME"

log = logging.getLogger(__name__)


class _TokensForSave(BaseModel):
    """Internal schema for validating tokens before persistence."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    access_token: str = Field(min_length=1)
    refresh_token: str | None = None
    expires_in: int | None = None
    refresh_expires_in: int | None = None


class _LoadedTokens(_TokensForSave):
    """Internal schema for validating loaded token payloads."""

    hps_url: str | None = None
    saved_at: float = Field(default_factory=time.time)


def _normalize_tokens_for_save(tokens: dict) -> dict:
    """Validate and normalize token payload before persistence."""
    try:
        normalized = _TokensForSave.model_validate(tokens)
    except ValidationError as ex:
        raise ValueError(f"Invalid token payload for save: {ex}") from ex

    return normalized.model_dump()


def _normalize_loaded_tokens(tokens: dict) -> dict:
    """Validate and normalize loaded token payload before returning to callers."""
    payload = dict(tokens)
    payload["expires_in"] = payload.get("expires_in", 3600)
    payload["refresh_expires_in"] = payload.get("refresh_expires_in", 86400)
    payload["saved_at"] = payload.get("saved_at", time.time())

    try:
        normalized = _LoadedTokens.model_validate(payload)
    except ValidationError as ex:
        raise ValueError(f"Invalid loaded token payload: {ex}") from ex

    return normalized.model_dump()


def _resolve_keyring_service_name(service_name: str | None = None) -> str:
    """Resolve keyring service name from argument, env var, or default."""
    resolved = service_name or os.environ.get(KEYRING_SERVICE_ENV_VAR) or DEFAULT_KEYRING_SERVICE_NAME
    resolved = str(resolved).strip()
    if not resolved:
        raise ValueError("Keyring service name cannot be empty.")
    return resolved


def _encrypt_with_dpapi(data: bytes) -> bytes:
    """Encrypt data using Windows DPAPI (user-scoped).

    Windows-only function. Will raise RuntimeError if called on other platforms.
    """
    if platform.system() != "Windows":
        raise RuntimeError("DPAPI encryption is only available on Windows")

    import ctypes
    import ctypes.wintypes as wintypes

    LocalFree = ctypes.windll.kernel32.LocalFree
    CryptProtectData = ctypes.windll.Crypt32.CryptProtectData

    class DataBlob(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(wintypes.BYTE))]

    def dpapi_encrypt(plaintext: bytes) -> bytes:
        plaintext_buffer = ctypes.create_string_buffer(plaintext, len(plaintext))
        plaintext_blob = DataBlob(
            len(plaintext),
            ctypes.cast(plaintext_buffer, ctypes.POINTER(wintypes.BYTE)),
        )
        ciphertext_blob = DataBlob()
        # CRYPTPROTECT_UI_FORBIDDEN = 0x1
        flags = 0x1
        result = CryptProtectData(
            ctypes.byref(plaintext_blob),
            None,
            None,
            None,
            None,
            flags,
            ctypes.byref(ciphertext_blob),
        )
        if not result:
            raise RuntimeError("Failed to encrypt data with DPAPI")
        ciphertext = bytes(ciphertext_blob.pbData[: ciphertext_blob.cbData])
        LocalFree(ciphertext_blob.pbData)
        return ciphertext

    return dpapi_encrypt(data)


def _decrypt_with_dpapi(ciphertext: bytes) -> bytes:
    """Decrypt data using Windows DPAPI.

    Windows-only function. Will raise RuntimeError if called on other platforms.
    """
    if platform.system() != "Windows":
        raise RuntimeError("DPAPI decryption is only available on Windows")

    import ctypes
    import ctypes.wintypes as wintypes

    LocalFree = ctypes.windll.kernel32.LocalFree
    CryptUnprotectData = ctypes.windll.Crypt32.CryptUnprotectData

    class DataBlob(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(wintypes.BYTE))]

    def dpapi_decrypt(ciphertext: bytes) -> bytes:
        ciphertext_buffer = ctypes.create_string_buffer(ciphertext, len(ciphertext))
        ciphertext_blob = DataBlob(
            len(ciphertext),
            ctypes.cast(ciphertext_buffer, ctypes.POINTER(wintypes.BYTE)),
        )
        plaintext_blob = DataBlob()
        flags = 0x1
        result = CryptUnprotectData(
            ctypes.byref(ciphertext_blob),
            None,
            None,
            None,
            None,
            flags,
            ctypes.byref(plaintext_blob),
        )
        if not result:
            raise RuntimeError("Failed to decrypt data with DPAPI")
        plaintext = bytes(plaintext_blob.pbData[: plaintext_blob.cbData])
        LocalFree(plaintext_blob.pbData)
        return plaintext

    return dpapi_decrypt(ciphertext)


def _save_to_keyring(tokens: dict, hps_url: str, service_name: str | None = None) -> bool:
    """Save tokens to system keyring using keyring library.

    The keyring namespace is selected by service_name or
    HPS_OIDC_KEYRING_SERVICE_NAME (falling back to ansys-hps).

    Returns True if successful, False if keyring is not available.
    """
    try:
        import keyring
    except ImportError:
        return False

    service_name = _resolve_keyring_service_name(service_name)
    try:
        keyring.set_password(service_name, "hps_url", hps_url)
        keyring.set_password(service_name, "access_token", tokens["access_token"])
        if tokens.get("refresh_token"):
            keyring.set_password(service_name, "refresh_token", tokens["refresh_token"])
        if tokens.get("expires_in") is not None:
            keyring.set_password(service_name, "expires_in", str(tokens["expires_in"]))
        if tokens.get("refresh_expires_in") is not None:
            keyring.set_password(service_name, "refresh_expires_in", str(tokens["refresh_expires_in"]))
        keyring.set_password(service_name, "saved_at", str(time.time()))
        return True
    except Exception as ex:
        safe_error = redact_sensitive_values(str(ex), tokens)
        log.warning("Failed to save tokens to keyring: %s", safe_error)
        return False


def _load_from_keyring(service_name: str | None = None) -> dict | None:
    """Load tokens from system keyring.

    The keyring namespace is selected by service_name or
    HPS_OIDC_KEYRING_SERVICE_NAME (falling back to ansys-hps).

    Returns token dict if available, None if keyring unavailable or no tokens saved.
    """
    try:
        import keyring
    except ImportError:
        return None

    service_name = _resolve_keyring_service_name(service_name)
    try:
        access_token = keyring.get_password(service_name, "access_token")
        if not access_token:
            return None

        raw_tokens = {
            "hps_url": keyring.get_password(service_name, "hps_url"),
            "access_token": access_token,
            "refresh_token": keyring.get_password(service_name, "refresh_token"),
            "expires_in": keyring.get_password(service_name, "expires_in"),
            "refresh_expires_in": keyring.get_password(service_name, "refresh_expires_in"),
            "saved_at": keyring.get_password(service_name, "saved_at"),
        }
        return _normalize_loaded_tokens(raw_tokens)
    except Exception:
        return None


def _load_from_disk() -> dict | None:
    """Load tokens from disk file.

    Returns token dict if available, None if file doesn't exist or can't be read.
    """
    if not TOKEN_FILE.exists():
        return None

    try:
        content = TOKEN_FILE.read_bytes()
        # Check if encrypted with DPAPI
        if content.startswith(b"DPAPI:"):
            encrypted = base64.b64decode(content[6:])
            json_data = _decrypt_with_dpapi(encrypted)
            raw_tokens = json.loads(json_data.decode("utf-8"))
        else:
            raw_tokens = json.loads(content.decode("utf-8"))

        return _normalize_loaded_tokens(raw_tokens)
    except Exception as ex:
        safe_error = redact_sensitive_values(str(ex))
        log.warning("Failed to load tokens from disk: %s", safe_error)
        return None


def load_tokens(storage: str = "keyring", service_name: str | None = None) -> dict | None:
    """Load saved tokens from the explicitly selected backend.

    Parameters
    ----------
    storage:
        Backend to load from. Supported values are ``"memory"``, ``"disk"``,
        and ``"keyring"``.
    service_name:
        Keyring service name override. Used only when ``storage="keyring"``.

    Returns
    -------
    dict | None
        Loaded token payload when present, otherwise ``None``.
    """
    if storage not in ("memory", "disk", "keyring"):
        raise ValueError(
            f"Invalid storage method: {storage}. Must be 'memory', 'disk', or 'keyring'"
        )

    if storage == "memory":
        return None

    if storage == "disk":
        return _load_from_disk()

    resolved_service_name = _resolve_keyring_service_name(service_name)
    return _load_from_keyring(service_name=resolved_service_name)


def _check_keyring_backend() -> str | None:
    """Return error details if keyring backend is unavailable, else None."""
    try:
        import keyring
    except ImportError:
        return "python package 'keyring' is not installed"

    probe_service = "ansys-hps-token-storage-probe"
    probe_user = f"probe-{os.getpid()}-{secrets.token_hex(4)}"
    try:
        keyring.set_password(probe_service, probe_user, "ok")
        keyring.delete_password(probe_service, probe_user)
    except Exception as ex:
        return str(ex)
    return None


def _check_disk_storage_backend() -> str | None:
    """Return error details if disk storage backend is unavailable, else None."""
    try:
        token_dir = TOKEN_FILE.parent
        token_dir.mkdir(parents=True, exist_ok=True)
        probe = token_dir / f".hps_storage_probe_{uuid.uuid4().hex}"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except Exception as ex:
        return str(ex)
    return None


def _check_storage_backend(storage: str) -> str | None:
    """Return error details if storage backend is unavailable, else None."""
    if storage == "memory":
        return None
    if storage == "disk":
        return _check_disk_storage_backend()
    if storage == "keyring":
        return _check_keyring_backend()
    raise ValueError(f"Invalid storage method: {storage}. Must be 'memory', 'disk', or 'keyring'")


def _is_token_expired(tokens: dict, buffer_seconds: int = 60) -> bool:
    """Check if access token is expired or close to expiry."""
    if "expires_in" not in tokens or "saved_at" not in tokens:
        return True

    elapsed = time.time() - tokens["saved_at"]
    expires_in = tokens["expires_in"]
    return elapsed > (expires_in - buffer_seconds)



def _atomic_write_bytes(path: Path, data: bytes, mode: int | None = None) -> None:
    """Write bytes to disk atomically using a same-directory temporary file."""
    temp_path = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temp_written = False

    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if mode is None:
            fd = os.open(temp_path, flags)
        else:
            fd = os.open(temp_path, flags, mode)

        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())

        temp_written = True
        if mode is not None and platform.system() != "Windows":
            temp_path.chmod(mode)

        os.replace(temp_path, path)

        if platform.system() != "Windows":
            try:
                dir_fd = os.open(path.parent, os.O_RDONLY)
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)
            except OSError:
                pass

        if mode is not None and platform.system() != "Windows":
            path.chmod(mode)
    finally:
        if temp_written and temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass

def save_tokens(
    tokens: dict,
    hps_url: str,
    storage: str = "memory",
    service_name: str | None = None,
) -> Path | None:
    """Persist tokens to specified storage location.

    For `storage="disk"`, tokens are written to:
    - Windows: `%USERPROFILE%\\.ansys\\hps_tokens.json` (DPAPI encrypted)
    - Unix/Linux: `~/.ansys/hps_tokens.json` (permissions set to 0o600)
    """
    if storage not in ("memory", "disk", "keyring"):
        raise ValueError(f"Invalid storage method: {storage}. Must be 'memory', 'disk', or 'keyring'")

    if not isinstance(hps_url, str) or not hps_url.strip():
        raise ValueError("'hps_url' must be a non-empty string.")

    tokens = _normalize_tokens_for_save(tokens)

    if storage == "memory":
        return None
    elif storage == "keyring":
        resolved_service_name = _resolve_keyring_service_name(service_name)
        if _save_to_keyring(tokens, hps_url, service_name=resolved_service_name):
            return None
        raise RuntimeError("Keyring storage requested but unavailable or failed to save.")

    # storage == "disk"
    # Persist tokens to disk only when explicit disk mode is requested.
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "hps_url": hps_url,
        "access_token": tokens["access_token"],
        "refresh_token": tokens.get("refresh_token"),
        "expires_in": tokens.get("expires_in"),
        "refresh_expires_in": tokens.get("refresh_expires_in"),
        "saved_at": time.time(),
    }
    json_bytes = json.dumps(payload, indent=2).encode("utf-8")

    # Platform-specific security
    if platform.system() == "Windows":
        encrypted = _encrypt_with_dpapi(json_bytes)
        _atomic_write_bytes(TOKEN_FILE, b"DPAPI:" + base64.b64encode(encrypted))
    else:
        _atomic_write_bytes(TOKEN_FILE, json_bytes, mode=0o600)

    return TOKEN_FILE











