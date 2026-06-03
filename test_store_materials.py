from __future__ import annotations

import importlib.util
import os
from pathlib import Path

from PySide6.QtGui import QImage


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROJECT_ROOT = Path(__file__).resolve().parent
MODULE_PATH = PROJECT_ROOT / "_WARTUNG" / "generate_store_screenshots.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("prosync_store_materials", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_build_demo_config_contains_store_relevant_examples():
    module = _load_module()

    config = module.build_demo_config()

    assert "app" in config
    assert len(config["connections"]) == 3
    assert {conn["type"] for conn in config["connections"]} == {"folder", "file"}
    assert any("_portable_import" in conn for conn in config["connections"])


def test_write_manifest_lists_expected_screenshots(tmp_path):
    module = _load_module()

    module.write_manifest(tmp_path)

    content = (tmp_path / "README.md").read_text(encoding="utf-8")
    for filename, caption in module.SCREENSHOTS:
        assert filename in content
        assert caption in content


def test_generate_store_assets_creates_expected_sizes(tmp_path):
    module = _load_module()

    generated = module.generate_store_assets(tmp_path)

    assert len(generated) == len(module.STORE_ASSETS)
    for filename, width, height in module.STORE_ASSETS:
        image = QImage(str(tmp_path / filename))
        assert not image.isNull()
        assert image.width() == width
        assert image.height() == height


def main() -> int:
    from tempfile import TemporaryDirectory

    test_build_demo_config_contains_store_relevant_examples()
    with TemporaryDirectory(prefix="prosync-store-test-") as temp_dir:
        temp_path = Path(temp_dir)
        test_write_manifest_lists_expected_screenshots(temp_path / "manifest")
        test_generate_store_assets_creates_expected_sizes(temp_path / "assets")
    print("Store-Material-Tests bestanden.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
