APP_STYLESHEET = r"""
QWidget {
    background: #09090b;
    color: #f5f5f5;
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
}
QMainWindow { background: #09090b; }
QFrame#Sidebar {
    background: #111116;
    border-right: 1px solid #27272f;
}
QFrame#Card {
    background: #121218;
    border: 1px solid #27272f;
    border-radius: 14px;
}
QLabel#Title {
    font-size: 26px;
    font-weight: 800;
    color: #ff4fa3;
}
QLabel#Subtitle { color: #a1a1aa; font-size: 12px; }
QLabel#SectionTitle { font-weight: 700; font-size: 15px; color: #ffffff; }
QLabel#Badge {
    background: #25111d;
    color: #ff76b8;
    border: 1px solid #5b2141;
    border-radius: 9px;
    padding: 3px 8px;
}
QPushButton {
    background: #202027;
    border: 1px solid #30303a;
    border-radius: 9px;
    padding: 9px 14px;
    font-weight: 600;
}
QPushButton:hover { background: #2a2a33; border-color: #4b4b58; }
QPushButton:disabled { color: #666671; background: #18181d; }
QPushButton#Primary {
    background: #ff2f92;
    color: #ffffff;
    border: 1px solid #ff5aaa;
}
QPushButton#Primary:hover { background: #ff4fa3; }
QPushButton#Danger { color: #ff92bd; border-color: #5b2141; background: #25111d; }
QLineEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background: #0d0d12;
    border: 1px solid #30303a;
    border-radius: 8px;
    padding: 7px 9px;
    selection-background-color: #ff2f92;
}
QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #ff4fa3;
}
QComboBox::drop-down { border: none; width: 24px; }
QCheckBox { spacing: 8px; color: #d4d4d8; }
QCheckBox::indicator {
    width: 16px; height: 16px; border-radius: 4px;
    border: 1px solid #474752; background: #101015;
}
QCheckBox::indicator:checked { background: #ff2f92; border-color: #ff6ab1; }
QTableWidget {
    background: #0d0d12;
    alternate-background-color: #111118;
    gridline-color: #22222a;
    border: 1px solid #292932;
    border-radius: 10px;
}
QHeaderView::section {
    background: #17171e;
    color: #c9c9d1;
    border: none;
    border-bottom: 1px solid #30303a;
    padding: 8px;
    font-weight: 700;
}
QProgressBar {
    background: #17171e;
    border: 1px solid #30303a;
    border-radius: 7px;
    height: 14px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk { background: #ff2f92; border-radius: 6px; }
QScrollBar:vertical { background: #111116; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #383843; border-radius: 5px; min-height: 24px; }
QToolTip { background: #1b1b22; color: white; border: 1px solid #44444f; padding: 5px; }
"""
