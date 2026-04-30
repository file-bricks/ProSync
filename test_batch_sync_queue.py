"""
Smoke-Test für die BatchSyncQueue.
Prüft Deduplizierung, Reihenfolge und Reset-Verhalten.
"""

import os
import sys
import importlib.util


EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def load_prosync_module():
    """Lädt das Hauptmodul per importlib."""
    module_path = os.path.join(os.path.dirname(__file__), "ProSyncStart_V3.1.py")
    spec = importlib.util.spec_from_file_location("prosync", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    print("=== BatchSyncQueue Smoke-Test ===\n")

    try:
        prosync = load_prosync_module()
        queue = prosync.BatchSyncQueue()

        conn_a = {"id": "a", "name": "A"}
        conn_b = {"id": "b", "name": "B"}
        conn_c = {"id": "c", "name": "C"}

        print("Test 1: Deduplizierung")
        planned = queue.start([conn_a, conn_b, conn_a, conn_c])
        assert [conn["id"] for conn in planned] == ["a", "b", "c"]
        assert queue.total == 3
        print("✓ PASS: Doppelte IDs werden entfernt\n")

        print("Test 2: Reihenfolge bleibt stabil")
        first = queue.next_connection()
        second = None
        third = None
        assert first["id"] == "a"
        queue.mark_current_finished()
        second = queue.next_connection()
        assert second["id"] == "b"
        queue.mark_current_finished()
        third = queue.next_connection()
        assert third["id"] == "c"
        print("✓ PASS: Verbindungen werden in Auswahl-Reihenfolge abgearbeitet\n")

        print("Test 3: Abschluss zählt korrekt")
        queue.mark_current_finished()
        assert queue.completed_count == 3
        assert queue.remaining_count == 0
        assert not queue.active
        print("✓ PASS: Abschlussstatus ist korrekt\n")

        print("Test 4: Reset bei neuem Batch")
        queue.start([conn_b, conn_c])
        assert queue.total == 2
        assert queue.completed_count == 0
        assert queue.remaining_count == 2
        print("✓ PASS: Neuer Batch setzt alten Zustand zurück\n")

        print("Test 5: cancel_pending verwirft Rest")
        queue.next_connection()
        skipped = queue.cancel_pending()
        assert len(skipped) == 1
        assert skipped[0]["id"] == "c"
        print("✓ PASS: Wartende Batch-Aufgaben werden korrekt verworfen\n")

        print("=== ALLE TESTS BESTANDEN ✓ ===")
        return EXIT_SUCCESS

    except AssertionError as exc:
        print(f"\n❌ TEST FEHLGESCHLAGEN: {exc}")
        return EXIT_FAILURE
    except Exception as exc:
        print(f"\n❌ UNERWARTETER FEHLER: {exc}")
        import traceback
        traceback.print_exc()
        return EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())
