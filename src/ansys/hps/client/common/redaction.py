# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT

"""Internal utilities for redacting sensitive values from logs and telemetry."""

import re

REDACTED = "***REDACTED***"


def redact_sensitive_values(text: str, tokens: dict | None = None) -> str:
    """Redact sensitive token-like values from logs and telemetry strings."""
    redacted = text

    # Redact explicit token values when available.
    if tokens:
        for key in ("access_token", "refresh_token"):
            value = tokens.get(key)
            if value:
                redacted = redacted.replace(str(value), REDACTED)

    # Redact bearer credentials and JWT-like payloads defensively.
    redacted = re.sub(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*", f"Bearer {REDACTED}", redacted)
    redacted = re.sub(
        r"\beyJ[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]*\b",
        REDACTED,
        redacted,
    )

    return redacted
