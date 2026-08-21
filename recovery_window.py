import subprocess
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
    QHBoxLayout
)

from config import (
    CONFIG_FILE,
    default_config,
    save
)


class RecoveryWindow(QDialog):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.setWindowTitle(
            "🛠 EZ Scan — Recovery Mode"
        )

        self.resize(
            520,
            360
        )

        self.result_mode = None

        self.setup_ui()

    # ========================================================
    # UI
    # ========================================================

    def setup_ui(self):

        title = QLabel(
            "🛠 Восстановление EZ Scan"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: bold;
            }
            """
        )

        info = QLabel(
            "Конфигурационный файл EZ Scan "
            "повреждён или не может быть прочитан.\n\n"
            "Выберите способ восстановления."
        )

        info.setWordWrap(
            True
        )

        restore = QPushButton(
            "↩ Восстановить резервную копию"
        )

        restore.clicked.connect(
            self.restore_backup
        )

        reset = QPushButton(
            "🧹 Сбросить настройки"
        )

        reset.clicked.connect(
            self.reset_config
        )

        folder = QPushButton(
            "📂 Открыть папку конфигурации"
        )

        folder.clicked.connect(
            self.open_folder
        )

        exit_button = QPushButton(
            "🚪 Выход"
        )

        exit_button.clicked.connect(
            self.reject
        )

        layout = QVBoxLayout()

        layout.addWidget(
            title
        )

        layout.addWidget(
            info
        )

        layout.addSpacing(
            10
        )

        layout.addWidget(
            restore
        )

        layout.addWidget(
            reset
        )

        layout.addWidget(
            folder
        )

        layout.addStretch()

        layout.addWidget(
            exit_button
        )

        self.setLayout(
            layout
        )

    # ========================================================
    # RESTORE
    # ========================================================

    def restore_backup(self):

        backup = CONFIG_FILE.with_name(
            "config.json.broken"
        )

        if not backup.exists():

            QMessageBox.warning(
                self,
                "Recovery",
                "Резервная копия не найдена."
            )

            return

        try:

            CONFIG_FILE.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            CONFIG_FILE.write_text(
                backup.read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8"
            )

            QMessageBox.information(
                self,
                "Recovery",
                "✅ Резервная конфигурация восстановлена."
            )

            self.result_mode = (
                "restored"
            )

            self.accept()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Recovery",
                f"❌ Не удалось восстановить:\n\n{e}"
            )

    # ========================================================
    # RESET
    # ========================================================

    def reset_config(self):

        answer = QMessageBox.question(
            self,
            "Сброс",
            "Сбросить настройки EZ Scan?\n\n"
            "Текущий повреждённый файл будет "
            "сохранён как backup."
        )

        if answer != QMessageBox.Yes:

            return

        try:

            if CONFIG_FILE.exists():

                backup = (
                    CONFIG_FILE.with_name(
                        "config.json.reset-backup"
                    )
                )

                CONFIG_FILE.replace(
                    backup
                )

            cfg = default_config()

            save(
                cfg
            )

            QMessageBox.information(
                self,
                "Recovery",
                "✅ Создана новая конфигурация."
            )

            self.result_mode = (
                "reset"
            )

            self.accept()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Recovery",
                f"❌ Ошибка сброса:\n\n{e}"
            )

    # ========================================================
    # FOLDER
    # ========================================================

    def open_folder(self):

        try:

            CONFIG_FILE.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            subprocess.Popen(
                [
                    "xdg-open",
                    str(
                        CONFIG_FILE.parent
                    )
                ]
            )

        except Exception as e:

            QMessageBox.warning(
                self,
                "Recovery",
                f"Не удалось открыть папку:\n\n{e}"
            )