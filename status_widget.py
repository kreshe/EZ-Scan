from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
    QHBoxLayout
)

from PySide6.QtCore import Qt


class StatusWidget(QFrame):

    def __init__(self):

        super().__init__()

        self.setObjectName(
            "StatusWidget"
        )

        self.setFrameShape(
            QFrame.StyledPanel
        )

        self.setMinimumHeight(
            105
        )

        self.setMaximumHeight(
            125
        )

        # ====================================================
        # ОСНОВНОЙ СТАТУС
        # ====================================================

        self.state = QLabel(
            "⚪ Ожидание QR..."
        )

        self.state.setAlignment(
            Qt.AlignCenter
        )

        self.state.setStyleSheet(
            """
            QLabel {
                font-size: 15px;
                font-weight: bold;
            }
            """
        )

        # ====================================================
        # ИНФОРМАЦИЯ
        # ====================================================

        self.batch = QLabel(
            "📦 Пачка: —"
        )

        self.qr = QLabel(
            "🔹 QR: —"
        )

        self.progress = QLabel(
            "📤 Отправлено: 0"
        )

        self.profile = QLabel(
            "👤 Профиль: По умолчанию"
        )

        self.mode = QLabel(
            "⚡ Авто: ВКЛ"
        )

        # ====================================================
        # СТИЛЬ ИНФОРМАЦИИ
        # ====================================================

        info_style = """
            QLabel {
                font-size: 12px;
            }
        """

        for label in (
            self.batch,
            self.qr,
            self.progress,
            self.profile,
            self.mode
        ):

            label.setStyleSheet(
                info_style
            )

        # ====================================================
        # ВЕРХНЯЯ СТРОКА
        # ====================================================

        top = QHBoxLayout()

        top.setContentsMargins(
            0,
            0,
            0,
            0
        )

        top.setSpacing(
            6
        )

        top.addWidget(
            self.batch
        )

        top.addStretch()

        top.addWidget(
            self.mode
        )

        # ====================================================
        # QR
        # ====================================================

        self.qr.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )

        self.qr.setToolTip(
            "Последний обработанный QR"
        )

        # ====================================================
        # НИЖНЯЯ СТРОКА
        # ====================================================

        bottom = QHBoxLayout()

        bottom.setContentsMargins(
            0,
            0,
            0,
            0
        )

        bottom.setSpacing(
            6
        )

        bottom.addWidget(
            self.progress
        )

        bottom.addStretch()

        bottom.addWidget(
            self.profile
        )

        # ====================================================
        # ОСНОВНОЙ LAYOUT
        # ====================================================

        layout = QVBoxLayout()

        layout.setContentsMargins(
            8,
            6,
            8,
            6
        )

        layout.setSpacing(
            3
        )

        layout.addWidget(
            self.state
        )

        layout.addLayout(
            top
        )

        layout.addWidget(
            self.qr
        )

        layout.addLayout(
            bottom
        )

        self.setLayout(
            layout
        )

    # ========================================================
    # ОСНОВНОЙ СТАТУС
    # ========================================================

    def set_stage(self, text):

        if not text:

            text = "⚪ Ожидание QR..."

        self.state.setText(
            str(text)
        )

    # --------------------------------------------------------
    # Совместимость с main.py
    # --------------------------------------------------------

    def setText(self, text):

        self.set_stage(
            text
        )

    # ========================================================
    # ПАЧКА
    # ========================================================

    def set_batch(
        self,
        current,
        total
    ):

        self.batch.setText(
            f"📦 Пачка: {current}/{total}"
        )

    # ========================================================
    # QR
    # ========================================================

    def set_qr(self, code):

        if code is None:

            code = ""

        code = str(code)

        # Полный QR сохраняем в tooltip

        self.qr.setToolTip(
            code
        )

        # Чтобы длинный код не ломал интерфейс

        max_length = 42

        if len(code) > max_length:

            display_code = (
                code[:max_length]
                + "…"
            )

        else:

            display_code = code

        self.qr.setText(
            f"🔹 QR: {display_code}"
        )

    # ========================================================
    # ПРОГРЕСС
    # ========================================================

    def set_progress(self, value):

        try:

            value = int(value)

        except Exception:

            value = 0

        self.progress.setText(
            f"📤 Отправлено: {value}"
        )

    # ========================================================
    # ПРОФИЛЬ
    # ========================================================

    def set_profile(self, name):

        if not name:

            name = "По умолчанию"

        self.profile.setText(
            f"👤 Профиль: {name}"
        )

    # ========================================================
    # АВТОРЕЖИМ
    # ========================================================

    def set_auto(self, enabled):

        if enabled:

            self.mode.setText(
                "⚡ Авто: ВКЛ"
            )

        else:

            self.mode.setText(
                "⚡ Авто: ВЫКЛ"
            )

    # ========================================================
    # ОЖИДАНИЕ
    # ========================================================

    def waiting(self):

        self.state.setText(
            "⚪ Ожидание QR..."
        )

        self.qr.setText(
            "🔹 QR: —"
        )

        self.qr.setToolTip(
            ""
        )

    # ========================================================
    # ОТПРАВКА
    # ========================================================

    def sending(self):

        self.state.setText(
            "🔵 Отправка..."
        )

    # ========================================================
    # ЗАВЕРШЕНИЕ
    # ========================================================

    def finished(self):

        self.state.setText(
            "🟢 Отправка завершена"
        )

    # ========================================================
    # ОСТАНОВКА
    # ========================================================

    def stopped(self):

        self.state.setText(
            "🟠 Отправка остановлена"
        )

    # ========================================================
    # ОШИБКА
    # ========================================================

    def error(self, text):

        if not text:

            text = "Неизвестная ошибка"

        self.state.setText(
            f"🔴 {text}"
        )