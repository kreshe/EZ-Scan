from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QInputDialog,
    QMessageBox
)

from profiles import (
    get_profiles,
    get_active_profile,
    create_profile,
    load_profile,
    delete_profile,
    save_current_to_profile,
    rename_profile
)


class ProfileWindow(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle(
            "👤 Профили"
        )

        self.resize(
            350,
            300
        )

        # ====================================================
        # СПИСОК
        # ====================================================

        self.list = QListWidget()

        self.reload()

        # ====================================================
        # КНОПКИ
        # ====================================================

        create_btn = QPushButton(
            "➕ Новый"
        )

        rename_btn = QPushButton(
            "✏️ Переименовать"
        )

        save_btn = QPushButton(
            "💾 Сохранить"
        )

        load_btn = QPushButton(
            "▶ Загрузить"
        )

        delete_btn = QPushButton(
            "🗑 Удалить"
        )

        # ----------------------------------------------------
        # Подключение
        # ----------------------------------------------------

        create_btn.clicked.connect(
            self.create
        )

        rename_btn.clicked.connect(
            self.rename
        )

        save_btn.clicked.connect(
            self.save_current
        )

        load_btn.clicked.connect(
            self.load
        )

        delete_btn.clicked.connect(
            self.delete
        )

        # ====================================================
        # ПЕРВАЯ СТРОКА
        # ====================================================

        row1 = QHBoxLayout()

        row1.setSpacing(
            6
        )

        row1.addWidget(
            create_btn
        )

        row1.addWidget(
            rename_btn
        )

        # ====================================================
        # ВТОРАЯ СТРОКА
        # ====================================================

        row2 = QHBoxLayout()

        row2.setSpacing(
            6
        )

        row2.addWidget(
            save_btn
        )

        row2.addWidget(
            load_btn
        )

        # ====================================================
        # ТРЕТЬЯ СТРОКА
        # ====================================================

        row3 = QHBoxLayout()

        row3.setSpacing(
            6
        )

        row3.addWidget(
            delete_btn
        )

        # ====================================================
        # ОСНОВНОЙ LAYOUT
        # ====================================================

        layout = QVBoxLayout()

        layout.setContentsMargins(
            8,
            8,
            8,
            8
        )

        layout.setSpacing(
            6
        )

        layout.addWidget(
            self.list
        )

        layout.addLayout(
            row1
        )

        layout.addLayout(
            row2
        )

        layout.addLayout(
            row3
        )

        self.setLayout(
            layout
        )

    # ========================================================
    # ОБНОВЛЕНИЕ СПИСКА
    # ========================================================

    def reload(self):

        self.list.clear()

        profiles = get_profiles()

        active = get_active_profile()

        for name in profiles:

            item = QListWidgetItem(
                name
            )

            if name == active:

                item.setText(
                    f"● {name}"
                )

            self.list.addItem(
                item
            )

    # ========================================================
    # ВЫБРАННЫЙ ПРОФИЛЬ
    # ========================================================

    def selected_name(self):

        item = self.list.currentItem()

        if not item:

            return None

        name = item.text()

        if name.startswith("● "):

            name = name[2:]

        return name

    # ========================================================
    # СОЗДАНИЕ
    # ========================================================

    def create(self):

        name, ok = QInputDialog.getText(
            self,
            "Новый профиль",
            "Название профиля:"
        )

        if not ok:

            return

        name = name.strip()

        if not name:

            return

        if not create_profile(
            name
        ):

            QMessageBox.warning(
                self,
                "Профиль",
                "Такой профиль уже существует."
            )

            return

        self.reload()

    # ========================================================
    # СОХРАНЕНИЕ ТЕКУЩИХ НАСТРОЕК
    # ========================================================

    def save_current(self):

        name = self.selected_name()

        if not name:

            QMessageBox.warning(
                self,
                "Профиль",
                "Сначала выберите профиль."
            )

            return

        save_current_to_profile(
            name
        )

        QMessageBox.information(
            self,
            "Профиль",
            f"✅ Текущие настройки сохранены в профиль:\n\n"
            f"«{name}»"
        )

        self.reload()

    # ========================================================
    # ЗАГРУЗКА
    # ========================================================

    def load(self):

        name = self.selected_name()

        if not name:

            QMessageBox.warning(
                self,
                "Профиль",
                "Сначала выберите профиль."
            )

            return

        if load_profile(
            name
        ):

            QMessageBox.information(
                self,
                "Профиль",
                f"✅ Профиль «{name}» загружен."
            )

            self.accept()

    # ========================================================
    # УДАЛЕНИЕ
    # ========================================================

    def delete(self):

        name = self.selected_name()

        if not name:

            QMessageBox.warning(
                self,
                "Профиль",
                "Сначала выберите профиль."
            )

            return

        if name == "По умолчанию":

            QMessageBox.warning(
                self,
                "Профиль",
                "Профиль «По умолчанию» удалить нельзя."
            )

            return

        answer = QMessageBox.question(
            self,
            "Удаление",
            f"Удалить профиль «{name}»?"
        )

        if answer != QMessageBox.Yes:

            return

        delete_profile(
            name
        )

        self.reload()

    # ========================================================
    # ПЕРЕИМЕНОВАНИЕ
    # ========================================================

    def rename(self):

        old_name = self.selected_name()

        if not old_name:

            QMessageBox.warning(
                self,
                "Профиль",
                "Сначала выберите профиль."
            )

            return

        # ----------------------------------------------------
        # Базовый профиль не переименовываем
        # ----------------------------------------------------

        if old_name == "По умолчанию":

            QMessageBox.warning(
                self,
                "Профиль",
                "Профиль «По умолчанию» переименовать нельзя."
            )

            return

        # ----------------------------------------------------
        # Новое имя
        # ----------------------------------------------------

        new_name, ok = QInputDialog.getText(
            self,
            "Переименование профиля",
            "Новое название:",
            text=old_name
        )

        if not ok:

            return

        new_name = new_name.strip()

        if not new_name:

            QMessageBox.warning(
                self,
                "Профиль",
                "Название не может быть пустым."
            )

            return

        if new_name == old_name:

            return

        # ----------------------------------------------------
        # Переименование
        # ----------------------------------------------------

        if not rename_profile(
            old_name,
            new_name
        ):

            QMessageBox.warning(
                self,
                "Профиль",
                f"Профиль «{new_name}» уже существует."
            )

            return

        QMessageBox.information(
            self,
            "Профиль",
            f"✅ Профиль переименован:\n\n"
            f"«{old_name}» → «{new_name}»"
        )

        self.reload()