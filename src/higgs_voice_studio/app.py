from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .ui import MainWindow


def main() -> int:
    # Ensure imports work when running app.py from source checkout.
    app = QApplication(sys.argv)
    app.setApplicationName("Higgs Voice Studio")
    app.setOrganizationName("Local Voice Tools")
    window = MainWindow()
    window.show()
    return app.exec()
