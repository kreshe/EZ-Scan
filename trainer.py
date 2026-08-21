import subprocess

from PySide6.QtWidgets import *
from PySide6.QtCore import Qt

from config import load


class Trainer(QWidget):

    def __init__(self, cfg=None):

        super().__init__()

        # ========================================================
        # CONFIG
        # ========================================================

        if cfg is None:
            self.cfg = load()
        else:
            self.cfg = cfg

        self.cfg.setdefault(
            "workflow",
            {}
        )

        self.cfg["workflow"].setdefault(
            "input_stage",
            []
        )

        self.cfg["workflow"].setdefault(
            "button_stage",
            []
        )

        self.cfg.setdefault(
            "positions",
            {}
        )

        # ========================================================
        # WINDOW
        # ========================================================

        self.setWindowTitle(
            "🎯 Обучение"
        )

        self.resize(
            450,
            500
        )

        # ========================================================
        # LISTS
        # ========================================================

        self.input_list = QTreeWidget()

        self.button_list = QTreeWidget()

        for tree in (
            self.input_list,
            self.button_list
        ):

            tree.setColumnCount(
                4
            )

            tree.setHeaderLabels(
                [
                    "Действие",
                    "X",
                    "Y",
                    "Статус"
                ]
            )

            tree.itemDoubleClicked.connect(
                self.train
            )

            tree.setContextMenuPolicy(
                Qt.CustomContextMenu
            )

            tree.customContextMenuRequested.connect(
                self.menu
            )

        # ========================================================
        # BUTTONS
        # ========================================================

        self.up = QPushButton(
            "⬆"
        )

        self.down = QPushButton(
            "⬇"
        )

        self.add_input = QPushButton(
            "➕ Поле"
        )

        self.add_button = QPushButton(
            "➕ Кнопка"
        )

        self.delete_button = QPushButton(
            "🗑 Удалить"
        )

        self.up.clicked.connect(
            lambda: self.move(-1)
        )

        self.down.clicked.connect(
            lambda: self.move(1)
        )

        self.add_input.clicked.connect(
            self.add_input_action
        )

        self.add_button.clicked.connect(
            self.add_button_action
        )

        self.delete_button.clicked.connect(
            self.delete_selected
        )

        # ========================================================
        # SCREEN INFO
        # ========================================================

        screen = self.get_screen_size()

        self.screen_info = QLabel(
            f"📐 Текущий экран: "
            f"{screen['width']} × {screen['height']}"
        )

        self.screen_info.setStyleSheet(
            """
            QLabel {
                padding: 4px;
                color: #666;
            }
            """
        )

        # ========================================================
        # LAYOUT
        # ========================================================

        layout = QVBoxLayout()

        layout.addWidget(
            QLabel(
                "Поля ввода"
            )
        )

        layout.addWidget(
            self.input_list
        )

        layout.addWidget(
            QLabel(
                "Кнопки"
            )
        )

        layout.addWidget(
            self.button_list
        )

        row = QHBoxLayout()

        row.addWidget(
            self.up
        )

        row.addWidget(
            self.down
        )

        row.addWidget(
            self.add_input
        )

        row.addWidget(
            self.add_button
        )

        row.addWidget(
            self.delete_button
        )

        layout.addLayout(
            row
        )

        layout.addWidget(
            self.screen_info
        )

        self.setLayout(
            layout
        )

        self.refresh()

    # ============================================================
    # SCREEN SIZE
    # ============================================================

    def get_screen_size(self):

        try:

            data = subprocess.check_output(
                [
                    "xdotool",
                    "getdisplaygeometry"
                ],
                text=True
            ).strip()

            width, height = map(
                int,
                data.split()
            )

            return {
                "width": width,
                "height": height
            }

        except Exception:

            # Резервное значение
            return {
                "width": 1920,
                "height": 1080
            }

    # ============================================================
    # SCALE POSITION
    # ============================================================

    def scale_position(
        self,
        position
    ):

        x = position.get(
            "x",
            0
        )

        y = position.get(
            "y",
            0
        )

        saved_width = position.get(
            "screen_width"
        )

        saved_height = position.get(
            "screen_height"
        )

        # Старый профиль без информации
        # о разрешении экрана
        if (
            not saved_width
            or
            not saved_height
        ):

            return x, y

        current = self.get_screen_size()

        current_width = current["width"]
        current_height = current["height"]

        # Разрешение не изменилось
        if (
            current_width == saved_width
            and
            current_height == saved_height
        ):

            return x, y

        scaled_x = round(
            x
            * current_width
            / saved_width
        )

        scaled_y = round(
            y
            * current_height
            / saved_height
        )

        print(
            f"📐 Масштабирование: "
            f"({x}, {y}) "
            f"{saved_width}x{saved_height}"
            f" → "
            f"({scaled_x}, {scaled_y}) "
            f"{current_width}x{current_height}"
        )

        return (
            scaled_x,
            scaled_y
        )

    # ============================================================
    # ADD INPUT
    # ============================================================

    def add_input_action(self):

        arr = self.cfg[
            "workflow"
        ][
            "input_stage"
        ]

        name = self.next_name(
            "input_",
            arr
        )

        arr.append(
            name
        )

        # Новое действие пока не обучено
        self.cfg[
            "positions"
        ][name] = {
            "x": 0,
            "y": 0,
            "screen_width": 0,
            "screen_height": 0
        }

        self.refresh()

    # ============================================================
    # ADD BUTTON
    # ============================================================

    def add_button_action(self):

        arr = self.cfg[
            "workflow"
        ][
            "button_stage"
        ]

        name = self.next_name(
            "button",
            arr
        )

        arr.append(
            name
        )

        self.cfg[
            "positions"
        ][name] = {
            "x": 0,
            "y": 0,
            "screen_width": 0,
            "screen_height": 0
        }

        self.refresh()

    # ============================================================
    # DELETE SELECTED
    # ============================================================

    def delete_selected(self):

        tree = self.current()

        if not tree:
            return

        item = tree.currentItem()

        if not item:
            return

        name = item.text(
            0
        )

        result = QMessageBox.question(
            self,
            "Удаление",
            f"Удалить {name}?"
        )

        if result != QMessageBox.Yes:
            return

        self.delete_item(
            name
        )

    # ============================================================
    # REFRESH
    # ============================================================

    def refresh(self):

        self.input_list.clear()

        self.button_list.clear()

        for name in self.cfg[
            "workflow"
        ][
            "input_stage"
        ]:

            self.add_row(
                self.input_list,
                name
            )

        for name in self.cfg[
            "workflow"
        ][
            "button_stage"
        ]:

            self.add_row(
                self.button_list,
                name
            )

        # Обновляем информацию об экране
        screen = self.get_screen_size()

        self.screen_info.setText(
            f"📐 Текущий экран: "
            f"{screen['width']} × {screen['height']}"
        )

    # ============================================================
    # ADD ROW
    # ============================================================

    def add_row(
        self,
        tree,
        name
    ):

        pos = self.cfg[
            "positions"
        ].get(
            name,
            {
                "x": 0,
                "y": 0
            }
        )

        ok = (
            pos.get("x", 0) != 0
            or
            pos.get("y", 0) != 0
        )

        tree.addTopLevelItem(
            QTreeWidgetItem(
                [
                    name,
                    str(
                        pos.get(
                            "x",
                            0
                        )
                    ),
                    str(
                        pos.get(
                            "y",
                            0
                        )
                    ),
                    "✔" if ok else "❌"
                ]
            )
        )

    # ============================================================
    # CURRENT LIST
    # ============================================================

    def current(self):

        for tree in (
            self.input_list,
            self.button_list
        ):

            if tree.currentItem():

                return tree

        return None

    # ============================================================
    # TRAIN
    # ============================================================

    def train(
        self,
        item
    ):

        name = item.text(
            0
        )

        QMessageBox.information(
            self,
            "Обучение",
            f"Действие:\n\n"
            f"{name}\n\n"
            f"Наведите мышь на нужный элемент "
            f"и нажмите OK."
        )

        try:

            data = subprocess.check_output(
                [
                    "xdotool",
                    "getmouselocation"
                ],
                text=True
            )

            x = int(
                data.split(
                    "x:"
                )[1].split()[0]
            )

            y = int(
                data.split(
                    "y:"
                )[1].split()[0]
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось получить координаты:\n\n{e}"
            )

            return

        screen = self.get_screen_size()

        self.cfg[
            "positions"
        ][name] = {

            "x": x,
            "y": y,

            "screen_width":
                screen["width"],

            "screen_height":
                screen["height"]
        }

        print(
            f"🎯 Обучено: {name}"
        )

        print(
            f"   Координаты: {x}, {y}"
        )

        print(
            f"   Экран: "
            f"{screen['width']}x"
            f"{screen['height']}"
        )

        self.refresh()

    # ============================================================
    # MOVE
    # ============================================================

    def move(
        self,
        step
    ):

        tree = self.current()

        if not tree:
            return

        item = tree.currentItem()

        if not item:
            return

        row = tree.indexOfTopLevelItem(
            item
        )

        if row < 0:
            return

        if tree == self.input_list:

            arr = self.cfg[
                "workflow"
            ][
                "input_stage"
            ]

        else:

            arr = self.cfg[
                "workflow"
            ][
                "button_stage"
            ]

        new = row + step

        if 0 <= new < len(arr):

            arr[row], arr[new] = (
                arr[new],
                arr[row]
            )

            self.refresh()

    # ============================================================
    # CONTEXT MENU
    # ============================================================

    def menu(
        self,
        pos
    ):

        tree = self.sender()

        item = tree.itemAt(
            pos
        )

        if not item:
            return

        tree.setCurrentItem(
            item
        )

        menu = QMenu()

        train = menu.addAction(
            "🎯 Обучить"
        )

        test = menu.addAction(
            "🖱 Проверить"
        )

        delete = menu.addAction(
            "🗑 Удалить"
        )

        action = menu.exec(
            tree.viewport().mapToGlobal(
                pos
            )
        )

        if action == train:

            self.train(
                item
            )

        elif action == delete:

            self.delete_item(
                item.text(
                    0
                )
            )

        elif action == test:

            self.test_click(
                item
            )

    # ============================================================
    # DELETE
    # ============================================================

    def delete_item(
        self,
        name
    ):

        for arr in (
            self.cfg[
                "workflow"
            ][
                "input_stage"
            ],

            self.cfg[
                "workflow"
            ][
                "button_stage"
            ]
        ):

            if name in arr:

                arr.remove(
                    name
                )

        self.cfg[
            "positions"
        ].pop(
            name,
            None
        )

        self.refresh()

    # ============================================================
    # NEXT NAME
    # ============================================================

    def next_name(
        self,
        prefix,
        arr
    ):

        number = 1

        while (
            f"{prefix}{number}"
            in arr
        ):

            number += 1

        return (
            f"{prefix}{number}"
        )

    # ============================================================
    # TEST CLICK
    # ============================================================

    def test_click(
        self,
        item
    ):

        name = item.text(
            0
        )

        pos = self.cfg[
            "positions"
        ].get(
            name
        )

        if not pos:

            QMessageBox.warning(
                self,
                "Ошибка",
                "Координаты не обучены."
            )

            return

        raw_x = pos.get(
            "x",
            0
        )

        raw_y = pos.get(
            "y",
            0
        )

        if (
            raw_x == 0
            and
            raw_y == 0
        ):

            QMessageBox.warning(
                self,
                "Ошибка",
                "Координаты не обучены."
            )

            return

        x, y = self.scale_position(
            pos
        )

        print(
            f"🖱 Тестовый клик: "
            f"{name} → ({x}, {y})"
        )

        try:

            subprocess.call(
                [
                    "xdotool",
                    "mousemove",
                    str(x),
                    str(y)
                ]
            )

            subprocess.call(
                [
                    "xdotool",
                    "click",
                    "1"
                ]
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось выполнить клик:\n\n{e}"
            )