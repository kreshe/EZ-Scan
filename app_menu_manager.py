import os
import shutil
import subprocess
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QLineEdit
    
)


APP_NAME = "EZ Scan"

DESKTOP_ID = "ez-scan.desktop"

APPLICATIONS_DIR = (
    Path.home()
    / ".local"
    / "share"
    / "applications"
)

ICON_DIR = (
    Path.home()
    / ".local"
    / "share"
    / "icons"
    / "ez-scan"
)

ICON_FILE = ICON_DIR / "ez-scan.png"

DESKTOP_FILE = (
    APPLICATIONS_DIR
    / DESKTOP_ID
)


# ============================================================
# ПОИСК ТЕКУЩЕГО APPIMAGE
# ============================================================

def find_current_appimage():

    appimage_env = os.environ.get(
        "APPIMAGE"
    )

    if appimage_env:

        path = Path(
            appimage_env
        )

        if path.exists():

            return path.resolve()

    candidates = []

    search_dirs = [
        Path.cwd(),
        Path.home() / "Downloads",
        Path.home() / "Загрузки",
    ]

    for directory in search_dirs:

        if not directory.exists():

            continue

        try:

            for file in directory.glob(
                "*.AppImage"
            ):

                if not file.is_file():

                    continue

                if (
                    "EZ SCAN"
                    in file.name.upper()
                ):

                    candidates.append(
                        file
                    )

        except Exception:

            pass

    if not candidates:

        return None

    candidates.sort(
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )

    return candidates[0].resolve()


# ============================================================
# ИНСТАЛЛИРОВАНО ЛИ
# ============================================================

def is_installed():

    return DESKTOP_FILE.exists()


# ============================================================
# ПОИСК ИКОНКИ
# ============================================================

def find_icon(appimage_path=None):

    candidates = []

    if appimage_path:

        appimage_path = Path(
            appimage_path
        )

        candidates.extend([
            appimage_path.parent / "icon.png",
            appimage_path.parent / "icon.svg",
            appimage_path.parent / "ez-scan.png",
        ])

    candidates.extend([
        Path.cwd() / "icon.png",
        Path.cwd() / "icon.svg",
        Path.cwd() / "ez-scan.png",
    ])

    for icon in candidates:

        if icon.exists():

            return icon.resolve()

    return None


# ============================================================
# УСТАНОВКА ИКОНКИ
# ============================================================

def install_icon(
    icon_path
):

    if not icon_path:

        return None

    icon_path = Path(
        icon_path
    ).expanduser().resolve()

    if not icon_path.exists():

        return None

    ICON_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    try:

        shutil.copy2(
            icon_path,
            ICON_FILE
        )

        return ICON_FILE

    except Exception:

        return None


# ============================================================
# ОБНОВЛЕНИЕ МЕНЮ
# ============================================================

def refresh_menu():

    command = shutil.which(
        "update-desktop-database"
    )

    if not command:

        return

    try:

        subprocess.run(
            [
                command,
                str(APPLICATIONS_DIR)
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )

    except Exception:

        pass


# ============================================================
# СОЗДАНИЕ DESKTOP
# ============================================================

def create_desktop_file(
    appimage_path
):

    appimage_path = Path(
        appimage_path
    ).resolve()

    APPLICATIONS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    content = f"""[Desktop Entry]
Type=Application
Name=EZ Scan
GenericName=QR Code Sender
Comment=Буферизация и автоматическая отправка QR-кодов
Exec="{appimage_path}"
Icon={ICON_FILE}
Terminal=false
Categories=Utility;
StartupNotify=true
StartupWMClass=EZ-SCAN
"""

    DESKTOP_FILE.write_text(
        content,
        encoding="utf-8"
    )


# ============================================================
# ДОБАВИТЬ В МЕНЮ
# ============================================================

def add_to_menu(
    appimage_path,
    icon_path=None
):

    appimage_path = Path(
        appimage_path
    ).expanduser().resolve()

    if not appimage_path.exists():

        return (
            False,
            "AppImage не найден."
        )

    if not appimage_path.is_file():

        return (
            False,
            "Указанный путь не является файлом."
        )

    if (
        not appimage_path.name
        .lower()
        .endswith(".appimage")
    ):

        return (
            False,
            "Выбранный файл не является AppImage."
        )

    # --------------------------------------------------------
    # Делаем AppImage исполняемым
    # --------------------------------------------------------

    try:

        current_mode = (
            appimage_path.stat().st_mode
        )

        os.chmod(
            appimage_path,
            current_mode | 0o111
        )

    except Exception as e:

        return (
            False,
            f"Не удалось сделать AppImage "
            f"исполняемым:\n{e}"
        )

    # --------------------------------------------------------
    # Иконка
    # --------------------------------------------------------

    if icon_path is None:

        icon_path = find_icon(
            appimage_path
        )

    installed_icon = install_icon(
        icon_path
    )

    if installed_icon is None:

        return (
            False,
            "Не удалось установить иконку."
        )

    # --------------------------------------------------------
    # Desktop
    # --------------------------------------------------------

    try:

        create_desktop_file(
            appimage_path
        )

    except Exception as e:

        return (
            False,
            f"Не удалось создать desktop-файл:\n{e}"
        )

    refresh_menu()

    return (
        True,
        f"EZ Scan добавлен в меню.\n\n"
        f"AppImage:\n{appimage_path}\n\n"
        f"Иконка:\n{installed_icon}"
    )


# ============================================================
# УДАЛЕНИЕ
# ============================================================

def remove_from_menu():

    removed = False

    if DESKTOP_FILE.exists():

        try:

            DESKTOP_FILE.unlink()

            removed = True

        except Exception as e:

            return (
                False,
                f"Не удалось удалить запись:\n{e}"
            )

    if ICON_DIR.exists():

        try:

            shutil.rmtree(
                ICON_DIR
            )

        except Exception:

            pass

    refresh_menu()

    if removed:

        return (
            True,
            "EZ Scan удалён из меню приложений."
        )

    return (
        False,
        "EZ Scan уже отсутствует в меню."
    )


# ============================================================
# ТЕКУЩИЙ APPIMAGE ИЗ DESKTOP
# ============================================================

def get_installed_appimage():

    if not DESKTOP_FILE.exists():

        return None

    try:

        text = DESKTOP_FILE.read_text(
            encoding="utf-8"
        )

    except Exception:

        return None

    for line in text.splitlines():

        line = line.strip()

        if line.startswith(
            "Exec="
        ):

            path = line[5:].strip()

            if (
                path.startswith('"')
                and
                path.endswith('"')
            ):

                path = path[1:-1]

            result = Path(
                path
            )

            if result.exists():

                return result

    return None


# ============================================================
# GUI
# ============================================================

class AppMenuManager(QDialog):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.selected_appimage = None
        self.selected_icon = None

        self.setWindowTitle(
            "🖥 EZ Scan — меню Ubuntu"
        )

        self.resize(
            560,
            360
        )

        self.setup_ui()

        self.update_status()

    # ========================================================
    # UI
    # ========================================================

    def setup_ui(self):

        title = QLabel(
            "🖥 Управление EZ Scan в меню Ubuntu"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 8px;
            }
            """
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        status_group = QGroupBox(
            "Состояние"
        )

        status_layout = QVBoxLayout()

        self.status = QLabel()

        self.status.setWordWrap(
            True
        )

        status_layout.addWidget(
            self.status
        )

        status_group.setLayout(
            status_layout
        )

        # ----------------------------------------------------
        # APPIMAGE
        # ----------------------------------------------------

        self.path_edit = QLineEdit()

        self.path_edit.setReadOnly(
            True
        )

        self.path_edit.setPlaceholderText(
            "AppImage не выбран"
        )

        browse_button = QPushButton(
            "📂 Выбрать"
        )

        browse_button.clicked.connect(
            self.select_appimage
        )

        path_layout = QHBoxLayout()

        path_layout.addWidget(
            self.path_edit
        )

        path_layout.addWidget(
            browse_button
        )

        # ----------------------------------------------------
        # ICON
        # ----------------------------------------------------

        self.icon_edit = QLineEdit()

        self.icon_edit.setReadOnly(
            True
        )

        self.icon_edit.setPlaceholderText(
            "Иконка не выбрана"
        )

        icon_button = QPushButton(
            "🖼 Иконка"
        )

        icon_button.clicked.connect(
            self.select_icon
        )

        icon_layout = QHBoxLayout()

        icon_layout.addWidget(
            self.icon_edit
        )

        icon_layout.addWidget(
            icon_button
        )

        # ----------------------------------------------------
        # BUTTONS
        # ----------------------------------------------------

        self.add_button = QPushButton(
            "➕ Добавить / обновить"
        )

        self.add_button.clicked.connect(
            self.add_app
        )

        self.remove_button = QPushButton(
            "🗑 Удалить"
        )

        self.remove_button.clicked.connect(
            self.remove_app
        )

        refresh_button = QPushButton(
            "🔄 Обновить"
        )

        refresh_button.clicked.connect(
            self.update_status
        )

        close_button = QPushButton(
            "Закрыть"
        )

        close_button.clicked.connect(
            self.accept
        )

        buttons = QHBoxLayout()

        buttons.addWidget(
            self.add_button
        )

        buttons.addWidget(
            self.remove_button
        )

        buttons.addWidget(
            refresh_button
        )

        buttons.addWidget(
            close_button
        )

        # ----------------------------------------------------
        # LAYOUT
        # ----------------------------------------------------

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
            status_group
        )

        layout.addWidget(
            QLabel(
                "AppImage:"
            )
        )

        layout.addLayout(
            path_layout
        )

        layout.addWidget(
            QLabel(
                "Иконка:"
            )
        )

        layout.addLayout(
            icon_layout
        )

        layout.addStretch()

        layout.addLayout(
            buttons
        )

        self.setLayout(
            layout
        )

    # ========================================================
    # STATUS
    # ========================================================

    def update_status(self):

        installed = is_installed()

        installed_appimage = (
            get_installed_appimage()
        )

        if installed:

            text = (
                "🟢 EZ Scan добавлен в меню приложений."
            )

            if installed_appimage:

                text += (
                    "\n\n"
                    f"AppImage:\n{installed_appimage}"
                )

            self.status.setStyleSheet(
                "color: green;"
            )

            self.status.setText(
                text
            )

        else:

            self.status.setStyleSheet(
                "color: #666;"
            )

            self.status.setText(
                "⚪ EZ Scan не добавлен "
                "в меню приложений."
            )

        # ----------------------------------------------------
        # AppImage
        # ----------------------------------------------------

        if not self.selected_appimage:

            current = (
                installed_appimage
                or
                find_current_appimage()
            )

            if current:

                self.selected_appimage = current

                self.path_edit.setText(
                    str(current)
                )

        # ----------------------------------------------------
        # Icon
        # ----------------------------------------------------

        if not self.selected_icon:

            icon = find_icon(
                self.selected_appimage
            )

            if icon:

                self.selected_icon = icon

                self.icon_edit.setText(
                    str(icon)
                )

    # ========================================================
    # SELECT APPIMAGE
    # ========================================================

    def select_appimage(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите EZ Scan AppImage",
            str(
                Path.home()
            ),
            "AppImage (*.AppImage)"
        )

        if not path:

            return

        self.selected_appimage = Path(
            path
        ).resolve()

        self.path_edit.setText(
            str(
                self.selected_appimage
            )
        )

        icon = find_icon(
            self.selected_appimage
        )

        if icon:

            self.selected_icon = icon

            self.icon_edit.setText(
                str(icon)
            )

    # ========================================================
    # SELECT ICON
    # ========================================================

    def select_icon(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите иконку EZ Scan",
            str(
                Path.home()
            ),
            "Images (*.png *.svg *.xpm)"
        )

        if not path:

            return

        self.selected_icon = Path(
            path
        ).resolve()

        self.icon_edit.setText(
            str(
                self.selected_icon
            )
        )

    # ========================================================
    # ADD
    # ========================================================

    def add_app(self):

        appimage = (
            self.selected_appimage
            or
            find_current_appimage()
        )

        if not appimage:

            QMessageBox.warning(
                self,
                "EZ Scan",
                "AppImage не найден.\n\n"
                "Выберите AppImage вручную."
            )

            self.select_appimage()

            appimage = (
                self.selected_appimage
            )

            if not appimage:

                return

        icon = (
            self.selected_icon
            or
            find_icon(
                appimage
            )
        )

        success, message = add_to_menu(
            appimage,
            icon
        )

        if success:

            QMessageBox.information(
                self,
                "EZ Scan",
                "✅ " + message
            )

            self.update_status()

        else:

            QMessageBox.critical(
                self,
                "EZ Scan",
                "❌ " + message
            )

    # ========================================================
    # REMOVE
    # ========================================================

    def remove_app(self):

        if not is_installed():

            QMessageBox.information(
                self,
                "EZ Scan",
                "EZ Scan уже отсутствует "
                "в меню приложений."
            )

            return

        answer = QMessageBox.question(
            self,
            "Удаление",
            "Удалить EZ Scan из меню приложений?"
        )

        if answer != QMessageBox.Yes:

            return

        success, message = (
            remove_from_menu()
        )

        if success:

            QMessageBox.information(
                self,
                "EZ Scan",
                "✅ " + message
            )

        else:

            QMessageBox.warning(
                self,
                "EZ Scan",
                message
            )

        self.update_status()


# ============================================================
# DIRECT START
# ============================================================

def main():

    app = QApplication([])

    window = AppMenuManager()

    window.exec()


if __name__ == "__main__":

    main()