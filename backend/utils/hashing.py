from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KeyIdHasher:
    """Internal helper for generating deterministic key IDs.

    The specific hashing primitive is intentionally encapsulated so callers
    don't depend on the algorithm details.
    """

    @staticmethod
    def digest(data: bytes) -> bytes:
        import hashlib

        return hashlib.sha256(data).digest()
