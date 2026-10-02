"""Cross-OS path conflict helpers for ProSync profile handoffs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Iterable
import re
import unicodedata


_SEPARATOR_RE = re.compile(r"/+")
_REDUNDANT_SEP_RE = re.compile(r"/{2,}")


@dataclass(frozen=True)
class CrossOsPathConflict:
    """A set of labels that collapse to the same portable path key."""

    key: str
    paths: tuple[str, ...]
    reasons: tuple[str, ...]


def portable_path_key(path: str, *, case_sensitive: bool = False) -> str:
    """Return a comparison key for cross-platform path handoffs.

    The key is deliberately conservative: it normalizes Unicode to NFC, treats
    backslashes as separators, collapses repeated separators, removes redundant
    ``.`` segments, strips trailing slashes, and case-folds by default. It does
    not resolve symlinks, environment variables, drives, or real filesystem
    targets.
    """

    if path is None:
        path = ""
    value = unicodedata.normalize("NFC", str(path).strip())
    if not value:
        return ""
    value = value.replace("\\", "/")
    value = _SEPARATOR_RE.sub("/", value)
    value = str(PurePosixPath(value))
    if value != "/" and value.endswith("/"):
        value = value.rstrip("/")
    if not case_sensitive:
        value = value.casefold()
    return value


def describe_path_normalization(path: str) -> tuple[str, ...]:
    """Return human-readable reasons why a path label changes for portability."""

    original = "" if path is None else str(path)
    normalized_unicode = unicodedata.normalize("NFC", original)
    normalized_key = portable_path_key(original)
    reasons: list[str] = []

    if "\\" in original:
        reasons.append("separator")
    if original != normalized_unicode:
        reasons.append("unicode-nfc")
    if original.casefold() != original:
        reasons.append("case")

    clean_slashes = original.strip().replace("\\", "/")
    has_redundant_segments = (
        original.strip() != original
        or _REDUNDANT_SEP_RE.search(clean_slashes) is not None
        or (clean_slashes.endswith("/") and clean_slashes != "/")
        or (clean_slashes != "" and str(PurePosixPath(clean_slashes)) != clean_slashes.rstrip("/"))
    )
    if has_redundant_segments:
        reasons.append("redundant-segments")

    if normalized_key != portable_path_key(original, case_sensitive=True):
        reasons.append("case-insensitive-key")

    return tuple(dict.fromkeys(reasons))


def find_cross_os_path_conflicts(
    paths: Iterable[str],
    *,
    case_sensitive: bool = False,
) -> list[CrossOsPathConflict]:
    """Find path labels that should be treated as conflicts across OSes."""

    grouped: dict[str, list[str]] = {}
    reasons_by_key: dict[str, list[str]] = {}

    for raw_path in paths:
        key = portable_path_key(raw_path, case_sensitive=case_sensitive)
        grouped.setdefault(key, []).append(str(raw_path))
        reasons_by_key.setdefault(key, []).extend(describe_path_normalization(str(raw_path)))

    conflicts: list[CrossOsPathConflict] = []
    for key, originals in grouped.items():
        unique_originals = tuple(dict.fromkeys(originals))
        if len(unique_originals) < 2:
            continue
        reasons = tuple(dict.fromkeys(reasons_by_key.get(key, ()))) or ("same-portable-key",)
        conflicts.append(CrossOsPathConflict(key=key, paths=unique_originals, reasons=reasons))

    return sorted(conflicts, key=lambda item: item.key)
