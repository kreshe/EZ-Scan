from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QFrame
)

from PySide6.QtCore import Qt
from version import VERSION

class WelcomeWindow(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle(
            f"🚀 Добро пожаловать в EZ SCAN {VERSION} "
        )

        self.setFixedSize(
            520,
            560
        )

        self.setModal(True)

        # ==================================================
        # ЗАГОЛОВОК
        # ==================================================

        title = QLabel(
            "🚀 EZ SCAN"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 28px;
                font-weight: bold;
                padding: 10px;
            }
            """
        )

        subtitle = QLabel(
            "Сканируй → буферизуй → отправляй"
        )

        subtitle.setAlignment(
            Qt.AlignCenter
        )

        subtitle.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                color: #aaaaaa;
                padding-bottom: 10px;
            }
            """
        )

        # ==================================================
        # ОСНОВНАЯ ИНСТРУКЦИЯ
        # ==================================================

        info = QLabel(
            """
            <h3>📦 Как это работает</h3>

            <b>1. Сканируй QR-коды</b><br>
            QR автоматически попадает в буфер.

            <br><br>

            <b>2. Набери нужное количество</b><br>
            Программа показывает количество:
            <b>18 / 24</b>.

            <br><br>

            <b>3. Отправка</b><br>
            Нажми <b>▶ Отправить</b> или включи
            автоматическую отправку.

            <br><br>

            <h3>🎯 Обучение</h3>

            В настройках можно указать координаты
            полей и кнопок мыши.

            <br><br>

            <h3>👤 Профили</h3>

            Сохраняй разные наборы координат,
            таймингов и настроек для разных рабочих мест.

            <br><br>

            <h3>⚡ Полезные возможности</h3>

            • автоматическая отправка пачками<br>
            • защита от дубликатов<br>
            • настраиваемые задержки<br>
            • несколько полей ввода<br>
            • несколько кнопок в workflow<br>
            • остановка отправки<br>
            • очередь QR-кодов<br>
            • горячие клавиши
            """
        )

        info.setWordWrap(
            True
        )

        info.setTextFormat(
            Qt.RichText
        )

        info.setStyleSheet(
            """
            QLabel {
                font-size: 13px;
                padding: 10px;
            }
            """
        )

        # ==================================================
        # ГОРЯЧИЕ КЛАВИШИ
        # ==================================================

        shortcuts = QLabel(
            """
            <h3>⌨ Горячие клавиши</h3>

            <table>
            <tr>
                <td><b>F1</b></td>
                <td>▶ Отправить</td>
            </tr>
            <tr>
                <td><b>F2</b></td>
                <td>⏹ Стоп</td>
            </tr>
            <tr>
                <td><b>F3</b></td>
                <td>🗑 Очистить</td>
            </tr>
            <tr>
                <td><b>F4</b></td>
                <td>⚡ Автоотправка</td>
            </tr>
            <tr>
                <td><b>F5</b></td>
                <td>⚙ Настройки</td>
            </tr>
            <tr>
                <td><b>F6</b></td>
                <td>👤 Профили</td>
            </tr>
            </table>
            """
        )

        shortcuts.setTextFormat(
            Qt.RichText
        )

        shortcuts.setStyleSheet(
            """
            QLabel {
                padding: 5px 10px;
                font-size: 12px;
            }
            """
        )

        # ==================================================
        # НЕ ПОКАЗЫВАТЬ
        # ==================================================

        self.show_again = QCheckBox(
            "Показывать эту инструкцию при запуске"
        )

        self.show_again.setChecked(
            True
        )

        # ==================================================
        # КНОПКА
        # ==================================================

        start_btn = QPushButton(
            "🚀 Начать работу"
        )

        start_btn.setMinimumHeight(
            40
        )

        start_btn.clicked.connect(
            self.accept
        )

        # ==================================================
        # LAYOUT
        # ==================================================

        layout = QVBoxLayout()

        layout.setContentsMargins(
            20,
            15,
            20,
            15
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            subtitle
        )

        layout.addWidget(
            info
        )

        layout.addWidget(
            shortcuts
        )

        layout.addStretch()

        layout.addWidget(
            self.show_again
        )

        layout.addWidget(
            start_btn
        )

        self.setLayout(
            layout
        )