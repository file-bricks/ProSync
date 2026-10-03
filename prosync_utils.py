"""
ProSync Utilities
Gemeinsame Hilfsfunktionen für ProSync-Komponenten
"""

import json
import os
import subprocess
import sys
import tempfile
from typing import Any


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
        os.replace(tmp_path, abs_path)
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
        os.replace(tmp_path, abs_path)
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
