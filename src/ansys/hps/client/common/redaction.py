# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT

"""Internal utilities for redacting sensitive values from logs and telemetry."""

import re

REDACTED = "***REDACTED***"


def _normalize_text(value: object) -> str:
    """Normalize arbitrary values into a safe string for redaction."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def redact_sensitive_values(text: object, tokens: object = None) -> str:
    """Redact sensitive token-like values from logs and telemetry strings."""
    redacted = _normalize_text(text)
    token_map = tokens if isinstance(tokens, dict) else {}

    # Redact explicit token values when available.
    if token_map:
        for key in ("access_token", "refresh_token"):
            value = token_map.get(key)
            if value:
                redacted = redacted.replace(_normalize_text(value), REDACTED)

    # Redact bearer credentials and JWT-like payloads defensively.
    redacted = re.sub(
        r"\b(Bearer)\s+[A-Za-z0-9\-._~+/]+=*",
        lambda match: f"{match.group(1)} {REDACTED}",
        redacted,
        flags=re.IGNORECASE,
    )
    redacted = re.sub(
        r"\beyJ[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]*\b",
        REDACTED,
        redacted,
    )

    return redacted
