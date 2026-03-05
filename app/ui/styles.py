"""
App-wide styles: high-contrast, readable theme for POS/touch.
Light backgrounds with dark text for maximum legibility.
"""
# Surfaces
BG_MAIN = "#eef1f5"
BG_CARD = "#ffffff"
BG_BUTTON_SECONDARY = "#d1d5db"
BG_BUTTON_HOVER = "#b8bec7"
# Text - always dark on light for readability
TEXT_PRIMARY = "#1a1a1a"
TEXT_SECONDARY = "#374151"
TEXT_MUTED = "#6b7280"
# Accents
ACCENT_PRIMARY = "#2563eb"
ACCENT_PRIMARY_HOVER = "#1d4ed8"
ACCENT_SUCCESS = "#15803d"
ACCENT_SUCCESS_HOVER = "#166534"
ACCENT_DANGER = "#b91c1c"
ACCENT_DANGER_HOVER = "#991b1b"
# Borders
BORDER = "#d1d5db"
BORDER_LIGHT = "#e5e7eb"

MAIN_WINDOW = f"""
    QWidget {{ background-color: {BG_MAIN}; }}
    QLabel {{ color: {TEXT_PRIMARY}; }}
    QTabWidget::pane {{
        background-color: {BG_MAIN};
        border: 1px solid {BORDER};
        border-radius: 8px;
        margin-top: -1px;
    }}
    QTabBar::tab {{
        background: {BG_BUTTON_SECONDARY};
        color: {TEXT_PRIMARY};
        padding: 14px 28px;
        font-size: 16px;
        font-weight: bold;
        margin-right: 4px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
    }}
    QTabBar::tab:selected {{
        background: {BG_MAIN};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-bottom: none;
    }}
"""

WEIGHT_LABEL = f"color: {TEXT_PRIMARY}; font-weight: bold;"
STATUS_LABEL = f"color: {TEXT_SECONDARY}; font-size: 15px;"
SELECTED_NAME = f"color: {TEXT_PRIMARY}; font-size: 19px; font-weight: bold;"
SELECTED_PRICE_KG = f"color: {TEXT_SECONDARY}; font-size: 17px;"
SELECTED_TOTAL = f"color: {ACCENT_PRIMARY}; font-size: 24px; font-weight: bold;"

BTN_SECONDARY = f"""
    QPushButton {{
        background: {BG_BUTTON_SECONDARY};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        font-size: 15px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background: {BG_BUTTON_HOVER};
        border-color: {TEXT_MUTED};
    }}
"""

BTN_PRIMARY = f"""
    QPushButton {{
        background: {ACCENT_PRIMARY};
        color: white;
        border: none;
        border-radius: 10px;
        font-size: 18px;
        font-weight: bold;
        padding: 12px 24px;
    }}
    QPushButton:hover {{
        background: {ACCENT_PRIMARY_HOVER};
    }}
    QPushButton:disabled {{
        background: {BG_BUTTON_SECONDARY};
        color: {TEXT_MUTED};
    }}
"""

BTN_PRODUCT = f"""
    QPushButton {{
        background: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 2px solid {BORDER};
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background: {BG_BUTTON_SECONDARY};
        border-color: {TEXT_MUTED};
    }}
    QPushButton:checked {{
        background: {ACCENT_PRIMARY};
        color: white;
        border-color: {ACCENT_PRIMARY};
    }}
"""

BTN_GENERIC = f"""
    QPushButton {{
        background: #dcfce7;
        color: {TEXT_PRIMARY};
        border: 2px solid {ACCENT_SUCCESS};
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background: #bbf7d0;
        border-color: {ACCENT_SUCCESS_HOVER};
    }}
    QPushButton:checked {{
        background: {ACCENT_PRIMARY};
        color: white;
        border-color: {ACCENT_PRIMARY};
    }}
"""

BTN_DANGER = f"""
    QPushButton {{
        background: {ACCENT_DANGER};
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background: {ACCENT_DANGER_HOVER};
    }}
"""

# Management table: light background, dark text
TABLE_STYLE = f"""
    QTableWidget {{
        background: {BG_CARD};
        color: {TEXT_PRIMARY};
        gridline-color: {BORDER_LIGHT};
        border: 1px solid {BORDER};
        border-radius: 8px;
    }}
    QTableWidget::item {{
        color: {TEXT_PRIMARY};
        padding: 10px;
    }}
    QHeaderView::section {{
        background: {BG_BUTTON_SECONDARY};
        color: {TEXT_PRIMARY};
        padding: 12px;
        font-weight: bold;
        border: none;
        border-bottom: 2px solid {BORDER};
    }}
"""

# Keypad: dialog with light background, dark text on keys
KEYPAD_DISPLAY = f"""
    QLabel {{
        background: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 2px solid {BORDER};
        border-radius: 8px;
        padding: 12px;
    }}
"""

KEYPAD_BTN = f"""
    QPushButton {{
        background: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 2px solid {BORDER};
        border-radius: 10px;
        font-size: 18px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background: {BG_BUTTON_SECONDARY};
        border-color: {TEXT_MUTED};
    }}
    QPushButton:disabled {{
        background: {BORDER_LIGHT};
        color: {TEXT_MUTED};
        border-color: {BORDER};
    }}
"""

KEYPAD_BTN_PRIMARY = f"""
    QPushButton {{
        background: {ACCENT_PRIMARY};
        color: white;
        border: none;
        border-radius: 10px;
        font-size: 18px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background: {ACCENT_PRIMARY_HOVER};
    }}
    QPushButton:disabled {{
        background: {BG_BUTTON_SECONDARY};
        color: {TEXT_MUTED};
    }}
"""

# Keypad dialog window
KEYPAD_DIALOG = f"""
    QDialog {{ background: {BG_MAIN}; }}
    QLabel {{ color: {TEXT_PRIMARY}; }}
"""

# Form dialog: light background, dark labels and inputs
FORM_DIALOG = f"""
    QDialog {{ background: {BG_MAIN}; }}
    QLabel {{ color: {TEXT_PRIMARY}; }}
    QLineEdit {{
        background: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 2px solid {BORDER};
        border-radius: 6px;
        padding: 8px;
        font-size: 15px;
        selection-background-color: {ACCENT_PRIMARY};
    }}
    QCheckBox {{
        color: {TEXT_PRIMARY};
        font-size: 15px;
    }}
    QPushButton {{
        background: {BG_BUTTON_SECONDARY};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background: {BG_BUTTON_HOVER};
    }}
"""
