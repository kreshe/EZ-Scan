from PySide6.QtWidgets import *
from config import load, save
from trainer import Trainer
from PySide6.QtGui import QKeySequence
from guide import GuideWindow
from version import VERSION
from update_window import UpdateWindow
class Settings(QDialog):

    def __init__(self):

        super().__init__()

        self.cfg = load()
        
        self.profile_name = self.cfg.get(
            "active_profile",
            "По умолчанию"
        )

        self.profile = self.cfg["profiles"].get(
            self.profile_name
        )

        if self.profile is None:

            self.profile_name = "По умолчанию"

            self.profile = self.cfg["profiles"][
                self.profile_name
            ]
        self.setWindowTitle(
            "⚙ Настройки"
        )

        self.resize(
            500,
            500
        )

        tabs = QTabWidget()

        tabs.addTab(
            self.general_tab(),
            "🔎 Основные"
        )

        tabs.addTab(
            self.delay_tab(),
            "🕒 Тайминги"
        )

        tabs.addTab(
            self.trainer_tab(),
            "🎯 Тренер"
        )

        tabs.addTab(
            self.hotkey_tab(),
            "⌨ Клавиши"
        )

        save_btn = QPushButton(
            "💾 Сохранить"
        )

        save_btn.clicked.connect(
            self.save_settings
        )

        cancel_btn = QPushButton(
            "Отмена"
        )

        cancel_btn.clicked.connect(
            self.reject
        )

        buttons = QHBoxLayout()

        buttons.addWidget(
            save_btn
        )

        buttons.addWidget(
            cancel_btn
        )

        layout = QVBoxLayout()

        layout.addWidget(
            tabs
        )

        layout.addLayout(
            buttons
        )

        self.setLayout(
            layout
        )
    def check_updates(self):

        dialog = UpdateWindow(
            VERSION,
            self
        )

        dialog.exec()
    def check_updates_on_startup(self):

        try:

            if not should_check_updates():

                return

            from updater import get_update_info

            info = get_update_info(
                VERSION
            )

            if not info:

                return

            if not info.get(
                "update_available",
                False
            ):

                return

            dialog = UpdateWindow(
                VERSION,
                self
            )

            dialog.exec()

        except Exception as e:

            print(
                "Ошибка автоматической проверки обновлений:",
                e
            )
    def open_guide(self):

        dialog = GuideWindow(
            self
        )

        dialog.exec()
    # ==================================================
    # ОСНОВНЫЕ
    # ==================================================

    def general_tab(self):

        w = QWidget()

        layout = QFormLayout()

        self.buffer = QSpinBox()

        self.buffer.setRange(
            1,
            500
        )

        self.buffer.setValue(
            self.profile["buffer_size"]
        )


        self.batch = QSpinBox()

        self.batch.setRange(
            1,
            100
        )

        self.batch.setValue(
            self.profile["batch_size"]
        )


        self.auto = QCheckBox(
            "Автоматическая отправка"
        )

        self.auto.setChecked(
            self.profile["auto_send"]
        )


        self.enter = QCheckBox(
            "Нажимать Enter после QR"
        )

        self.enter.setChecked(
            self.profile["press_enter"]
        )


        layout.addRow(
            "Размер буфера:",
            self.buffer
        )

        layout.addRow(
            "Размер пачки:",
            self.batch
        )

        layout.addRow(
            self.auto
        )

        layout.addRow(
            self.enter
        )


        guide_btn = QPushButton(
            "📖 Открыть инструкцию"
        )

        guide_btn.clicked.connect(
            self.open_guide
        )

        layout.addRow(
            guide_btn
        )

        update_btn = QPushButton(
            "🔄 Проверить обновления"
        )

        update_btn.clicked.connect(
            self.check_updates
        )

        layout.addRow(
            update_btn
        )
        
        w.setLayout(
            layout
        )

        return w

    # ==================================================
    # ТАЙМИНГИ
    # ==================================================

    def delay_tab(self):

        w = QWidget()

        layout = QFormLayout()

        self.delay = {}

        delay_names = {

            "click":
                "🖱 После клика:",

            "paste":
                "📋 После вставки QR:",

            "enter":
                "↵ Перед Enter:",

            "before_buttons":
                "⏳ Перед кнопками:",

            "button_click":
                "🔘 Между кнопками:",

            "after_batch":
                "📦 После пачки:",

            "after_buttons":
                "⏱ После кнопок:",

            "between_batches":
                "🔄 Между пачками:"
        }

        for key, value in self.profile.get(
            "delays",
            {}
        ).items():

            spin = QDoubleSpinBox()

            spin.setRange(
                0,
                60
            )

            spin.setSingleStep(
                0.1
            )

            spin.setDecimals(
                2
            )

            spin.setSuffix(
                " сек."
            )

            spin.setValue(
                value
            )

            self.delay[key] = spin

            layout.addRow(
                delay_names.get(
                    key,
                    key
                ),
                spin
            )

        info = QLabel(
            "💡 Настройте паузы между действиями автоматической отправки."
        )

        info.setWordWrap(
            True
        )

        layout.addRow(
            info
        )

        w.setLayout(
            layout
        )

        return w

    # ==================================================
    # ТРЕНЕР
    # ==================================================

    def trainer_tab(self):

        w = QWidget()

        layout = QVBoxLayout()

        info = QLabel(
            "🎯 Обучение координат мыши\n\n"
            "• Дважды нажмите действие для обучения\n"
            "• Используйте ➕ для добавления\n"
            "• Используйте 🗑 для удаления\n"
            "• Используйте ⬆ ⬇ для изменения порядка"
        )

        layout.addWidget(
            info
        )

        # Передаём ОДИН И ТОТ ЖЕ конфиг
        profile_name = self.cfg.get(
            "active_profile",
            "По умолчанию"
        )

        profile = self.cfg.setdefault(
            "profiles",
            {}
        ).setdefault(
            profile_name,
            {}
        )

        self.trainer = Trainer(
            profile
        )
        layout.addWidget(
            self.trainer
        )

        w.setLayout(
            layout
        )

        return w


    # ==================================================
    # ГОРЯЧИЕ КЛАВИШИ
    # ==================================================
    def hotkey_tab(self):

        w = QWidget()

        layout = QFormLayout()

        self.hotkey_widgets = {}

        hotkey_names = {

            "send": "▶ Отправить",

            "stop": "⏹ Стоп",

            "clear": "🗑 Очистить",

            "auto": "⚡ Авто",

            "settings": "⚙ Настройки",

            "profile": "👤 Профиль"
        }

        hotkeys = self.cfg.setdefault(
            "hotkeys",
            {}
        )

        for key, title in hotkey_names.items():

            edit = QKeySequenceEdit()

            edit.setKeySequence(
                QKeySequence(
                    hotkeys.get(
                        key,
                        ""
                    )
                )
            )

            self.hotkey_widgets[key] = edit

            layout.addRow(
                title + ":",
                edit
            )

        info = QLabel(
            "💡 Нажмите на поле и назначьте нужную клавишу."
        )

        layout.addRow(
            info
        )

        w.setLayout(
            layout
        )

        return w


    # ==================================================
    # СОХРАНЕНИЕ
    # ==================================================

    def save_settings(self):

        try:

            # ==================================================
            # АКТИВНЫЙ ПРОФИЛЬ
            # ==================================================

            self.cfg.setdefault(
                "profiles",
                {}
            )

            profile_name = self.cfg.get(
                "active_profile",
                "По умолчанию"
            )

            # Если профиль каким-то образом отсутствует —
            # создаём его
            self.cfg["profiles"].setdefault(
                profile_name,
                {}
            )

            profile = self.cfg["profiles"][profile_name]

            # ==================================================
            # ОСНОВНЫЕ НАСТРОЙКИ ПРОФИЛЯ
            # ==================================================

            profile["buffer_size"] = (
                self.buffer.value()
            )

            profile["batch_size"] = (
                self.batch.value()
            )

            profile["auto_send"] = (
                self.auto.isChecked()
            )

            profile["press_enter"] = (
                self.enter.isChecked()
            )

            # ==================================================
            # ТАЙМИНГИ
            # ==================================================

            profile.setdefault(
                "delays",
                {}
            )

            for key, widget in self.delay.items():

                profile["delays"][key] = (
                    widget.value()
                )

            # ==================================================
            # TRAINER
            # ==================================================

            profile.setdefault(
                "workflow",
                {}
            )

            profile.setdefault(
                "positions",
                {}
            )

            profile["workflow"]["input_stage"] = list(
                self.trainer.cfg["workflow"].get(
                    "input_stage",
                    []
                )
            )

            profile["workflow"]["button_stage"] = list(
                self.trainer.cfg["workflow"].get(
                    "button_stage",
                    []
                )
            )

            profile["positions"] = dict(
                self.trainer.cfg.get(
                    "positions",
                    {}
                )
            )

            # ==================================================
            # ГОРЯЧИЕ КЛАВИШИ
            # ==================================================

            self.cfg.setdefault(
                "hotkeys",
                {}
            )

            for key, widget in self.hotkey_widgets.items():

                self.cfg["hotkeys"][key] = (
                    widget.keySequence().toString()
                )

            # ==================================================
            # СОХРАНЯЕМ ИМЕННО ПРОФИЛЬ
            # ==================================================

            self.cfg["profiles"][profile_name] = profile

            save(
                self.cfg
            )

            # ==================================================
            # ПРОВЕРКА
            # ==================================================

            check = load()

            saved_profile = check.get(
                "profiles",
                {}
            ).get(
                profile_name
            )

            if saved_profile != profile:

                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"❌ Не удалось сохранить профиль:\n\n"
                    f"{profile_name}"
                )

                return

            # ==================================================
            # УСПЕШНО
            # ==================================================

            QMessageBox.information(
                self,
                "Настройки",
                f"✅ Профиль «{profile_name}» сохранён"
            )

            self.accept()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Ошибка сохранения",
                f"❌ Не удалось сохранить настройки:\n\n{e}"
            )

            print(
                "ОШИБКА СОХРАНЕНИЯ:",
                repr(e)
            )