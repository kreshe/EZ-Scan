from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QMessageBox
)

from PySide6.QtCore import (
    QThread,
    Signal
)

from updater import (
    get_update_info,
    download_update
)


class UpdateThread(QThread):

    progress = Signal(int)
    finished = Signal(object)
    error = Signal(str)

    def __init__(
        self,
        info
    ):

        super().__init__()

        self.info = info

    def run(self):

        try:

            path = download_update(
                self.info,
                self.progress.emit
            )

            if path:

                self.finished.emit(
                    path
                )

            else:

                self.error.emit(
                    "Не удалось скачать обновление."
                )

        except Exception as e:

            self.error.emit(
                str(e)
            )


class UpdateWindow(QDialog):

    def __init__(
        self,
        current_version,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.current_version = (
            current_version
        )

        self.info_data = None
        self.update_thread = None
        self.updated_file = None

        self.setWindowTitle(
            "🔄 Обновление EZ Scan"
        )

        self.resize(
            520,
            380
        )

        self.setup_ui()

        self.check()

    def setup_ui(self):

        self.title = QLabel(
            "🔄 Проверка обновлений..."
        )

        self.title.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
            }
            """
        )

        self.info = QLabel()

        self.info.setWordWrap(
            True
        )

        self.notes = QLabel()

        self.notes.setWordWrap(
            True
        )

        self.progress = QProgressBar()

        self.progress.setValue(
            0
        )

        self.update_btn = QPushButton(
            "⬇ Скачать обновление"
        )

        self.update_btn.clicked.connect(
            self.download
        )

        self.update_btn.setEnabled(
            False
        )

        self.close_btn = QPushButton(
            "Закрыть"
        )

        self.close_btn.clicked.connect(
            self.reject
        )

        layout = QVBoxLayout()

        layout.addWidget(
            self.title
        )

        layout.addWidget(
            self.info
        )

        layout.addWidget(
            self.notes
        )

        layout.addWidget(
            self.progress
        )

        layout.addWidget(
            self.update_btn
        )

        layout.addWidget(
            self.close_btn
        )

        self.setLayout(
            layout
        )

    def check(self):

        self.info_data = (
            get_update_info(
                self.current_version
            )
        )

        if not self.info_data:

            self.title.setText(
                "⚠️ Не удалось проверить обновления"
            )

            self.info.setText(
                "Проверьте подключение к интернету."
            )

            return

        if not self.info_data.get(
            "update_available"
        ):

            self.title.setText(
                "✅ Установлена последняя версия"
            )

            self.info.setText(
                f"Текущая версия: "
                f"{self.current_version}"
            )

            return

        version = self.info_data[
            "version"
        ]

        self.title.setText(
            f"🚀 Доступна версия {version}"
        )

        self.info.setText(
            f"Текущая версия: "
            f"{self.current_version}<br>"
            f"Новая версия: "
            f"<b>{version}</b>"
        )

        self.notes.setText(
            self.info_data.get(
                "notes",
                ""
            )
        )

        self.update_btn.setEnabled(
            True
        )

    def download(self):

        self.update_btn.setEnabled(
            False
        )

        self.close_btn.setEnabled(
            False
        )

        self.title.setText(
            "⬇ Скачивание обновления..."
        )

        self.update_thread = UpdateThread(
            self.info_data
        )

        self.update_thread.progress.connect(
            self.progress.setValue
        )

        self.update_thread.finished.connect(
            self.download_finished
        )

        self.update_thread.error.connect(
            self.download_error
        )

        self.update_thread.start()

    def download_finished(
        self,
        path
    ):

        self.updated_file = path

        self.progress.setValue(
            100
        )

        self.title.setText(
            "✅ Обновление скачано"
        )

        self.info.setText(
            str(path)
        )

        self.close_btn.setText(
            "🚀 Перезапустить"
        )

        self.close_btn.setEnabled(
            True
        )

        self.close_btn.clicked.disconnect()

        self.close_btn.clicked.connect(
            self.restart
        )

    def download_error(
        self,
        message
    ):

        QMessageBox.critical(
            self,
            "Ошибка обновления",
            message
        )

        self.close_btn.setEnabled(
            True
        )

        self.update_btn.setEnabled(
            True
        )

    def restart(self):

        if not self.updated_file:

            return

        import os
        import subprocess

        updater = (
            self.updated_file
            .with_name(
                "update_and_restart.sh"
            )
        )

        updater.write_text(
            f"""#!/bin/bash
sleep 1
mv -f "{self.updated_file}" "$APPIMAGE"
chmod +x "$APPIMAGE"
exec "$APPIMAGE"
""",
            encoding="utf-8"
        )

        os.chmod(
            updater,
            0o755
        )

        appimage = os.environ.get(
            "APPIMAGE"
        )

        if not appimage:

            QMessageBox.warning(
                self,
                "Обновление",
                "Текущая программа не запущена "
                "как AppImage."
            )

            return

        subprocess.Popen(
            [
                "bash",
                str(updater)
            ],
            env={
                **os.environ,
                "APPIMAGE": appimage
            },
            start_new_session=True
        )

        self.accept()