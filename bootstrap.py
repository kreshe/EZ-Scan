import sys

from PySide6.QtWidgets import (
    QApplication,
    QDialog
)

from config import load, save
from setup_window import SetupWindow


def main():

    app = QApplication(
        sys.argv
    )

    cfg = load()

    # ============================================================
    # ПЕРВЫЙ ЗАПУСК
    # ============================================================

    if cfg.get(
        "first_run",
        True
    ):

        setup = SetupWindow()

        result = setup.exec()

        if result != QDialog.Accepted:

            return 0

        cfg = load()

        cfg["first_run"] = False

        save(
            cfg
        )

    # ============================================================
    # ОСНОВНОЕ ПРИЛОЖЕНИЕ
    # ============================================================

    from main import run

    window = run()

    if window is None:

        return 0

    return app.exec()


if __name__ == "__main__":

    sys.exit(
        main()
    )