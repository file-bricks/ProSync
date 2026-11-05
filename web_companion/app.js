import {
  createDemoProfile,
  filterConnections,
  parseProfilePayload,
  parseProfileText,
  readProfileFile,
  sortConnections,
  summarizeProfile,
} from "./library.js";

const STORAGE_KEY = "prosync-web-companion-profile-v1";
const LANG_STORAGE_KEY = "prosync_companion_lang";

export const SUPPORTED_LANGUAGES = ["de", "en", "es", "zh", "ja", "ru"];

export const TRANSLATIONS = {
  "de": {
    "app_eyebrow": "ProSync Web/PWA Companion",
    "app_title": "Profile und letzte Sync-Berichte lokal lesen",
    "hero_text": "Dieser Companion importiert prosync-profile-v1.json aus der Desktop-App, zeigt Verbindungen und Report-Metadaten read-only an und speichert den letzten Stand lokal für Offline-Starts.",
    "lbl_language": "Sprache / Language:",
    "btn_import": "Profil importieren",
    "btn_paste": "JSON aus Text laden",
    "btn_demo": "Demo laden",
    "btn_reset": "Zurücksetzen",
    "status_initial": "Noch kein Profil geladen. Importiere eine prosync-profile-v1.json oder starte mit Demo.",
    "label_json_paste": "Optionaler JSON-Paste",
    "heading_filters": "Filter",
    "lbl_search": "Suche",
    "placeholder_search": "Name, Modus, Labels, Muster",
    "lbl_connection_type": "Verbindungstyp",
    "opt_all_types": "Alle Typen",
    "lbl_sync_mode": "Sync-Modus",
    "opt_all_modes": "Alle Modi",
    "lbl_autosync": "Autosync",
    "opt_all": "Alle",
    "opt_enabled": "Aktiv",
    "opt_disabled": "Inaktiv",
    "lbl_sorting": "Sortierung",
    "opt_sort_name_asc": "Name A–Z",
    "opt_sort_name_desc": "Name Z–A",
    "opt_sort_autosync_first": "Autosync aktiv zuerst",
    "opt_sort_type": "Nach Typ",
    "heading_types_modes": "Typen und Modi",
    "heading_types": "Typen",
    "heading_modes": "Modi",
    "heading_connections": "Verbindungen",
    "connections_desc": "Read-only Ansicht des exportierten ProSync-Profils ohne echte lokale Pfade.",
    "empty_connections": "Noch keine Verbindungen sichtbar.",
    "heading_reports": "Berichte",
    "reports_desc": "Der Export liefert nur redigierte Report-Metadaten. Trigger und Live-Sync bleiben Desktop-Aufgabe.",
    "empty_reports": "Keine Report-Metadaten im Profil enthalten.",
    "summary_source": "Quelle",
    "summary_exported": "Exportiert",
    "summary_version": "App-Version",
    "summary_connections": "Verbindungen",
    "summary_autosync_active": "Autosync aktiv",
    "summary_reports_in_export": "Reports im Export",
    "summary_last_run": "Letzter Lauf",
    "summary_desktop_note": "Desktop-Hinweis",
    "summary_notifications_on": "Benachrichtigungen an",
    "summary_notifications_off": "Benachrichtigungen aus",
    "summary_none": "Keiner",
    "pill_visible": "{count} sichtbar",
    "fact_databases": "Datenbanken",
    "fact_critical": "Kritisch",
    "fact_excluded": "Ausgeschlossen",
    "fact_db_size": "DB-Größe",
    "chip_autosync_active": "Autosync aktiv",
    "chip_checkpoint": "Checkpoint vor Sync",
    "chip_indexing": "Indexierung",
    "chip_requires_mapping": "Neu zuordnen",
    "lbl_source": "Quelle",
    "lbl_target": "Ziel",
    "lbl_db_index": "Index / DB",
    "lbl_conflict_policy": "Konfliktregel",
    "lbl_exclude_patterns": "Ausschlussmuster",
    "not_included": "Nicht enthalten",
    "not_set": "Nicht gesetzt",
    "no_exclude_patterns": "Keine Ausschlussmuster im Export.",
    "duration": "Dauer",
    "copied": "Kopiert",
    "deleted": "Gelöscht",
    "skipped": "Übersprungen",
    "actions": "Aktionen",
    "data_volume": "Datenmenge",
    "status_demo_loaded": "Demo-Profil geladen.",
    "status_file_loaded": "Profil geladen: {name}",
    "status_paste_loaded": "Profil aus Text geladen.",
    "status_paste_empty": "Bitte zuerst JSON in das Textfeld einfügen.",
    "status_storage_error": "Profil konnte nicht lokal gespeichert werden.",
    "status_profile_cleared": "Lokaler Profilstand entfernt.",
    "status_restored": "Letztes Profil aus dem Browser-Speicher wiederhergestellt.",
    "hint_iphone": "iPhone/iPad: In Safari über Teilen -> Zum Home-Bildschirm als lokale Referenz anheften.",
    "hint_android": "Android: Im Browser-Menü App installieren oder Zum Startbildschirm hinzufügen nutzen.",
    "hint_desktop": "Desktop: Im Browser als App installieren oder einfach als Offline-Referenz geöffnet lassen.",
    "hint_online": "Online oder lokaler Host erkannt. Nach dem ersten Laden bleibt der letzte Profilstand offline verfügbar.",
    "hint_offline": "Offline-Modus aktiv. Der Companion arbeitet mit dem letzten lokal gespeicherten Profilstand."
  },
  "en": {
    "app_eyebrow": "ProSync Web/PWA Companion",
    "app_title": "Read profiles and recent sync reports locally",
    "hero_text": "This companion imports prosync-profile-v1.json from the desktop app, displays connections and report metadata read-only, and saves the latest state locally for offline starts.",
    "lbl_language": "Language / Sprache:",
    "btn_import": "Import profile",
    "btn_paste": "Load JSON from text",
    "btn_demo": "Load demo",
    "btn_reset": "Reset",
    "status_initial": "No profile loaded yet. Import a prosync-profile-v1.json or start with demo.",
    "label_json_paste": "Optional JSON paste",
    "heading_filters": "Filters",
    "lbl_search": "Search",
    "placeholder_search": "Name, mode, labels, pattern",
    "lbl_connection_type": "Connection type",
    "opt_all_types": "All types",
    "lbl_sync_mode": "Sync mode",
    "opt_all_modes": "All modes",
    "lbl_autosync": "Autosync",
    "opt_all": "All",
    "opt_enabled": "Enabled",
    "opt_disabled": "Disabled",
    "lbl_sorting": "Sorting",
    "opt_sort_name_asc": "Name A–Z",
    "opt_sort_name_desc": "Name Z–A",
    "opt_sort_autosync_first": "Autosync active first",
    "opt_sort_type": "By type",
    "heading_types_modes": "Types and modes",
    "heading_types": "Types",
    "heading_modes": "Modes",
    "heading_connections": "Connections",
    "connections_desc": "Read-only view of exported ProSync profile without real local paths.",
    "empty_connections": "No connections visible yet.",
    "heading_reports": "Reports",
    "reports_desc": "The export provides redacted report metadata only. Triggers and live sync remain desktop tasks.",
    "empty_reports": "No report metadata included in profile.",
    "summary_source": "Source",
    "summary_exported": "Exported",
    "summary_version": "App version",
    "summary_connections": "Connections",
    "summary_autosync_active": "Autosync active",
    "summary_reports_in_export": "Reports in export",
    "summary_last_run": "Last run",
    "summary_desktop_note": "Desktop note",
    "summary_notifications_on": "Notifications on",
    "summary_notifications_off": "Notifications off",
    "summary_none": "None",
    "pill_visible": "{count} visible",
    "fact_databases": "Databases",
    "fact_critical": "Critical",
    "fact_excluded": "Excluded",
    "fact_db_size": "DB size",
    "chip_autosync_active": "Autosync active",
    "chip_checkpoint": "Checkpoint before sync",
    "chip_indexing": "Indexing",
    "chip_requires_mapping": "Remap required",
    "lbl_source": "Source",
    "lbl_target": "Target",
    "lbl_db_index": "Index / DB",
    "lbl_conflict_policy": "Conflict policy",
    "lbl_exclude_patterns": "Exclude patterns",
    "not_included": "Not included",
    "not_set": "Not set",
    "no_exclude_patterns": "No exclude patterns in export.",
    "duration": "Duration",
    "copied": "Copied",
    "deleted": "Deleted",
    "skipped": "Skipped",
    "actions": "Actions",
    "data_volume": "Data volume",
    "status_demo_loaded": "Demo profile loaded.",
    "status_file_loaded": "Profile loaded: {name}",
    "status_paste_loaded": "Profile loaded from text.",
    "status_paste_empty": "Please paste JSON into the text field first.",
    "status_storage_error": "Could not save profile locally.",
    "status_profile_cleared": "Local profile data cleared.",
    "status_restored": "Last profile restored from browser storage.",
    "hint_iphone": "iPhone/iPad: In Safari tap Share -> Add to Home Screen for local offline reference.",
    "hint_android": "Android: Use Install App or Add to Home Screen from the browser menu.",
    "hint_desktop": "Desktop: Install as an app in your browser or keep it open for offline reference.",
    "hint_online": "Online or local host detected. The last profile state remains available offline after first load.",
    "hint_offline": "Offline mode active. The companion works with the last locally saved profile state."
  },
  "es": {
    "app_eyebrow": "ProSync Web/PWA Companion",
    "app_title": "Leer perfiles e informes recientes de sincronización localmente",
    "hero_text": "Este asistente importa prosync-profile-v1.json desde la aplicación de escritorio, muestra conexiones y metadatos de informes en solo lectura, y guarda el estado localmente para arranques sin conexión.",
    "lbl_language": "Idioma / Language:",
    "btn_import": "Importar perfil",
    "btn_paste": "Cargar JSON desde texto",
    "btn_demo": "Cargar demo",
    "btn_reset": "Restablecer",
    "status_initial": "Aún no se ha cargado ningún perfil. Importe un prosync-profile-v1.json o comience con la demo.",
    "label_json_paste": "Pegado opcional de JSON",
    "heading_filters": "Filtros",
    "lbl_search": "Buscar",
    "placeholder_search": "Nombre, modo, etiquetas, patrón",
    "lbl_connection_type": "Tipo de conexión",
    "opt_all_types": "Todos los tipos",
    "lbl_sync_mode": "Modo de sincronización",
    "opt_all_modes": "Todos los modos",
    "lbl_autosync": "Autosync",
    "opt_all": "Todos",
    "opt_enabled": "Activo",
    "opt_disabled": "Inactivo",
    "lbl_sorting": "Orden",
    "opt_sort_name_asc": "Nombre A–Z",
    "opt_sort_name_desc": "Nombre Z–A",
    "opt_sort_autosync_first": "Autosync activo primero",
    "opt_sort_type": "Por tipo",
    "heading_types_modes": "Tipos y modos",
    "heading_types": "Tipos",
    "heading_modes": "Modos",
    "heading_connections": "Conexiones",
    "connections_desc": "Vista de solo lectura del perfil de ProSync sin rutas locales reales.",
    "empty_connections": "No hay conexiones visibles todavía.",
    "heading_reports": "Informes",
    "reports_desc": "La exportación solo incluye metadatos de informes. Las ejecuciones en vivo siguen siendo tarea de escritorio.",
    "empty_reports": "No hay metadatos de informes en el perfil.",
    "summary_source": "Origen",
    "summary_exported": "Exportado",
    "summary_version": "Versión app",
    "summary_connections": "Conexiones",
    "summary_autosync_active": "Autosync activo",
    "summary_reports_in_export": "Informes en exportación",
    "summary_last_run": "Última ejecución",
    "summary_desktop_note": "Aviso de escritorio",
    "summary_notifications_on": "Notificaciones activadas",
    "summary_notifications_off": "Notificaciones desactivadas",
    "summary_none": "Ninguno",
    "pill_visible": "{count} visible(s)",
    "fact_databases": "Bases de datos",
    "fact_critical": "Crítico",
    "fact_excluded": "Excluido",
    "fact_db_size": "Tamaño BD",
    "chip_autosync_active": "Autosync activo",
    "chip_checkpoint": "Punto de control antes de sincronizar",
    "chip_indexing": "Indexación",
    "chip_requires_mapping": "Reasignación requerida",
    "lbl_source": "Origen",
    "lbl_target": "Destino",
    "lbl_db_index": "Índice / BD",
    "lbl_conflict_policy": "Política de conflictos",
    "lbl_exclude_patterns": "Patrones de exclusión",
    "not_included": "No incluido",
    "not_set": "No establecido",
    "no_exclude_patterns": "Sin patrones de exclusión en la exportación.",
    "duration": "Duración",
    "copied": "Copiados",
    "deleted": "Eliminados",
    "skipped": "Omitidos",
    "actions": "Acciones",
    "data_volume": "Volumen de datos",
    "status_demo_loaded": "Perfil de demo cargado.",
    "status_file_loaded": "Perfil cargado: {name}",
    "status_paste_loaded": "Perfil cargado desde texto.",
    "status_paste_empty": "Por favor pegue JSON en el campo primero.",
    "status_storage_error": "No se pudo guardar el perfil localmente.",
    "status_profile_cleared": "Perfil local eliminado.",
    "status_restored": "Último perfil restaurado del almacenamiento del navegador.",
    "hint_iphone": "iPhone/iPad: En Safari, pulse Compartir -> Añadir a la pantalla de inicio.",
    "hint_android": "Android: Use Instalar aplicación o Añadir a pantalla principal desde el menú.",
    "hint_desktop": "Escritorio: Instale como app en su navegador o manténgalo abierto sin conexión.",
    "hint_online": "Host local o en línea detectado. El último perfil permanece disponible sin conexión tras la primera carga.",
    "hint_offline": "Modo sin conexión activo. El asistente trabaja con el último perfil guardado localmente."
  },
  "zh": {
    "app_eyebrow": "ProSync Web/PWA 协同端",
    "app_title": "在本地读取配置文件与最新同步报告",
    "hero_text": "此协同端支持从桌面端导入 prosync-profile-v1.json，只读展示连接与报告元数据，并在本地保存最新状态以供离线使用。",
    "lbl_language": "语言 / Language:",
    "btn_import": "导入配置文件",
    "btn_paste": "从文本加载 JSON",
    "btn_demo": "加载演示数据",
    "btn_reset": "重置",
    "status_initial": "尚未加载配置文件。请导入 prosync-profile-v1.json 或加载演示。",
    "label_json_paste": "可选的 JSON 粘贴",
    "heading_filters": "筛选",
    "lbl_search": "搜索",
    "placeholder_search": "名称、模式、标签、模式",
    "lbl_connection_type": "连接类型",
    "opt_all_types": "所有类型",
    "lbl_sync_mode": "同步模式",
    "opt_all_modes": "所有模式",
    "lbl_autosync": "自动同步",
    "opt_all": "全部",
    "opt_enabled": "已启用",
    "opt_disabled": "已禁用",
    "lbl_sorting": "排序",
    "opt_sort_name_asc": "名称 A–Z",
    "opt_sort_name_desc": "名称 Z–A",
    "opt_sort_autosync_first": "自动同步优先",
    "opt_sort_type": "按类型",
    "heading_types_modes": "类型与模式",
    "heading_types": "类型",
    "heading_modes": "模式",
    "heading_connections": "连接",
    "connections_desc": "导出的 ProSync 配置文件只读视图，不包含本地真实路径。",
    "empty_connections": "暂无可见连接。",
    "heading_reports": "报告",
    "reports_desc": "导出仅提供脱敏后的报告元数据。触发与实时同步仍由桌面端负责。",
    "empty_reports": "配置文件中不含报告元数据。",
    "summary_source": "来源",
    "summary_exported": "导出时间",
    "summary_version": "应用版本",
    "summary_connections": "连接数",
    "summary_autosync_active": "自动同步激活",
    "summary_reports_in_export": "导出中包含报告",
    "summary_last_run": "最后运行",
    "summary_desktop_note": "桌面端提示",
    "summary_notifications_on": "通知已开启",
    "summary_notifications_off": "通知已关闭",
    "summary_none": "无",
    "pill_visible": "{count} 条可见",
    "fact_databases": "数据库",
    "fact_critical": "关键",
    "fact_excluded": "已排除",
    "fact_db_size": "数据库体积",
    "chip_autosync_active": "自动同步已激活",
    "chip_checkpoint": "同步前检查点",
    "chip_indexing": "索引中",
    "chip_requires_mapping": "需要重新映射",
    "lbl_source": "源路径",
    "lbl_target": "目标路径",
    "lbl_db_index": "索引 / 数据库",
    "lbl_conflict_policy": "冲突策略",
    "lbl_exclude_patterns": "排除规则",
    "not_included": "不包含",
    "not_set": "未设置",
    "no_exclude_patterns": "导出中无排除规则。",
    "duration": "耗时",
    "copied": "已复制",
    "deleted": "已删除",
    "skipped": "已跳过",
    "actions": "操作总数",
    "data_volume": "传输体积",
    "status_demo_loaded": "演示配置文件已加载。",
    "status_file_loaded": "已从文件加载配置：{name}",
    "status_paste_loaded": "已从文本成功解析配置。",
    "status_paste_empty": "请先在文本框中粘贴 JSON 数据。",
    "status_storage_error": "无法将配置存储至本地浏览器。",
    "status_profile_cleared": "本地配置文件已清除。",
    "status_restored": "已从本地存储恢复最新配置文件。",
    "hint_iphone": "iPhone/iPad：在 Safari 中点击分享 -> 添加至主屏幕以便离线使用。",
    "hint_android": "Android：在浏览器菜单中使用安装应用或添加至主屏幕。",
    "hint_desktop": "桌面端：在浏览器中作为应用安装，或直接打开作为离线参考。",
    "hint_online": "检测到在线或本地主机。首次加载后，最新配置文件可在离线状态下使用。",
    "hint_offline": "离线模式生效。协同端正在使用本地最近保存的配置文件状态。"
  },
  "ja": {
    "app_eyebrow": "ProSync Web/PWA コンパニオン",
    "app_title": "プロファイルと最新の同期レポートをローカルで閲覧",
    "hero_text": "このコンパニオンはデスクトップアプリから prosync-profile-v1.json を読み込み、接続とレポートメタデータを閲覧専用で表示し、オフライン起動用に最新状態を保存します。",
    "lbl_language": "言語 / Language:",
    "btn_import": "プロファイルをインポート",
    "btn_paste": "テキストから JSON を読込",
    "btn_demo": "デモを読込",
    "btn_reset": "リセット",
    "status_initial": "プロファイルがまだ読み込まれていません。prosync-profile-v1.json をインポートするかデモを開始してください。",
    "label_json_paste": "任意の JSON 貼り付け",
    "heading_filters": "フィルター",
    "lbl_search": "検索",
    "placeholder_search": "名前、モード、ラベル、パターン",
    "lbl_connection_type": "接続タイプ",
    "opt_all_types": "すべてのタイプ",
    "lbl_sync_mode": "同期モード",
    "opt_all_modes": "すべてのモード",
    "lbl_autosync": "自動同期",
    "opt_all": "すべて",
    "opt_enabled": "有効",
    "opt_disabled": "無効",
    "lbl_sorting": "並び順",
    "opt_sort_name_asc": "名前 A–Z",
    "opt_sort_name_desc": "名前 Z–A",
    "opt_sort_autosync_first": "自動同期有効を優先",
    "opt_sort_type": "タイプ順",
    "heading_types_modes": "タイプとモード",
    "heading_types": "タイプ",
    "heading_modes": "モード",
    "heading_connections": "接続",
    "connections_desc": "実ローカルパスを含まない、エクスポートされた ProSync プロファイルの閲覧ビュー。",
    "empty_connections": "表示可能な接続がありません。",
    "heading_reports": "レポート",
    "reports_desc": "エクスポートには秘匿化されたメタデータのみが含まれます。実行と同期はデスクトップで行います。",
    "empty_reports": "プロファイルにレポートメタデータが含まれていません。",
    "summary_source": "ソース",
    "summary_exported": "エクスポート日時",
    "summary_version": "アプリバージョン",
    "summary_connections": "接続総数",
    "summary_autosync_active": "自動同期有効",
    "summary_reports_in_export": "レポート件数",
    "summary_last_run": "前回の実行",
    "summary_desktop_note": "デスクトップ通知",
    "summary_notifications_on": "通知オン",
    "summary_notifications_off": "通知オフ",
    "summary_none": "なし",
    "pill_visible": "{count} 件表示中",
    "fact_databases": "データベース",
    "fact_critical": "重要",
    "fact_excluded": "除外",
    "fact_db_size": "DBサイズ",
    "chip_autosync_active": "自動同期有効",
    "chip_checkpoint": "同期前チェックポイント",
    "chip_indexing": "インデックス中",
    "chip_requires_mapping": "再マッピング必要",
    "lbl_source": "ソース",
    "lbl_target": "ターゲット",
    "lbl_db_index": "インデックス / DB",
    "lbl_conflict_policy": "衝突ポリシー",
    "lbl_exclude_patterns": "除外パターン",
    "not_included": "未含有",
    "not_set": "未設定",
    "no_exclude_patterns": "除外パターンはありません。",
    "duration": "所要時間",
    "copied": "コピー済",
    "deleted": "削除済",
    "skipped": "スキップ",
    "actions": "アクション総数",
    "data_volume": "転送容量",
    "status_demo_loaded": "デモプロファイルを読み込みました。",
    "status_file_loaded": "プロファイルをファイルから読み込みました: {name}",
    "status_paste_loaded": "テキストからプロファイルを読み込みました。",
    "status_paste_empty": "テキスト入力欄に JSON を貼り付けてください。",
    "status_storage_error": "プロファイルのローカル保存に失敗しました。",
    "status_profile_cleared": "ローカルプロファイルデータを消去しました。",
    "status_restored": "ブラウザストレージから前回のプロファイルを復元しました。",
    "hint_iphone": "iPhone/iPad: Safari で「共有」→「ホーム画面に追加」してオフライン参照。",
    "hint_android": "Android: ブラウザメニューの「アプリをインストール」または「ホーム画面に追加」を使用。",
    "hint_desktop": "デスクトップ: ブラウザからアプリとしてインストールするか、オフライン参照用に使用。",
    "hint_online": "オンラインまたはローカルホストを検出。初回読込後、最新状態はオフラインで利用可能です。",
    "hint_offline": "オフラインモード有効。最後に保存されたプロファイルデータで動作しています。"
  },
  "ru": {
    "app_eyebrow": "ProSync Web/PWA Companion",
    "app_title": "Локальный просмотр профилей и последних отчетов синхронизации",
    "hero_text": "Этот компаньон импортирует prosync-profile-v1.json из приложения, отображает подключения и метаданные отчетов только для чтения и сохраняет состояние локально для автономной работы.",
    "lbl_language": "Язык / Language:",
    "btn_import": "Импортировать профиль",
    "btn_paste": "Загрузить JSON из текста",
    "btn_demo": "Загрузить демо",
    "btn_reset": "Сброс",
    "status_initial": "Профиль еще не загружен. Импортируйте prosync-profile-v1.json или начните с демо.",
    "label_json_paste": "Вставка JSON (необязательно)",
    "heading_filters": "Фильтры",
    "lbl_search": "Поиск",
    "placeholder_search": "Имя, режим, метки, шаблоны",
    "lbl_connection_type": "Тип подключения",
    "opt_all_types": "Все типы",
    "lbl_sync_mode": "Режим синхронизации",
    "opt_all_modes": "Все режимы",
    "lbl_autosync": "Автосинхронизация",
    "opt_all": "Все",
    "opt_enabled": "Активно",
    "opt_disabled": "Неактивно",
    "lbl_sorting": "Сортировка",
    "opt_sort_name_asc": "Имя А–Я",
    "opt_sort_name_desc": "Имя Я–А",
    "opt_sort_autosync_first": "Сначала с автосинхронизацией",
    "opt_sort_type": "По типу",
    "heading_types_modes": "Типы и режимы",
    "heading_types": "Типы",
    "heading_modes": "Режимы",
    "heading_connections": "Подключения",
    "connections_desc": "Просмотр профиля ProSync только для чтения без реальных локальных путей.",
    "empty_connections": "Подключения пока не отображаются.",
    "heading_reports": "Отчеты",
    "reports_desc": "Экспорт содержит только обработанные метаданные. Запуск и синхронизация выполняются на ПК.",
    "empty_reports": "В профиле нет метаданных отчетов.",
    "summary_source": "Источник",
    "summary_exported": "Экспортировано",
    "summary_version": "Версия",
    "summary_connections": "Подключения",
    "summary_autosync_active": "Автосинхр. активна",
    "summary_reports_in_export": "Отчетов в экспорте",
    "summary_last_run": "Последний запуск",
    "summary_desktop_note": "Заметка",
    "summary_notifications_on": "Уведомления вкл.",
    "summary_notifications_off": "Уведомления выкл.",
    "summary_none": "Нет",
    "pill_visible": "{count} видимых",
    "fact_databases": "Базы данных",
    "fact_critical": "Критические",
    "fact_excluded": "Исключено",
    "fact_db_size": "Размер БД",
    "chip_autosync_active": "Автосинхр. активна",
    "chip_checkpoint": "Точка перед синхронизацией",
    "chip_indexing": "Индексирование",
    "chip_requires_mapping": "Требуется сопоставление",
    "lbl_source": "Источник",
    "lbl_target": "Назначение",
    "lbl_db_index": "Индекс / БД",
    "lbl_conflict_policy": "Конфликты",
    "lbl_exclude_patterns": "Исключения",
    "not_included": "Не включено",
    "not_set": "Не задано",
    "no_exclude_patterns": "В экспорте нет правил исключения.",
    "duration": "Длительность",
    "copied": "Скопировано",
    "deleted": "Удалено",
    "skipped": "Пропущено",
    "actions": "Действий",
    "data_volume": "Объем данных",
    "status_demo_loaded": "Демо-профиль загружен.",
    "status_file_loaded": "Профиль загружен: {name}",
    "status_paste_loaded": "Профиль загружен из текста.",
    "status_paste_empty": "Пожалуйста, вставьте JSON в текстовое поле.",
    "status_storage_error": "Не удалось сохранить профиль локально.",
    "status_profile_cleared": "Локальные данные профиля удалены.",
    "status_restored": "Последний профиль восстановлен из хранилища браузера.",
    "hint_iphone": "iPhone/iPad: В Safari нажмите Поделиться -> На экран «Домой».",
    "hint_android": "Android: В меню браузера выберите Установить приложение или Добавить на главный экран.",
    "hint_desktop": "ПК: Установите как приложение в браузере или используйте автономно.",
    "hint_online": "Сеть или локальный хост обнаружены. После первой загрузки профиль доступен офлайн.",
    "hint_offline": "Автономный режим активен. Используется последнее сохраненное состояние профиля."
  }
};

let currentLanguage = "de";

export function getLanguage() {
  return currentLanguage;
}

export function getTranslation(key, lang = currentLanguage) {
  const dict = TRANSLATIONS[lang] || TRANSLATIONS.de;
  return dict[key] || TRANSLATIONS.de[key] || key;
}

export function setLanguage(lang) {
  if (SUPPORTED_LANGUAGES.includes(lang)) {
    currentLanguage = lang;
    try {
      localStorage.setItem(LANG_STORAGE_KEY, lang);
    } catch (_e) {
      // Safari private mode protection
    }
    if (typeof document !== "undefined") {
      applyTranslations();
    }
  }
}

export function applyTranslations() {
  if (typeof document === "undefined") return;
  document.documentElement.lang = currentLanguage;

  const langSelect = document.querySelector("#lang-select");
  if (langSelect && langSelect.value !== currentLanguage) {
    langSelect.value = currentLanguage;
  }

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    const val = getTranslation(key);
    if (val) {
      if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
        el.value = val;
      } else {
        el.textContent = val;
      }
    }
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.getAttribute("data-i18n-placeholder");
    const val = getTranslation(key);
    if (val) {
      el.placeholder = val;
    }
  });

  updateInstallHint();
  updateOfflineHint();

  if (state.profile) {
    renderProfile(state.profile);
  }
}

const state = {
  profile: null,
  sourceLabel: "Kein Profil geladen",
};

const isBrowser = typeof window !== "undefined" && typeof document !== "undefined";

const elements = isBrowser
  ? {
      importInput: document.querySelector("#import-input"),
      importButton: document.querySelector("#import-button"),
      pasteButton: document.querySelector("#paste-button"),
      demoButton: document.querySelector("#demo-button"),
      resetButton: document.querySelector("#reset-button"),
      jsonInput: document.querySelector("#json-input"),
      searchInput: document.querySelector("#search-input"),
      typeFilter: document.querySelector("#type-filter"),
      modeFilter: document.querySelector("#mode-filter"),
      autosyncFilter: document.querySelector("#autosync-filter"),
      sortSelect: document.querySelector("#sort-select"),
      status: document.querySelector("#load-status"),
      installHint: document.querySelector("#install-hint"),
      offlineHint: document.querySelector("#offline-hint"),
      summary: document.querySelector("#summary-cards"),
      typeList: document.querySelector("#type-list"),
      modeList: document.querySelector("#mode-list"),
      connectionCount: document.querySelector("#connection-count"),
      connectionList: document.querySelector("#connection-list"),
      emptyState: document.querySelector("#empty-state"),
      reportList: document.querySelector("#report-list"),
      reportEmpty: document.querySelector("#report-empty"),
      langSelect: document.querySelector("#lang-select"),
    }
  : {};

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function formatDate(isoString) {
  if (!isoString) {
    return getTranslation("summary_none");
  }
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) {
    return isoString;
  }
  const localeMap = {
    de: "de-DE",
    en: "en-US",
    es: "es-ES",
    zh: "zh-CN",
    ja: "ja-JP",
    ru: "ru-RU",
  };
  return new Intl.DateTimeFormat(localeMap[currentLanguage] || "de-DE", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function formatBytes(bytes) {
  const value = Number(bytes);
  if (!Number.isFinite(value) || value <= 0) {
    return "0 B";
  }
  const units = ["B", "KB", "MB", "GB", "TB"];
  let size = value;
  let index = 0;
  while (size >= 1024 && index < units.length - 1) {
    size /= 1024;
    index += 1;
  }
  return `${size.toFixed(size >= 10 || index === 0 ? 0 : 1)} ${units[index]}`;
}

function setStatus(message, kind = "info") {
  if (!elements.status) return;
  elements.status.textContent = message;
  elements.status.dataset.kind = kind;
}

function detectInstallHint() {
  if (!isBrowser || !navigator) return "";
  const agent = (navigator.userAgent || "").toLowerCase();
  if (agent.includes("iphone") || agent.includes("ipad")) {
    return getTranslation("hint_iphone");
  }
  if (agent.includes("android")) {
    return getTranslation("hint_android");
  }
  return getTranslation("hint_desktop");
}

function updateInstallHint() {
  if (elements.installHint) {
    elements.installHint.textContent = detectInstallHint();
  }
}

function updateOfflineHint() {
  if (!elements.offlineHint || !isBrowser) return;
  elements.offlineHint.textContent = navigator.onLine
    ? getTranslation("hint_online")
    : getTranslation("hint_offline");
}

function saveProfile(profile) {
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        sourceLabel: state.sourceLabel,
        profile,
        savedAt: new Date().toISOString(),
      }),
    );
  } catch (_error) {
    setStatus(getTranslation("status_storage_error"), "warning");
  }
}

function loadStoredProfile() {
  let raw;
  try {
    raw = localStorage.getItem(STORAGE_KEY);
  } catch (_error) {
    return null;
  }
  if (!raw) {
    return null;
  }
  try {
    const parsed = JSON.parse(raw);
    return {
      sourceLabel: parsed.sourceLabel ?? "Zuletzt geladenes Profil",
      profile: coerceStoredProfile(parsed.profile),
    };
  } catch (_error) {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (_removeError) {
      // Ignore removal errors (e.g. Safari Private Mode)
    }
    return null;
  }
}

function coerceStoredProfile(profile) {
  if (!profile || typeof profile !== "object") {
    throw new Error("Kein gespeichertes Profil gefunden.");
  }
  if ("exportedAt" in profile && Array.isArray(profile.connections) && profile.reports) {
    return profile;
  }
  return parseProfilePayload(profile);
}

function renderSummary(profile) {
  if (!elements.summary) return;
  const summary = summarizeProfile(profile);
  const latest = profile.reports.latest;
  const cards = [
    { label: getTranslation("summary_source"), value: state.sourceLabel },
    { label: getTranslation("summary_exported"), value: formatDate(profile.exportedAt) },
    { label: getTranslation("summary_version"), value: profile.exportedFromVersion },
    { label: getTranslation("summary_connections"), value: String(summary.connectionCount) },
    { label: getTranslation("summary_autosync_active"), value: String(summary.autosyncEnabledCount) },
    { label: getTranslation("summary_reports_in_export"), value: String(summary.reportCount) },
    { label: getTranslation("summary_last_run"), value: latest ? formatDate(latest.startedAt) : getTranslation("summary_none") },
    { label: getTranslation("summary_desktop_note"), value: profile.notificationsEnabled ? getTranslation("summary_notifications_on") : getTranslation("summary_notifications_off") },
  ];

  elements.summary.innerHTML = cards
    .map(
      (card) => `
        <article class="summary-card">
          <span class="summary-label">${escapeHtml(card.label)}</span>
          <strong class="summary-value">${escapeHtml(card.value)}</strong>
        </article>
      `,
    )
    .join("");
}

function renderMetaLists(profile) {
  if (!elements.typeFilter) return;
  const summary = summarizeProfile(profile);
  const typeEntries = Object.entries(summary.types).sort((left, right) => right[1] - left[1]);
  const modeEntries = Object.entries(summary.modes).sort((left, right) => right[1] - left[1]);

  const allTypesText = getTranslation("opt_all_types");
  const allModesText = getTranslation("opt_all_modes");

  elements.typeFilter.innerHTML = [`<option value="all">${escapeHtml(allTypesText)}</option>`]
    .concat(typeEntries.map(([type]) => `<option value="${escapeHtml(type)}">${escapeHtml(type)}</option>`))
    .join("");

  elements.modeFilter.innerHTML = [`<option value="all">${escapeHtml(allModesText)}</option>`]
    .concat(modeEntries.map(([mode]) => `<option value="${escapeHtml(mode)}">${escapeHtml(mode)}</option>`))
    .join("");

  elements.typeList.innerHTML = typeEntries
    .map(
      ([type, count]) => `
        <li class="meta-item">
          <span>${escapeHtml(type)}</span>
          <span class="pill">${count}</span>
        </li>
      `,
    )
    .join("");

  elements.modeList.innerHTML = modeEntries
    .map(
      ([mode, count]) => `
        <li class="meta-item">
          <span>${escapeHtml(mode)}</span>
          <span class="pill">${count}</span>
        </li>
      `,
    )
    .join("");
}

function renderConnections(profile) {
  if (!elements.connectionCount) return;
  const filtered = filterConnections(profile, {
    search: elements.searchInput ? elements.searchInput.value : "",
    type: elements.typeFilter ? elements.typeFilter.value : "all",
    mode: elements.modeFilter ? elements.modeFilter.value : "all",
    autosync: elements.autosyncFilter ? elements.autosyncFilter.value : "all",
  });
  const visibleConnections = sortConnections(filtered, elements.sortSelect ? elements.sortSelect.value : "name-asc");

  elements.connectionCount.textContent = getTranslation("pill_visible").replace("{count}", visibleConnections.length);
  elements.connectionList.innerHTML = visibleConnections
    .map((connection) => {
      const autosyncText = connection.autosyncEnabled
        ? `${getTranslation("opt_enabled")} · ${connection.autosyncIntervalMinutes} min`
        : getTranslation("opt_disabled");
      const safety = connection.safetySummary;
      const safetyFacts = safety
        ? `
          <div class="facts-grid">
            <div class="fact-box">
              <span class="label">${getTranslation("fact_databases")}</span>
              <strong>${safety.databasesFound}</strong>
            </div>
            <div class="fact-box">
              <span class="label">${getTranslation("fact_critical")}</span>
              <strong>${safety.criticalDatabases}</strong>
            </div>
            <div class="fact-box">
              <span class="label">${getTranslation("fact_excluded")}</span>
              <strong>${safety.excludedDatabases}</strong>
            </div>
            <div class="fact-box">
              <span class="label">${getTranslation("fact_db_size")}</span>
              <strong>${escapeHtml(`${safety.totalDbSizeMb} MB`)}</strong>
            </div>
          </div>
        `
        : "";

      const chips = [];
      chips.push(`<span class="pill">${escapeHtml(connection.type)}</span>`);
      chips.push(`<span class="pill">${escapeHtml(connection.mode)}</span>`);
      if (connection.autosyncEnabled) {
        chips.push(`<span class="pill pill--accent">${getTranslation("chip_autosync_active")}</span>`);
      }
      if (connection.checkpointBeforeSync) {
        chips.push(`<span class="pill">${getTranslation("chip_checkpoint")}</span>`);
      }
      if (connection.indexing) {
        chips.push(`<span class="pill">${getTranslation("chip_indexing")}</span>`);
      }
      if (connection.requiresMapping) {
        chips.push(`<span class="pill">${getTranslation("chip_requires_mapping")}</span>`);
      }

      const excludePatterns = connection.excludePatterns.length
        ? connection.excludePatterns.map((pattern) => `<span class="pill">${escapeHtml(pattern)}</span>`).join("")
        : `<span class="subtle">${getTranslation("no_exclude_patterns")}</span>`;

      return `
        <article class="connection-card">
          <div class="connection-card__header">
            <div>
              <h3>${escapeHtml(connection.name)}</h3>
              <p class="subtle">${escapeHtml(connection.id)} · ${escapeHtml(autosyncText)}</p>
            </div>
            <div class="chip-list">${chips.join("")}</div>
          </div>
          <div class="path-grid">
            <div class="path-box">
              <span class="label">${getTranslation("lbl_source")}</span>
              <strong class="code-line">${escapeHtml(connection.pathHints.sourceLabel)}</strong>
            </div>
            <div class="path-box">
              <span class="label">${getTranslation("lbl_target")}</span>
              <strong class="code-line">${escapeHtml(connection.pathHints.targetLabel)}</strong>
            </div>
            <div class="path-box">
              <span class="label">${getTranslation("lbl_db_index")}</span>
              <strong class="code-line">${escapeHtml(connection.pathHints.dbLabel || getTranslation("not_included"))}</strong>
            </div>
            <div class="path-box">
              <span class="label">${getTranslation("lbl_conflict_policy")}</span>
              <strong>${escapeHtml(connection.conflictPolicy || getTranslation("not_set"))}</strong>
            </div>
          </div>
          <div class="path-box">
            <span class="label">${getTranslation("lbl_exclude_patterns")}</span>
            <div class="chip-list">${excludePatterns}</div>
          </div>
          ${safetyFacts}
        </article>
      `;
    })
    .join("");

  const hasConnections = visibleConnections.length > 0;
  elements.emptyState.hidden = hasConnections;
  elements.connectionList.hidden = !hasConnections;
}

function renderReports(profile) {
  if (!elements.reportList) return;
  const reports = profile.reports.items;
  elements.reportList.innerHTML = reports
    .map(
      (report) => `
        <article class="report-card">
          <div class="report-card__header">
            <div>
              <h3>${escapeHtml(report.connection)}</h3>
              <p class="subtle">${escapeHtml(report.connectionId || "ohne ID")} · ${escapeHtml(report.mode)}</p>
            </div>
            <span class="pill">${escapeHtml(formatDate(report.startedAt))}</span>
          </div>
          <div class="report-stats">
            <div class="fact-box">
              <span class="label">${getTranslation("duration")}</span>
              <strong>${escapeHtml(`${report.durationSeconds} s`)}</strong>
            </div>
            <div class="fact-box">
              <span class="label">${getTranslation("copied")}</span>
              <strong>${report.filesCopied}</strong>
            </div>
            <div class="fact-box">
              <span class="label">${getTranslation("deleted")}</span>
              <strong>${report.filesDeleted}</strong>
            </div>
            <div class="fact-box">
              <span class="label">${getTranslation("skipped")}</span>
              <strong>${report.filesSkipped}</strong>
            </div>
            <div class="fact-box">
              <span class="label">${getTranslation("actions")}</span>
              <strong>${report.totalActions}</strong>
            </div>
            <div class="fact-box">
              <span class="label">${getTranslation("data_volume")}</span>
              <strong>${escapeHtml(formatBytes(report.bytesCopied))}</strong>
            </div>
          </div>
        </article>
      `,
    )
    .join("");

  const hasReports = reports.length > 0;
  elements.reportEmpty.hidden = hasReports;
  elements.reportList.hidden = !hasReports;
}

function renderProfile(profile) {
  state.profile = profile;
  renderSummary(profile);
  renderMetaLists(profile);
  renderConnections(profile);
  renderReports(profile);
}

function loadDemoProfile() {
  const profile = parseProfilePayload(createDemoProfile());
  state.sourceLabel = "Demo-Profil";
  saveProfile(profile);
  renderProfile(profile);
  setStatus(getTranslation("status_demo_loaded"), "success");
}

async function handleFileImport() {
  const [file] = elements.importInput.files ?? [];
  if (!file) {
    return;
  }
  try {
    const profile = await readProfileFile(file);
    state.sourceLabel = file.name;
    saveProfile(profile);
    renderProfile(profile);
    setStatus(getTranslation("status_file_loaded").replace("{name}", file.name), "success");
  } catch (error) {
    setStatus(error.message, "error");
  } finally {
    elements.importInput.value = "";
  }
}

function handlePasteImport() {
  const text = elements.jsonInput.value.trim();
  if (!text) {
    setStatus(getTranslation("status_paste_empty"), "warning");
    return;
  }
  try {
    const profile = parseProfileText(text);
    state.sourceLabel = "JSON-Paste";
    saveProfile(profile);
    renderProfile(profile);
    setStatus(getTranslation("status_paste_loaded"), "success");
  } catch (error) {
    setStatus(error.message, "error");
  }
}

function clearStoredProfile() {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (_removeError) {
    // Ignore removal errors (e.g. Safari Private Mode, policy-blocked storage)
  }
  state.profile = null;
  state.sourceLabel = "Kein Profil geladen";
  elements.jsonInput.value = "";
  elements.summary.innerHTML = "";
  elements.typeList.innerHTML = "";
  elements.modeList.innerHTML = "";
  elements.connectionList.innerHTML = "";
  elements.reportList.innerHTML = "";
  elements.connectionList.hidden = true;
  elements.reportList.hidden = true;
  elements.emptyState.hidden = false;
  elements.reportEmpty.hidden = false;
  elements.connectionCount.textContent = getTranslation("pill_visible").replace("{count}", "0");
  elements.typeFilter.innerHTML = `<option value="all">${escapeHtml(getTranslation("opt_all_types"))}</option>`;
  elements.modeFilter.innerHTML = `<option value="all">${escapeHtml(getTranslation("opt_all_modes"))}</option>`;
  elements.sortSelect.value = "name-asc";
  setStatus(getTranslation("status_profile_cleared"), "info");
}

function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) {
    return;
  }
  navigator.serviceWorker.register("./sw.js").catch(() => {
    setStatus("Service Worker konnte lokal nicht registriert werden.", "warning");
  });
}

function bindEvents() {
  if (!isBrowser) return;
  elements.importButton.addEventListener("click", () => elements.importInput.click());
  elements.importInput.addEventListener("change", handleFileImport);
  elements.pasteButton.addEventListener("click", handlePasteImport);
  elements.demoButton.addEventListener("click", loadDemoProfile);
  elements.resetButton.addEventListener("click", clearStoredProfile);
  elements.searchInput.addEventListener("input", () => {
    if (state.profile) {
      renderConnections(state.profile);
    }
  });
  elements.typeFilter.addEventListener("change", () => {
    if (state.profile) {
      renderConnections(state.profile);
    }
  });
  elements.modeFilter.addEventListener("change", () => {
    if (state.profile) {
      renderConnections(state.profile);
    }
  });
  elements.autosyncFilter.addEventListener("change", () => {
    if (state.profile) {
      renderConnections(state.profile);
    }
  });
  elements.sortSelect.addEventListener("change", () => {
    if (state.profile) {
      renderConnections(state.profile);
    }
  });
  if (elements.langSelect) {
    elements.langSelect.addEventListener("change", (e) => {
      setLanguage(e.target.value);
    });
  }
  window.addEventListener("online", updateOfflineHint);
  window.addEventListener("offline", updateOfflineHint);
}

export function boot() {
  if (!isBrowser) return;

  // Language restoration
  try {
    const savedLang = localStorage.getItem(LANG_STORAGE_KEY);
    if (savedLang && SUPPORTED_LANGUAGES.includes(savedLang)) {
      currentLanguage = savedLang;
    } else {
      const navLang = (navigator.language || "").slice(0, 2).toLowerCase();
      if (SUPPORTED_LANGUAGES.includes(navLang)) {
        currentLanguage = navLang;
      }
    }
  } catch (_e) {
    // Storage fallback
  }

  bindEvents();
  registerServiceWorker();
  applyTranslations();

  const params = new URLSearchParams(window.location.search);
  if (params.get("demo") === "1") {
    loadDemoProfile();
    return;
  }

  const stored = loadStoredProfile();
  if (stored) {
    state.sourceLabel = stored.sourceLabel;
    renderProfile(stored.profile);
    setStatus(getTranslation("status_restored"), "info");
    return;
  }

  setStatus(getTranslation("status_initial"), "info");
}

if (isBrowser) {
  boot();
}
