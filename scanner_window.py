from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QMessageBox
)

from PySide6.QtCore import Qt

from scanner import (
    get_scanner_devices,
    get_selected_scanner,
    set_selected_scanner,
    check_scanner_access,
    setup_scanner_permissions
)


class ScannerWindow(QDialog):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.setWindowTitle(
            "📷 QR-сканер"
        )

        self.resize(
            650,
            450
        )

        self.devices = []

        self.setup_ui()

        self.reload_devices()

    # ========================================================
    # UI
    # ========================================================

    def setup_ui(self):

        title = QLabel(
            "📷 Выбор QR-сканера"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
            }
            """
        )

        info = QLabel(
            "Выберите устройство, которое EZ SCAN "
            "будет использовать для чтения QR-кодов.\n\n"
            "Обычная клавиатура автоматически не выбирается "
            "после сохранения устройства."
        )

        info.setWordWrap(
            True
        )

        self.list = QListWidget()

        self.list.itemDoubleClicked.connect(
            self.select_device
        )

        self.status = QLabel(
            ""
        )

        self.status.setWordWrap(
            True
        )

        refresh = QPushButton(
            "🔄 Обновить"
        )

        refresh.clicked.connect(
            self.reload_devices
        )

        test = QPushButton(
            "🧪 Проверить"
        )

        test.clicked.connect(
            self.test_device
        )

        permissions = QPushButton(
            "🔐 Настроить доступ"
        )

        permissions.clicked.connect(
            self.setup_permissions
        )

        select = QPushButton(
            "💾 Использовать выбранный"
        )

        select.clicked.connect(
            self.select_device
        )

        close = QPushButton(
            "Закрыть"
        )

        close.clicked.connect(
            self.reject
        )

        buttons = QHBoxLayout()

        buttons.addWidget(
            refresh
        )

        buttons.addWidget(
            test
        )

        buttons.addWidget(
            permissions
        )

        buttons.addStretch()

        buttons.addWidget(
            select
        )

        buttons.addWidget(
            close
        )

        layout = QVBoxLayout()

        layout.addWidget(
            title
        )

        layout.addWidget(
            info
        )

        layout.addWidget(
            self.list
        )

        layout.addWidget(
            self.status
        )

        layout.addLayout(
            buttons
        )

        self.setLayout(
            layout
        )

    # ========================================================
    # RELOAD
    # ========================================================

    def reload_devices(self):

        self.list.clear()

        self.devices = (
            get_scanner_devices()
        )

        selected = (
            get_selected_scanner()
        )

        if not self.devices:

            item = QListWidgetItem(
                "❌ QR-сканеры не найдены"
            )

            item.setData(
                Qt.UserRole,
                None
            )

            self.list.addItem(
                item
            )

            self.status.setText(
                "Подключите сканер и нажмите "
                "«🔄 Обновить»."
            )

            return

        selected_row = -1

        for index, device in enumerate(
            self.devices
        ):

            path = device["path"]

            name = device["name"]

            accessible = device["accessible"]

            if path == selected:

                prefix = "● "

                selected_row = index

            else:

                prefix = ""

            if accessible:

                status = "✅"

            else:

                status = "🔐"

            text = (
                f"{prefix}{status} {name}\n"
                f"   {path}"
            )

            item = QListWidgetItem(
                text
            )

            item.setData(
                Qt.UserRole,
                path
            )

            self.list.addItem(
                item
            )

        if selected_row >= 0:

            self.list.setCurrentRow(
                selected_row
            )

            self.status.setText(
                "✅ Выбранный сканер найден."
            )

        else:

            self.list.setCurrentRow(
                0
            )

            self.status.setText(
                "Выберите сканер и нажмите "
                "«💾 Использовать выбранный»."
            )

    # ========================================================
    # CURRENT
    # ========================================================

    def current_path(self):

        item = self.list.currentItem()

        if not item:

            return None

        return item.data(
            Qt.UserRole
        )

    # ========================================================
    # TEST
    # ========================================================

    def test_device(self):

        path = self.current_path()

        if not path:

            QMessageBox.warning(
                self,
                "Сканер",
                "Сначала выберите устройство."
            )

            return

        try:

            from evdev import InputDevice

            device = InputDevice(
                path
            )

            name = device.name

            device.close()

            QMessageBox.information(
                self,
                "Сканер",
                f"✅ Устройство доступно.\n\n"
                f"Название:\n{name}\n\n"
                f"Путь:\n{path}"
            )

        except PermissionError:

            QMessageBox.warning(
                self,
                "Сканер",
                "🔐 Нет доступа к устройству.\n\n"
                "Используйте «🔐 Настроить доступ»."
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Сканер",
                f"❌ Ошибка:\n\n{e}"
            )

    # ========================================================
    # PERMISSIONS
    # ========================================================

    def setup_permissions(self):

        success, message = (
            setup_scanner_permissions()
        )

        if success:

            QMessageBox.information(
                self,
                "Доступ к сканеру",
                message
            )

        else:

            QMessageBox.warning(
                self,
                "Доступ к сканеру",
                message
            )

        self.reload_devices()

    # ========================================================
    # SELECT
    # ========================================================

    def select_device(self):

        path = self.current_path()

        if not path:

            QMessageBox.warning(
                self,
                "Сканер",
                "Сначала выберите устройство."
            )

            return

        set_selected_scanner(
            path
        )

        QMessageBox.information(
            self,
            "Сканер",
            "✅ Сканер сохранён.\n\n"
            "EZ SCAN теперь будет использовать "
            "именно это устройство."
        )

        self.reload_devices()