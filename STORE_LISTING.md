# Store Listing - ProSync

## Deutsch

### Kurzbeschreibung (max 100 Zeichen)
Lokales Backup- und Sync-Tool mit Datenbankschutz, Batch-Sync und redigiertem Profil-Export.

### Beschreibung (max 10.000 Zeichen)
ProSync ist eine lokale Desktop-Anwendung für Datei- und Ordner-Synchronisation mit besonderem Fokus auf sichere Backups für SQLite- und Access-Dateien. Das Tool läuft ohne Cloud-Zwang, arbeitet direkt mit lokalen Pfaden oder Netzlaufwerken und hilft dabei, wiederkehrende Sync-Jobs planbar und transparent auszuführen.

**Was ProSync kann:**

- Ordner-Synchronisation: Einweg, Update, Spiegelung oder Zwei-Wege-Sync für lokale Ordner und Freigaben
- Datei-Synchronisation: Einzelne Dateien separat absichern, ideal für Datenbanken oder sensible Projektdateien
- Datenbankschutz: SQLite- und Access-Dateien werden erkannt; WAL-Dateien und kritische Fälle werden sicher behandelt
- Batch-Sync: Mehrere ausgewählte Verbindungen in einem Lauf nacheinander starten
- Geplante Backups: Intervalle pro Verbindung festlegen und im Hintergrund über das Tray ausführen
- Sync-Reports: Kopierte, gelöschte und übersprungene Dateien werden lokal protokolliert
- Companion-Export: Redigierte Profile als `prosync-profile-v1.json` ohne echte lokale Pfade und ohne Secrets austauschen
- ProFiler-Companion: Optionalen ProFiler direkt aus ProSync starten

**Warum ProSync?**

- Lokal zuerst: Keine Pflicht-Cloud, keine Kontoregistrierung, keine versteckte Datensynchronisation
- Sicherer Umgang mit Datenbanken: Kritische SQLite-Dateien werden nicht wie normale Dateien behandelt
- Praktisch für den Alltag: Tray-Betrieb, Zeitpläne, Batch-Läufe und klare Statusanzeige
- Austauschfähig: Profile können redigiert exportiert werden, ohne private Pfade oder Tokens offenzulegen

**Für wen ist ProSync gedacht?**

Für Entwickler, Selbstständige, Power-User und kleine Teams, die lokale Projektordner, Dokumente oder Datenbanken regelmäßig sichern oder zwischen Geräten abgleichen möchten, ohne daraus gleich eine Cloud-Plattform zu machen.

### Schlüsselwörter
Backup, Synchronisation, Datei-Sync, Ordner-Sync, SQLite, Datenbankschutz, Batch-Sync

### Kategorie
Utilities

---

## English

### Short Description (max 100 chars)
Local backup and sync tool with database safety, batch runs, and redacted profile exchange.

### Description (max 10,000 chars)
ProSync is a local desktop application for file and folder synchronization with a strong focus on safe backups for SQLite and Access data. It works directly with local paths or network shares, avoids cloud lock-in, and makes recurring sync jobs transparent and repeatable.

**What ProSync does:**

- Folder synchronization: One-way, update, mirror, or two-way sync for local folders and shares
- File synchronization: Protect individual files separately, ideal for databases or sensitive project files
- Database safety: Detects SQLite and Access files and handles WAL-related edge cases deliberately
- Batch sync: Run multiple selected connections sequentially in one batch
- Scheduled backups: Configure per-connection intervals and keep jobs running in the tray
- Sync reports: Stores local reports with copied, deleted, and skipped file counters
- Companion export: Exchange redacted `prosync-profile-v1.json` profiles without real local paths or secrets
- ProFiler companion: Launch an optional ProFiler sidecar directly from ProSync

**Why ProSync?**

- Local first: No required cloud account, no forced online backend, no hidden remote sync
- Safer database handling: Critical SQLite files are not treated like ordinary documents
- Practical desktop workflow: Tray mode, schedules, batch execution, and clear status feedback
- Portable collaboration: Exchange profiles without exposing private paths or tokens

**Who is ProSync for?**

Developers, freelancers, power users, and small teams who want to back up or synchronize project folders, documents, and database files across devices without turning the workflow into a cloud platform.

### Keywords
backup, sync, file sync, folder sync, SQLite, database safety, batch sync

### Category
Utilities

---

## Español

### Short Description (max 100 chars)
Herramienta local de copia y sincronización con protección de bases de datos y exportación.

### Description (max 10,000 chars)
ProSync es una aplicación de escritorio local para la sincronización de archivos y carpetas, con especial atención a las copias de seguridad seguras para bases de datos SQLite y Access. Funciona sin dependencia de la nube, opera directamente con rutas locales o recursos de red compartidos y permite ejecutar tareas de sincronización periódicas de forma predecible y transparente.

**Capacidades de ProSync:**

- Sincronización de carpetas: Unidireccional, actualización, espejo o bidireccional para carpetas locales y recursos compartidos
- Sincronización de archivos: Protección individual de archivos críticos, ideal para bases de datos o archivos de proyecto sensibles
- Seguridad de bases de datos: Detección inteligente de archivos SQLite y Access con gestión segura de transacciones WAL
- Sincronización por lotes: Ejecución secuencial de múltiples conexiones seleccionadas en una sola pasada
- Copias programadas: Intervalos configurables por conexión con ejecución en segundo plano desde la bandeja del sistema
- Informes de sincronización: Registro local detallado con recuentos de archivos copiados, eliminados y omitidos
- Exportación para Companion: Intercambio de perfiles seguros como `prosync-profile-v1.json` sin rutas locales privadas ni credenciales
- Integración con ProFiler: Acceso directo opcional a herramientas de inspección ProFiler

**¿Por qué elegir ProSync?**

- Enfoque local primero: Sin cuentas obligatorias en la nube ni transferencias remotas ocultas
- Manejo seguro de bases de datos: Las bases de datos SQLite críticas no se tratan como archivos de texto convencionales
- Flujo de trabajo práctico: Modo bandeja, temporizadores, operaciones por lotes y estado en tiempo real
- Portabilidad transparente: Comparta esquemas de sincronización sin exponer tokens ni directorios personales

**¿A quién va dirigido?**

Desarrolladores, profesionales independientes, administradores y equipos que necesitan respaldar o sincronizar carpetas de proyectos y bases de datos locales entre dispositivos sin depender de infraestructuras en la nube.

### Keywords
copia seguridad, sincronizacion, sincronizar archivos, sincronizar carpetas, sqlite, seguridad base datos, sincronizacion lotes

### Category
Utilities

---

## 简体中文

### Short Description (max 100 chars)
本地备份与同步工具，具备数据库安全保护、批量同步与脱敏配置文件导出功能。

### Description (max 10,000 chars)
ProSync 是一款注重数据安全的本地桌面文件与文件夹同步工具，特别针对 SQLite 与 Access 数据库备份进行了深度优化。软件无需强制云端连接，直接对本地路径与网络共享进行操作，让周期性同步与备份任务变得透明、可控且高效。

**核心功能特性：**

- 文件夹同步：支持单向备份、增量更新、镜像同步以及双向协同同步
- 独立文件保护：针对关键数据库或项目文件提供专属同步保障
- 数据库专项防护：智能识别 SQLite 与 Access 文件，严格保障 WAL 检查点安全
- 批量同步执行：一次性顺序触发多个预设的同步连接
- 计划任务管理：为各连接配置独立时间间隔，托盘静默运行
- 本地同步报告：详尽记录已复制、已删除及跳过文件数量与时间戳
- Companion 配置文件导出：通过 `prosync-profile-v1.json` 导出已脱敏的同步配置，不包含私密绝对路径与认证密钥
- ProFiler 协同启动：可无缝配合 ProFiler 辅助工具运行

**选择 ProSync 的理由：**

- 本地优先原则：无强制在线注册，无隐式数据上传，绝对尊重隐私
- 专业的数据库安全：针对关键 SQLite 文件采取原子性保护，杜绝读写冲突损坏
- 高效实用的桌面交互：支持系统托盘最小化、定时排程、批量调度与清晰状态回显
- 安全的协作机制：配置文件经脱敏后可安全分享，杜绝机密泄露

**适用人群：**

适合开发者、自由职业者、企业IT运维及个人用户，用于高效同步与备份本地工作目录、文档及数据库。

### Keywords
备份, 同步, 文件同步, 文件夹同步, sqlite, 数据库安全, 批量同步

### Category
Utilities

---

## 日本語

### Short Description (max 100 chars)
データベース保護、一括同期、秘匿化プロファイル出力対応のローカル同期・バックアップツール。

### Description (max 10,000 chars)
ProSync は、SQLite や Access データベースの安全なバックアップに特化したローカルファイル・フォルダ同期デスクトップアプリケーションです。クラウドを介さず、ローカルストレージやネットワーク共有上で直接動作し、定期的な同期処理を透明かつ確実に実行します。

**主な機能：**

- フォルダ同期：片方向同期、差分更新、完全ミラーリング、双方向同期に対応
- 個別ファイル同期：重要なデータベースや設定ファイルを個別に保護
- データベース保護：SQLite および Access を自動検知し、WAL チェックポイントの安全性を確保
- バッチ同期：選択した複数の接続をワンクリックで順次実行
- スケジュール設定：接続ごとの同期間隔を指定し、システムトレイで常駐実行
- 同期レポート：コピー、削除、スキップされたファイル数と時刻をローカルに記録
- Companion プロファイル出力：実パスやシークレットを自動秘匿化した `prosync-profile-v1.json` の入出力に対応
- ProFiler 連携：ProFiler ツールとのスムーズな連携起動

**ProSync が選ばれる理由：**

- 完全ローカル動作：外部アカウント不要、クラウド依存なし、安全なデータ管理
- 確実なデータベース保護：重要な SQLite ファイルを安全に同期
- 快適なデスクトップ体験：トレイ常駐、スケジュール、一括同期、わかりやすいステータス表示
- 安全な共有機能：個人情報や絶対パスを含まない安全なプロファイル連携

**対象ユーザー：**

ローカル環境のファイル、プロジェクトフォルダ、データベースを確実にバックアップ・同期したい開発者、フリーランス、IT管理者向け。

### Keywords
バックアップ, 同期, ファイル同期, フォルダ同期, sqlite, データベース保護, 一括同期

### Category
Utilities

---

## Русский

### Short Description (max 100 chars)
Локальный инструмент резервного копирования и синхронизации с защитой БД и экспортом.

### Description (max 10,000 chars)
ProSync — это настольное приложение для локальной синхронизации файлов и папок с расширенной защитой баз данных SQLite и Access. Программа работает напрямую с локальными путями и сетевыми папками без привязки к облачным сервисам, обеспечивая прозрачное и надежное резервное копирование.

**Основные возможности ProSync:**

- Синхронизация папок: односторонняя, обновление, зеркалирование и двусторонняя синхронизация
- Синхронизация отдельных файлов: надежная защита критически важных файлов и баз данных
- Защита баз данных: распознавание SQLite и Access с безопасной обработкой WAL-файлов
- Пакетная синхронизация: последовательный запуск нескольких выбранных подключений
- Расписание резервного копирования: настраиваемые интервалы и фоновая работа в системном трее
- Локальные отчеты: подробная статистика скопированных, удаленных и пропущенных файлов
- Экспорт для Companion: обмен безопасными профилями `prosync-profile-v1.json` без конфиденциальных путей и паролей
- Интеграция с ProFiler: быстрый вызов инструментов ProFiler непосредственно из программы

**Преимущества ProSync:**

- Локальная безопасность: без обязательной регистрации, внешних облаков и скрытой передачи данных
- Безопасность баз данных: предотвращение повреждений файлов SQLite при копировании
- Удобство использования: работа в трее, гибкие таймеры, пакетные задания и наглядный статус
- Безопасный обмен конфигурациями: экспорт профилей без раскрытия личных путей

**Для кого предназначен ProSync:**

Для разработчиков, специалистов, системных администраторов и пользователей, которым требуется надежное и безопасное резервное копирование файлов и баз данных.

### Keywords
резервное копирование, синхронизация, синхронизация файлов, синхронизация папок, sqlite, защита баз данных, пакетная синхронизация

### Category
Utilities
