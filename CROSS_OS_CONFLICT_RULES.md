# Cross-OS Conflict Rules

Stand: 2026-07-03

## Ziel

ProSync bleibt eine Desktop-Sync-Engine. macOS, Linux, Web/PWA, Android und iOS
dürfen ProSync-Profile lesen oder später Trigger auslösen, aber sie dürfen keine
zweite Sync-Engine mit eigenen Konfliktentscheidungen einführen.

Diese Regeln gelten für `prosync-profile-v1.json`, lokale Companion-Trigger und
spätere macOS-/Linux-Läufe.

## Portable Pfadschlüssel

Für plattformübergreifende Vergleiche erzeugt `cross_os_rules.py` einen
konservativen Schlüssel:

- Unicode wird nach NFC normalisiert.
- `\` und `/` gelten als Separatoren.
- Mehrfache Separatoren und redundante `.`-Segmente werden reduziert.
- Der Vergleich ist standardmäßig case-insensitive, weil Windows und häufig auch
  macOS Namen anders behandeln als Linux.
- Symlinks, Junctions, Umgebungsvariablen und reale Dateisystemziele werden nicht
  aufgelöst.

Wenn mehrere Originalpfade denselben portablen Schlüssel haben, muss ProSync den
Fall als Konflikt behandeln. Der Nutzer muss dann lokal entscheiden; der
Companion darf keinen Gewinner wählen.

## Symlinks und Junctions

Symlinks, Junctions und gemountete Netzpfade bleiben explizite lokale
Eigenschaften. Ein importiertes Profil darf sie nur als Hinweis anzeigen. Ein
späterer Zwei-Wege-Lauf muss vor dem Start prüfen, ob Quelle oder Ziel ein Link
ist, und bei Unsicherheit abbrechen oder eine klare Nutzerbestätigung verlangen.

## Zwei-Wege-Konflikte

Bei Zwei-Wege-Sync über mehrere Betriebssysteme gelten diese Stop-Regeln:

- Derselbe portable Schlüssel mit unterschiedlichen Originalpfaden blockiert den
  Lauf.
- Unicode-Normalisierungsdrift blockiert den Lauf, bis der Nutzer einen Namen
  festlegt.
- Reine Groß-/Kleinschreibungsunterschiede blockieren plattformübergreifend den
  Lauf, auch wenn Linux sie lokal unterscheiden könnte.
- Redigierte oder fehlende Pfade aus `prosync-profile-v1.json` werden niemals
  automatisch rekonstruiert.

Damit bleibt die Mobile-/PWA-Linie read-only beziehungsweise trigger-only und
die eigentliche Dateientscheidung bei der Desktop-App.
