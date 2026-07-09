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

"""Typed models for monitor REST and WebSocket payloads."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import Any


class _PayloadMappingMixin:
    """Mixin for consistent __hash__ and __eq__ on Mapping-based dataclasses.

    Requires a `payload: dict[str, Any]` attribute.
    """

    payload: dict[str, Any]

    def __hash__(self) -> int:
        """Return hash of the response based on payload contents."""
        try:
            return hash(frozenset(self.payload.items()))
        except TypeError:
            # Fallback if payload contains unhashable values
            return hash(id(self))

    def __eq__(self, other: object) -> bool:
        """Check equality with another mapping-like object."""
        if isinstance(other, Mapping):
            return self.payload == dict(other)
        return False


@dataclass(frozen=True)
class ListTagsCommand:
    """Typed model for the monitor WebSocket ``list_tags`` command."""

    limit: int = 1000

    def to_payload(self) -> dict[str, Any]:
        """Serialize the command to a WebSocket payload dict."""
        return {
            "type": "command",
            "action": "list_tags",
            "limit": self.limit,
        }


@dataclass(frozen=True)
class SubscribeCommand:
    """Typed model for the monitor WebSocket ``subscribe`` command."""

    topics: list[dict[str, str]]
    backlog_limit: int = 100

    def to_payload(self) -> dict[str, Any]:
        """Serialize the command to a WebSocket payload dict."""
        return {
            "type": "command",
            "action": "subscribe",
            "topics": self.topics,
            "backlog": {"limit": self.backlog_limit},
        }


@dataclass(frozen=True)
class ListTagsResponse:
    """Typed model for the monitor ``list_tags`` response payload."""

    tag_list: dict[str, list[str]]

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> ListTagsResponse:
        """Construct a ``ListTagsResponse`` from a raw WebSocket payload."""
        raw_tags = payload.get("tag_list", payload.get("tags", {}))
        if not isinstance(raw_tags, Mapping):
            return cls(tag_list={})

        normalized: dict[str, list[str]] = {}
        for key, values in raw_tags.items():
            if not isinstance(key, str):
                continue
            if not isinstance(values, list):
                continue
            normalized[key] = [str(value) for value in values]

        return cls(tag_list=normalized)


@dataclass(frozen=True, unsafe_hash=True, eq=False)
class MonitorMessage(_PayloadMappingMixin, Mapping[str, Any]):
    """Typed wrapper around a single monitor message payload."""

    payload: dict[str, Any]

    def __getitem__(self, key: str) -> Any:
        """Get a value from the message payload."""
        return self.payload[key]

    def __iter__(self) -> Iterator[str]:
        """Iterate over message payload keys."""
        return iter(self.payload)

    def __len__(self) -> int:
        """Return the number of payload keys."""
        return len(self.payload)

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying payload."""
        return dict(self.payload)


@dataclass(frozen=True)
class MessageEnvelope:
    """Typed model for normalizing monitor WebSocket message payloads."""

    messages: list[MonitorMessage]

    @classmethod
    def from_payload(cls, payload: Any) -> MessageEnvelope:
        """Normalize payload into a list of typed message wrappers."""
        if isinstance(payload, Mapping) and isinstance(payload.get("messages"), list):
            raw_messages = payload["messages"]
        elif isinstance(payload, list):
            raw_messages = payload
        else:
            raw_messages = [payload]

        normalized = [MonitorMessage(payload=msg) for msg in raw_messages if isinstance(msg, dict)]
        return cls(messages=normalized)


@dataclass(frozen=True, unsafe_hash=True, eq=False)
class BuildInfoResponse(_PayloadMappingMixin, Mapping[str, Any]):
    """Typed wrapper for monitor build-info responses."""

    payload: dict[str, Any]

    def __getitem__(self, key: str) -> Any:
        """Get a value from the build-info response."""
        return self.payload[key]

    def __iter__(self) -> Iterator[str]:
        """Iterate over response payload keys."""
        return iter(self.payload)

    def __len__(self) -> int:
        """Return the number of payload keys."""
        return len(self.payload)

    @property
    def build(self) -> Mapping[str, Any] | None:
        """Return the nested ``build`` object if present."""
        data = self.payload.get("build")
        return data if isinstance(data, Mapping) else None


