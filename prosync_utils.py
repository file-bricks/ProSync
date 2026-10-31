"""
ProSync Utilities
Gemeinsame Hilfsfunktionen für ProSync-Komponenten
"""

import json
import os
import stat
import subprocess
import sys
import tempfile
import time
from typing import Any


def _atomic_replace_with_retry(
    tmp_path: str,
    abs_path: str,
    max_retries: int = 8,
    start_delay: float = 0.01,
) -> None:
    """
    Ersetzt eine Zieldatei atomar durch die temporäre Stage mit Windows-Resilienz.

    - Erkennt Verzeichnisse vorab und bricht mit IsADirectoryError ab.
    - Hebt unter Windows vorübergehend den Schreibschutz auf (stat.S_IWRITE),
      falls die Zieldatei bereits schreibgeschützt existiert.
    - Fängt transiente Sperren (WinError 5 / WinError 32 durch Defender, Cloud-Sync)
      über einen exponentiellen Backoff ab.
    - Stellt bei endgültigem Fehlschlag den ursprünglichen Modus der Zieldatei wieder her.
    """
    if os.path.isdir(abs_path):
        raise IsADirectoryError(f"Zieldatei ist ein Verzeichnis: {abs_path}")

    original_mode = None
    target_stat = None
    if os.path.exists(abs_path):
        try:
            target_stat = os.stat(abs_path)
            if os.name == "nt" and not (target_stat.st_mode & stat.S_IWRITE):
                original_mode = target_stat.st_mode
                os.chmod(abs_path, target_stat.st_mode | stat.S_IWRITE)
        except OSError:
            pass

    delay = start_delay
    last_error = None
    for attempt in range(max_retries):
        try:
            os.replace(tmp_path, abs_path)
            return
        except PermissionError as exc:
            last_error = exc
            if attempt == max_retries - 1:
                break
            time.sleep(delay)
            delay = min(delay * 2, 0.2)
        except OSError as exc:
            last_error = exc
            if getattr(exc, "winerror", None) in (5, 32) and attempt < max_retries - 1:
                time.sleep(delay)
                delay = min(delay * 2, 0.2)
                continue
            break

    # Im Fehlerfall Modus wiederherstellen, falls geändert
    if original_mode is not None and os.path.exists(abs_path):
        try:
            os.chmod(abs_path, original_mode)
        except OSError:
            pass

    if last_error is not None:
        raise last_error


def open_file_cross_platform(path: str) -> None:
    """
    Öffnet eine Datei mit dem Standard-Programm des Betriebssystems.

    Args:
        path: Pfad zur zu öffnenden Datei

    Returns:
        None
    """
    if not os.path.exists(path):
        return

    if sys.platform == 'win32':
        os.startfile(path)
    elif sys.platform == 'darwin':
        subprocess.call(['open', path])
    else:
        subprocess.call(['xdg-open', path])


def open_folder_cross_platform(path: str) -> None:
    """
    Öffnet den Ordner einer Datei im Datei-Explorer.

    Args:
        path: Pfad zur Datei (der Ordner wird geöffnet)

    Returns:
        None
    """
    folder = os.path.dirname(path)
    if not os.path.exists(folder):
        return

    if sys.platform == 'win32':
        os.startfile(folder)
    elif sys.platform == 'darwin':
        subprocess.call(['open', folder])
    else:
        subprocess.call(['xdg-open', folder])


def atomic_write_text(file_path: str, content: str, encoding: str = "utf-8") -> None:
    """
    Schreibt Text atomar und sicher in eine Datei.

    Verwendet eine exklusive temporäre Datei im selben Verzeichnis (O_CREAT | O_EXCL)
    und ersetzt das Ziel erst nach erfolgreichem Schreiben und Sync. Bei Fehlern wird
    die temporäre Datei restlos bereinigt.

    Args:
        file_path: Ziel-Dateipfad
        content: Zu schreibender Text-Inhalt
        encoding: Zeichenkodierung (Standard: utf-8)
    """
    abs_path = os.path.abspath(file_path)
    if os.path.isdir(abs_path):
        raise IsADirectoryError(f"Zieldatei ist ein Verzeichnis: {abs_path}")
    dirname = os.path.dirname(abs_path) or "."
    os.makedirs(dirname, exist_ok=True)
    basename = os.path.basename(abs_path)

    fd, tmp_path = tempfile.mkstemp(
        dir=dirname,
        prefix=f".{basename}-",
        suffix=".tmp",
    )
    closed = False
    try:
        with open(fd, "w", encoding=encoding) as fh:
            fh.write(content)
            fh.flush()
            os.fsync(fh.fileno())
        closed = True
        _atomic_replace_with_retry(tmp_path, abs_path)
    except BaseException:
        if not closed:
            try:
                os.close(fd)
            except OSError:
                pass
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        raise


def atomic_write_json(
    file_path: str,
    data: Any,
    indent: int = 2,
    ensure_ascii: bool = False,
    encoding: str = "utf-8",
) -> None:
    """
    Serialisiert und schreibt JSON-Daten atomar und sicher in eine Datei.

    Verwendet eine exklusive temporäre Datei im selben Verzeichnis (O_CREAT | O_EXCL)
    und ersetzt das Ziel erst nach erfolgreichem Schreiben und Sync.
    Schützt vor unvollständigen Schreibvorgängen, Abstürzen und parallelen
    Kollisionen an festen .tmp-Dateinamen.

    Args:
        file_path: Ziel-Dateipfad
        data: Serialisierbare Datenstruktur
        indent: JSON-Einrückung (Standard: 2)
        ensure_ascii: Ob ASCII erzwungen werden soll (Standard: False)
        encoding: Zeichenkodierung (Standard: utf-8)
    """
    abs_path = os.path.abspath(file_path)
    if os.path.isdir(abs_path):
        raise IsADirectoryError(f"Zieldatei ist ein Verzeichnis: {abs_path}")
    dirname = os.path.dirname(abs_path) or "."
    os.makedirs(dirname, exist_ok=True)
    basename = os.path.basename(abs_path)

    fd, tmp_path = tempfile.mkstemp(
        dir=dirname,
        prefix=f".{basename}-",
        suffix=".tmp",
    )
    closed = False
    try:
        with open(fd, "w", encoding=encoding) as fh:
            json.dump(data, fh, ensure_ascii=ensure_ascii, indent=indent)
            fh.flush()
            os.fsync(fh.fileno())
        closed = True
        _atomic_replace_with_retry(tmp_path, abs_path)
    except BaseException:
        if not closed:
            try:
                os.close(fd)
            except OSError:
                pass
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        raise
