# Sicherheit lokaler Dateikopien

Der lokale Kopierhelfer schreibt jede Kopie zunächst in eine exklusiv erzeugte,
zufällig benannte Datei im Zielverzeichnis. Erst nach erfolgreichem `shutil.copy2`
ersetzt `os.replace` das Ziel. Fremde Dateien mit dem früher verwendeten Namen
`<Ziel>.prosync_tmp` werden weder überschrieben noch bereinigt. Auch eine Quelle
mit diesem Namen bleibt erhalten.

Quelle und Ziel mit derselben Dateiidentität werden abgewiesen, einschließlich
Hardlinks und Pfaden durch Verzeichnis-Junctions. Die Identität wird vor der
Reservierung und nach der Kopie geprüft. Fehler bei der Identitätsprüfung führen
zum Abbruch. Parallele Kopierer verwenden unterschiedliche Stagingdateien; unter
Windows können einzelne Veröffentlichungen mit einem Sharingfehler scheitern.

Unter Windows bleibt das Überschreiben einer regulären, einfach verlinkten
schreibgeschützten Zieldatei möglich. Ihr Schreibschutz wird erst unmittelbar vor
dem Ersetzen aufgehoben. Scheitert das Ersetzen, wird der ursprüngliche Modus
wiederhergestellt, sofern das Ziel noch dieselbe Datei ist. Schreibgeschützte
Hardlink- oder Reparse-Ziele werden abgewiesen, damit keine andere Datei über
einen Alias verändert wird. Die Quelle wird niemals beschreibbar gemacht.

Bei Fehlern bereinigt der Helfer ausschließlich seine eigene Stagingdatei und
erhält die ursprüngliche Exception. Eine durch Copy2 schreibgeschützte Stage darf
für diese Bereinigung beschreibbar gemacht werden. Fehler beim Wiederherstellen
oder Bereinigen werden protokolliert; ein extern gesperrtes Objekt kann verbleiben.

Dies ist keine Garantie für einen konsistenten Snapshot einer gleichzeitig
veränderten Quelle oder für Dauerhaftigkeit bei Stromausfall. Externe Dateiaustausche
nach der letzten Prüfung und ein hartes Prozessende bleiben separate Grenzen.
SFTP-Tempdateien und Verzeichnisscans überlappender Syncjobs verwenden andere
Codepfade und sind durch diese Änderung nicht abgesichert.

Die Laufzeitgegenproben stehen in `tests/test_atomic_copy_ownership.py`.
