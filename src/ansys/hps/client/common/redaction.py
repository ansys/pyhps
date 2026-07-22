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
