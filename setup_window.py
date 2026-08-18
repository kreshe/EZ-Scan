import os
import glob
import shutil
import subprocess

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QProgressBar,
    QMessageBox,
    QGroupBox
)

from PySide6.QtCore import Qt

from scanner import (
    find_scanners,
    check_scanner_access,
    user_in_input_group,
    setup_scanner_permissions
)


class SetupWindow(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle(
            "🛠 EZ Scan — первоначальная настройка"
        )

        self.resize(
            600,
            500
        )

        self.setModal(True)

        self.setup_ui()

        self.run_check()

    # ============================================================
    # UI
    # ============================================================

    def setup_ui(self):

        title = QLabel(
            "🚀 Добро пожаловать в EZ Scan"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 22px;
                font-weight: bold;
                padding: 8px;
            }
            """
        )

        self.info = QLabel(
            "Проверяем систему..."
        )

        self.info.setWordWrap(
            True
        )

        # --------------------------------------------------------
        # STATUS
        # --------------------------------------------------------

        status_group = QGroupBox(
            "🔎 Проверка системы"
        )

        status_layout = QVBoxLayout()

        self.python_status = QLabel(
            "⏳ Python-зависимости..."
        )

        self.xdotool_status = QLabel(
            "⏳ xdotool..."
        )

        self.input_status = QLabel(
            "⏳ Доступ к input..."
        )

        self.scanner_status = QLabel(
            "⏳ QR-сканер..."
        )

        for widget in (
            self.python_status,
            self.xdotool_status,
            self.input_status,
            self.scanner_status
        ):

            widget.setStyleSheet(
                """
                QLabel {
                    font-size: 13px;
                    padding: 3px;
                }
                """
            )

            status_layout.addWidget(
                widget
            )

        status_group.setLayout(
            status_layout
        )

        # --------------------------------------------------------
        # LOG
        # --------------------------------------------------------

        self.log = QTextEdit()

        self.log.setReadOnly(
            True
        )

        self.log.setPlaceholderText(
            "Информация о проверке..."
        )

        # --------------------------------------------------------
        # PROGRESS
        # --------------------------------------------------------

        self.progress = QProgressBar()

        self.progress.setRange(
            0,
            100
        )

        # --------------------------------------------------------
        # BUTTONS
        # --------------------------------------------------------

        self.fix_button = QPushButton(
            "🔐 Настроить доступ к сканеру"
        )

        self.fix_button.clicked.connect(
            self.fix_permissions
        )

        self.fix_button.setVisible(
            False
        )

        self.refresh_button = QPushButton(
            "🔄 Проверить снова"
        )

        self.refresh_button.clicked.connect(
            self.run_check
        )

        self.continue_button = QPushButton(
            "🚀 Запустить EZ Scan"
        )

        self.continue_button.clicked.connect(
            self.accept
        )

        self.continue_button.setEnabled(
            False
        )

        # --------------------------------------------------------
        # LAYOUT
        # --------------------------------------------------------

        buttons = QHBoxLayout()

        buttons.addWidget(
            self.fix_button
        )

        buttons.addStretch()

        buttons.addWidget(
            self.refresh_button
        )

        buttons.addWidget(
            self.continue_button
        )

        layout = QVBoxLayout()

        layout.setContentsMargins(
            15,
            15,
            15,
            15
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            self.info
        )

        layout.addWidget(
            status_group
        )

        layout.addWidget(
            self.progress
        )

        layout.addWidget(
            self.log
        )

        layout.addLayout(
            buttons
        )

        self.setLayout(
            layout
        )

    # ============================================================
    # LOG
    # ============================================================

    def write(self, text):

        self.log.append(
            str(text)
        )

        self.log.ensureCursorVisible()

    # ============================================================
    # COMMAND
    # ============================================================

    def command_exists(self, command):

        return shutil.which(
            command
        ) is not None

    # ============================================================
    # PYTHON
    # ============================================================

    def check_python(self):

        modules = {
            "PySide6": "PySide6",
            "evdev": "evdev",
            "pyperclip": "pyperclip"
        }

        missing = []

        for name, module in modules.items():

            try:

                __import__(
                    module
                )

                self.write(
                    f"✅ {name}"
                )

            except ImportError:

                self.write(
                    f"❌ {name}"
                )

                missing.append(
                    name
                )

        return missing

    # ============================================================
    # XDOTOOL
    # ============================================================

    def check_xdotool(self):

        if self.command_exists(
            "xdotool"
        ):

            self.xdotool_status.setText(
                "✅ xdotool найден"
            )

            self.xdotool_status.setStyleSheet(
                "color: green; font-size: 13px;"
            )

            return True

        self.xdotool_status.setText(
            "❌ xdotool не найден"
        )

        self.xdotool_status.setStyleSheet(
            "color: red; font-size: 13px;"
        )

        self.write(
            "❌ xdotool отсутствует"
        )

        return False

    # ============================================================
    # INSTALL XDOTOOL
    # ============================================================

    def install_xdotool(self):

        if self.command_exists(
            "pkexec"
        ):

            self.write(
                "🔐 Запрашиваем права администратора..."
            )

            result = subprocess.run(
                [
                    "pkexec",
                    "apt",
                    "update"
                ]
            )

            if result.returncode != 0:

                return False

            result = subprocess.run(
                [
                    "pkexec",
                    "apt",
                    "install",
                    "-y",
                    "xdotool"
                ]
            )

            return result.returncode == 0

        return False

    # ============================================================
    # INPUT
    # ============================================================

    def check_input(self):

        if user_in_input_group():

            self.input_status.setText(
                "✅ Доступ к input настроен"
            )

            self.input_status.setStyleSheet(
                "color: green; font-size: 13px;"
            )

            return True

        self.input_status.setText(
            "❌ Нет группы input"
        )

        self.input_status.setStyleSheet(
            "color: red; font-size: 13px;"
        )

        return False

    # ============================================================
    # SCANNER
    # ============================================================

    def check_scanner(self):

        scanners = find_scanners()

        access = check_scanner_access()

        if not scanners:

            self.scanner_status.setText(
                "⚠ QR-сканер не найден"
            )

            self.scanner_status.setStyleSheet(
                "color: #d97706; font-size: 13px;"
            )

            self.write(
                "⚠ Подключённый QR-сканер не найден."
            )

            self.write(
                "Подключите сканер и нажмите "
                "«Проверить снова»."
            )

            return False

        self.write(
            f"🔎 Найдено подходящих устройств: "
            f"{len(scanners)}"
        )

        for scanner in scanners:

            name = scanner.get(
                "name",
                "Неизвестное устройство"
            )

            path = (
                scanner.get("link")
                or
                scanner.get("path")
            )

            self.write(
                f"   • {name}"
            )

            self.write(
                f"     {path}"
            )

        if access.get(
            "access",
            False
        ):

            self.scanner_status.setText(
                "✅ QR-сканер найден и доступен"
            )

            self.scanner_status.setStyleSheet(
                "color: green; font-size: 13px;"
            )

            return True

        self.scanner_status.setText(
            "❌ Сканер найден, но нет доступа"
        )

        self.scanner_status.setStyleSheet(
            "color: red; font-size: 13px;"
        )

        return False

    # ============================================================
    # FIX PERMISSIONS
    # ============================================================

    def fix_permissions(self):

        self.fix_button.setEnabled(
            False
        )

        self.write(
            ""
        )

        self.write(
            "🔐 Настраиваем права доступа..."
        )

        result = setup_scanner_permissions()

        if not result.get(
            "success",
            False
        ):

            QMessageBox.critical(
                self,
                "Ошибка",
                result.get(
                    "message",
                    "Не удалось настроить доступ."
                )
            )

            self.fix_button.setEnabled(
                True
            )

            return

        self.write(
            "✅ "
            + result.get(
                "message",
                "Права настроены."
            )
        )

        if result.get(
            "restart_required",
            False
        ):

            QMessageBox.information(
                self,
                "Перезапуск сеанса",
                "Пользователь добавлен в группу input.\n\n"
                "Для применения новых прав необходимо "
                "выйти из системы и войти снова.\n\n"
                "После этого запустите EZ Scan повторно."
            )

            self.reject()

            return

        self.run_check()

    # ============================================================
    # MAIN CHECK
    # ============================================================

    def run_check(self):

        self.log.clear()

        self.progress.setValue(
            5
        )

        self.continue_button.setEnabled(
            False
        )

        self.fix_button.setVisible(
            False
        )

        # --------------------------------------------------------
        # PYTHON
        # --------------------------------------------------------

        self.write(
            "🔎 Проверяем Python..."
        )

        missing = self.check_python()

        if missing:

            self.python_status.setText(
                "❌ Не хватает: "
                + ", ".join(missing)
            )

            self.python_status.setStyleSheet(
                "color: red; font-size: 13px;"
            )

            self.info.setText(
                "❌ В приложении отсутствуют "
                "необходимые Python-зависимости."
            )

            QMessageBox.critical(
                self,
                "Отсутствуют зависимости",
                "Не найдены:\n\n"
                + "\n".join(
                    f"• {x}"
                    for x in missing
                )
            )

            return

        self.python_status.setText(
            "✅ Python-зависимости"
        )

        self.python_status.setStyleSheet(
            "color: green; font-size: 13px;"
        )

        self.progress.setValue(
            25
        )

        # --------------------------------------------------------
        # XDOTOOL
        # --------------------------------------------------------

        xdotool_ok = self.check_xdotool()

        self.progress.setValue(
            45
        )

        if not xdotool_ok:

            answer = QMessageBox.question(
                self,
                "Установка xdotool",
                "xdotool не найден.\n\n"
                "Установить его автоматически?"
            )

            if answer == QMessageBox.Yes:

                if self.install_xdotool():

                    self.write(
                        "✅ xdotool установлен."
                    )

                    xdotool_ok = True

                else:

                    self.write(
                        "❌ Установка xdotool не удалась."
                    )

            if not xdotool_ok:

                return

            self.check_xdotool()

        # --------------------------------------------------------
        # INPUT
        # --------------------------------------------------------

        input_ok = self.check_input()

        self.progress.setValue(
            65
        )

        if not input_ok:

            self.fix_button.setVisible(
                True
            )

            self.info.setText(
                "⚠ Не настроен доступ к устройствам input."
            )

            return

        # --------------------------------------------------------
        # SCANNER
        # --------------------------------------------------------

        scanner_ok = self.check_scanner()

        self.progress.setValue(
            90
        )

        # --------------------------------------------------------
        # FINISH
        # --------------------------------------------------------

        if scanner_ok:

            self.progress.setValue(
                100
            )

            self.info.setText(
                "✅ Всё готово. EZ Scan можно запускать."
            )

            self.continue_button.setEnabled(
                True
            )

        else:

            self.progress.setValue(
                90
            )

            self.info.setText(
                "⚠ Подключите QR-сканер и "
                "повторите проверку."
            )

            # Сканер не блокирует приложение.
            # Можно продолжить и подключить его позже.
            self.continue_button.setEnabled(
                True
            )