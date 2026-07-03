# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#

from ansys.hps.client.common.redaction import REDACTED, redact_sensitive_values


def test_redact_explicit_token_values():
    """Known token values are redacted when tokens mapping is provided."""
    tokens = {
        "access_token": "access-token-123",
        "refresh_token": "refresh-token-456",
    }
    text = "access=access-token-123 refresh=refresh-token-456"

    result = redact_sensitive_values(text, tokens=tokens)

    assert "access-token-123" not in result
    assert "refresh-token-456" not in result
    assert result.count(REDACTED) == 2


def test_redact_bearer_credentials_without_tokens_mapping():
    """Bearer credentials are redacted even without explicit token mapping."""
    text = "Authorization: Bearer abc.def.ghi"

    result = redact_sensitive_values(text)

    assert "abc.def.ghi" not in result
    assert f"Bearer {REDACTED}" in result


def test_redact_bearer_credentials_case_insensitive():
    """Bearer credentials are redacted regardless of bearer scheme casing."""
    text = "authorization: bearer abc.def.ghi"

    result = redact_sensitive_values(text)

    assert "abc.def.ghi" not in result
    assert f"bearer {REDACTED}" in result


def test_redact_jwt_like_payloads_defensively():
    """JWT-like values are redacted defensively from free-form text."""
    jwt_like = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signature"
    text = f"token={jwt_like}"

    result = redact_sensitive_values(text)

    assert jwt_like not in result
    assert REDACTED in result


def test_non_sensitive_text_is_unchanged():
    """Text without secrets remains unchanged."""
    text = "No credentials here"

    result = redact_sensitive_values(text)

    assert result == text


def test_redact_handles_non_string_inputs_defensively():
    """Non-string text and token values are normalized without raising errors."""
    result = redact_sensitive_values(12345, tokens={"access_token": 12345})

    assert "12345" not in result
    assert REDACTED in result


def test_redact_ignores_non_dict_tokens_mapping():
    """Non-dict tokens inputs are ignored defensively."""
    text = "Authorization: bearer abc.def.ghi"

    result = redact_sensitive_values(text, tokens=["not", "a", "dict"])

    assert "abc.def.ghi" not in result
    assert f"bearer {REDACTED}" in result
