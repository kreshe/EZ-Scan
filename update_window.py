from pathlib import Path
import webbrowser


from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QMessageBox,
    QTextEdit
)

from PySide6.QtCore import (
    QThread,
    Signal
)

from updater import (
    get_update_info,
    download_update,
    start_update,
    start_rollback,
    get_current_appimage
)


# ============================================================
# GITHUB
# ============================================================

GITHUB_URL = "https://github.com/kreshe/EZ-Scan"


# ============================================================
# DOWNLOAD THREAD
# ============================================================

class DownloadThread(QThread):

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

            self.finished.emit(
                path
            )

        except Exception as e:

            self.error.emit(
                str(e)
            )


# ============================================================
# UPDATE WINDOW
# ============================================================

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
        self.thread = None
        self.downloaded = None

        self.setWindowTitle(
            "🔄 Обновление EZ Scan"
        )

        self.resize(
            560,
            450
        )

        self.setup_ui()

        self.check()

    # ========================================================
    # UI
    # ========================================================

    def setup_ui(self):

        title = QLabel(
            "🔄 EZ Scan — обновления"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
            }
            """
        )

        # ----------------------------------------------------
        # INFO
        # ----------------------------------------------------

        self.info = QLabel()

        self.info.setWordWrap(
            True
        )

        # ----------------------------------------------------
        # RELEASE NOTES
        # ----------------------------------------------------

        self.notes = QTextEdit()

        self.notes.setReadOnly(
            True
        )

        # ----------------------------------------------------
        # PROGRESS
        # ----------------------------------------------------

        self.progress = QProgressBar()

        self.progress.setValue(
            0
        )

        # ----------------------------------------------------
        # UPDATE
        # ----------------------------------------------------

        self.update_button = QPushButton(
            "⬇ Скачать и установить"
        )

        self.update_button.clicked.connect(
            self.download
        )

        self.update_button.setEnabled(
            False
        )

        # ----------------------------------------------------
        # ROLLBACK
        # ----------------------------------------------------

        self.rollback_button = QPushButton(
            "↩ Откатить"
        )

        self.rollback_button.clicked.connect(
            self.rollback
        )

        self.rollback_button.setVisible(
            False
        )

        current = get_current_appimage()

        if current:

            backup = Path(
                str(current)
                + ".bak"
            )

            if backup.exists():

                self.rollback_button.setVisible(
                    True
                )

        # ----------------------------------------------------
        # GITHUB
        # ----------------------------------------------------

        self.github_button = QPushButton(
            "🌐 GitHub"
        )

        self.github_button.setToolTip(
            "Открыть страницу проекта на GitHub"
        )

        self.github_button.clicked.connect(
            self.open_github
        )

        # ----------------------------------------------------
        # CLOSE
        # ----------------------------------------------------

        close_button = QPushButton(
            "Закрыть"
        )

        close_button.clicked.connect(
            self.reject
        )

        # ----------------------------------------------------
        # BUTTONS
        # ----------------------------------------------------

        buttons = QHBoxLayout()

        buttons.addWidget(
            self.update_button
        )

        buttons.addWidget(
            self.rollback_button
        )

        buttons.addStretch()

        buttons.addWidget(
            self.github_button
        )

        buttons.addWidget(
            close_button
        )

        # ----------------------------------------------------
        # MAIN LAYOUT
        # ----------------------------------------------------

        layout = QVBoxLayout()

        layout.addWidget(
            title
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

        layout.addLayout(
            buttons
        )

        self.setLayout(
            layout
        )

    # ========================================================
    # GITHUB
    # ========================================================

    def open_github(self):

        try:

            webbrowser.open(
                GITHUB_URL
            )

        except Exception as e:

            QMessageBox.warning(
                self,
                "GitHub",
                f"Не удалось открыть браузер:\n\n{e}"
            )

    # ========================================================
    # CHECK
    # ========================================================

    def check(self):

        self.info.setText(
            "🔎 Проверка GitHub..."
        )

        self.info_data = get_update_info(
            self.current_version
        )

        if not self.info_data:

            self.info.setText(
                "⚠️ Не удалось проверить GitHub."
            )

            self.notes.clear()

            return

        error = self.info_data.get(
            "error"
        )

        if error:

            self.info.setText(
                f"⚠️ {error}"
            )

            self.notes.clear()

            return

        # ----------------------------------------------------
        # NO UPDATE
        # ----------------------------------------------------

        if not self.info_data.get(
            "update_available",
            False
        ):

            self.info.setText(
                f"✅ Установлена последняя версия.\n\n"
                f"Текущая версия: "
                f"{self.current_version}"
            )

            self.notes.setPlainText(
                "Новых версий сейчас нет."
            )

            return

        # ----------------------------------------------------
        # UPDATE AVAILABLE
        # ----------------------------------------------------

        version = self.info_data.get(
            "version",
            "?"
        )

        release_name = self.info_data.get(
            "name",
            ""
        )

        self.info.setText(
            f"🚀 Доступна новая версия!\n\n"
            f"Текущая: "
            f"{self.current_version}\n"
            f"Новая: "
            f"{version}\n\n"
            f"{release_name}"
        )

        self.notes.setPlainText(
            self.info_data.get(
                "notes",
                ""
            )
        )

        self.update_button.setEnabled(
            True
        )

    # ========================================================
    # DOWNLOAD
    # ========================================================

    def download(self):

        if not self.info_data:

            return

        self.update_button.setEnabled(
            False
        )

        self.rollback_button.setEnabled(
            False
        )

        self.github_button.setEnabled(
            False
        )

        self.info.setText(
            "⬇ Скачивание обновления..."
        )

        self.progress.setValue(
            0
        )

        self.thread = DownloadThread(
            self.info_data
        )

        self.thread.progress.connect(
            self.progress.setValue
        )

        self.thread.finished.connect(
            self.download_finished
        )

        self.thread.error.connect(
            self.download_error
        )

        self.thread.start()

    # ========================================================
    # DOWNLOAD FINISHED
    # ========================================================

    def download_finished(
        self,
        path
    ):

        self.downloaded = Path(
            path
        )

        self.progress.setValue(
            100
        )

        new_version = self.info_data.get(
            "version",
            ""
        )

        try:

            backup = start_update(
                self.downloaded,
                new_version
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Обновление",
                f"❌ Не удалось начать обновление:\n\n{e}"
            )

            self.update_button.setEnabled(
                True
            )

            self.rollback_button.setEnabled(
                True
            )

            self.github_button.setEnabled(
                True
            )

            return

        QMessageBox.information(
            self,
            "Обновление",
            f"✅ Версия {new_version} подготовлена.\n\n"
            f"EZ Scan сейчас будет перезапущен.\n\n"
            f"Резервная копия:\n{backup}"
        )

        self.accept()

    # ========================================================
    # DOWNLOAD ERROR
    # ========================================================

    def download_error(
        self,
        message
    ):

        QMessageBox.critical(
            self,
            "Ошибка обновления",
            message
        )

        self.update_button.setEnabled(
            True
        )

        self.rollback_button.setEnabled(
            True
        )

        self.github_button.setEnabled(
            True
        )

    # ========================================================
    # ROLLBACK
    # ========================================================

    def rollback(self):

        answer = QMessageBox.question(
            self,
            "Откат",
            "Вернуть предыдущую версию EZ Scan?"
        )

        if answer != QMessageBox.Yes:

            return

        try:

            start_rollback()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Откат",
                f"❌ Ошибка отката:\n\n{e}"
            )

            return

        QMessageBox.information(
            self,
            "Откат",
            "✅ Будет запущена предыдущая версия."
        )

        self.accept()
