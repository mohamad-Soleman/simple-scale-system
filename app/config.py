"""
Application configuration and path resolution.
Paths resolve correctly when running as script or as PyInstaller-packaged EXE.
"""
import os
import sys
from pathlib import Path


def get_base_dir() -> Path:
    """Base directory: EXE directory when frozen, else script directory."""
    if getattr(sys, "frozen", False):
        return Path(os.path.dirname(sys.executable))
    return Path(os.path.dirname(os.path.abspath(sys.argv[0])))


_BASE = get_base_dir()

# Paths (next to EXE or script)
LOG_PATH = _BASE / "scale_app.log"
DB_PATH = _BASE / "products.db"
CONFIG_INI_PATH = _BASE / "config.ini"

# Serial (scale)
COM_PORT = "COM6"
BAUD = 9600

# Currency
CURRENCY_SYMBOL = "₪"

# Label layout (for printer; pixel-related constants)
LABEL_FONT_NAME = "Arial"
LABEL_FONT_HEIGHT = 48
LABEL_FONT_WEIGHT = 700
LABEL_RTL_MARGIN_PX = 50


def load_optional_config() -> None:
    """Override defaults from config.ini in base dir if present."""
    if not CONFIG_INI_PATH.exists():
        return
    try:
        import configparser
        cfg = configparser.ConfigParser()
        cfg.read(CONFIG_INI_PATH, encoding="utf-8")
        global COM_PORT, BAUD, CURRENCY_SYMBOL, LABEL_FONT_HEIGHT, LABEL_RTL_MARGIN_PX
        if cfg.has_section("serial"):
            COM_PORT = cfg.get("serial", "port", fallback=COM_PORT)
            BAUD = int(cfg.get("serial", "baud", fallback=BAUD))
        if cfg.has_section("app"):
            CURRENCY_SYMBOL = cfg.get("app", "currency", fallback=CURRENCY_SYMBOL)
        if cfg.has_section("printer"):
            LABEL_FONT_HEIGHT = int(cfg.get("printer", "font_height", fallback=LABEL_FONT_HEIGHT))
            LABEL_RTL_MARGIN_PX = int(cfg.get("printer", "rtl_margin_px", fallback=LABEL_RTL_MARGIN_PX))
    except Exception:
        pass  # Keep defaults on any error
