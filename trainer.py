import subprocess

from PySide6.QtWidgets import *
from PySide6.QtCore import Qt

from config import load, save


class Trainer(QWidget):


    def __init__(self, cfg=None):

        super().__init__()

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
        self.setWindowTitle(
            "🎯 Обучение"
        )

        self.resize(
            450,
            500
        )


        self.input_list = QTreeWidget()

        self.button_list = QTreeWidget()
        

        for tree in (
            self.input_list,
            self.button_list
        ):

            tree.setColumnCount(4)

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



        self.up=QPushButton("⬆")

        self.down=QPushButton("⬇")

        self.add_input = QPushButton(
            "➕ Поле"
        )

        self.add_button = QPushButton(
            "➕ Кнопка"
        )

        self.delete_button = QPushButton(
            "🗑 Удалить"
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

        self.up.clicked.connect(
            lambda:self.move(-1)
        )

        self.down.clicked.connect(
            lambda:self.move(1)
        )


        layout=QVBoxLayout()


        layout.addWidget(
            QLabel("Поля ввода")
        )

        layout.addWidget(
            self.input_list
        )


        layout.addWidget(
            QLabel("Кнопки")
        )

        layout.addWidget(
            self.button_list
        )


        row=QHBoxLayout()

        row.addWidget(self.up)
        row.addWidget(self.down)

        row.addWidget(
            self.add_input
        )

        row.addWidget(
            self.add_button
        )

        row.addWidget(
            self.delete_button
        )


        layout.addLayout(row)


        self.setLayout(layout)


        self.refresh()

    def add_input_action(self):

        arr = self.cfg["workflow"]["input_stage"]

        name = self.next_name(
            "input_",
            arr
        )

        arr.append(name)

        self.cfg["positions"][name] = {
            "x": 0,
            "y": 0
        }
        
        self.refresh()
        
    def add_button_action(self):

        arr = self.cfg["workflow"]["button_stage"]

        name = self.next_name(
            "button",
            arr
        )

        arr.append(name)

        self.cfg["positions"][name] = {
            "x": 0,
            "y": 0
        }

        self.refresh()
    
    def delete_selected(self):

        tree = self.current()

        if not tree:
            return

        item = tree.currentItem()

        if not item:
            return

        name = item.text(0)

        result = QMessageBox.question(
            self,
            "Удаление",
            f"Удалить {name}?"
        )

        if result != QMessageBox.Yes:
            return

        self.delete_item(name)
        
    def refresh(self):

        self.input_list.clear()
        self.button_list.clear()


        for name in self.cfg["workflow"]["input_stage"]:

            self.add_row(
                self.input_list,
                name
            )


        for name in self.cfg["workflow"]["button_stage"]:

            self.add_row(
                self.button_list,
                name
            )



    def add_row(self,tree,name):

        pos=self.cfg["positions"].get(
            name,
            {
                "x":0,
                "y":0
            }
        )


        ok = (
            pos["x"] !=0
            or
            pos["y"] !=0
        )


        tree.addTopLevelItem(
            QTreeWidgetItem(
                [
                    name,
                    str(pos["x"]),
                    str(pos["y"]),
                    "✔" if ok else "❌"
                ]
            )
        )



    def current(self):

        for tree in (
            self.input_list,
            self.button_list
        ):

            if tree.currentItem():

                return tree


        return None



    def train(self,item):

        name=item.text(0)


        QMessageBox.information(
            self,
            "Обучение",
            "Наведите мышь и нажмите OK"
        )


        data=subprocess.check_output(
            [
                "xdotool",
                "getmouselocation"
            ]
        ).decode()


        x=int(
            data.split("x:")[1].split()[0]
        )

        y=int(
            data.split("y:")[1].split()[0]
        )


        self.cfg["positions"][name]={
            "x":x,
            "y":y
        }


        self.refresh()



    def move(self,step):

        tree=self.current()

        if not tree:
            return


        item=tree.currentItem()

        row=tree.indexOfTopLevelItem(item)


        if tree==self.input_list:

            arr=self.cfg["workflow"]["input_stage"]

        else:

            arr=self.cfg["workflow"]["button_stage"]



        new=row+step


        if 0 <= new < len(arr):

            arr[row],arr[new]=arr[new],arr[row]

            self.refresh()



    def menu(self,pos):

        tree=self.sender()

        item=tree.itemAt(pos)

        if not item:
            return


        tree.setCurrentItem(item)


        menu=QMenu()


        train=menu.addAction(
            "🎯 Обучить"
        )

        test=menu.addAction(
            "🖱 Проверить"
        )

        delete=menu.addAction(
            "🗑 Удалить"
        )


        action=menu.exec(
            tree.viewport().mapToGlobal(pos)
        )


        if action==train:

            self.train(item)


        elif action == delete:

            self.delete_item(
                item.text(0)
            )
            
        elif action == test:
            self.test_click(item)
            
    def delete_item(self, name):

        for arr in (
            self.cfg["workflow"]["input_stage"],
            self.cfg["workflow"]["button_stage"]
        ):

            if name in arr:
                arr.remove(name)

        self.cfg["positions"].pop(
            name,
            None
        )

        self.refresh()
    
    def next_name(self, prefix, arr):

        number = 1

        while f"{prefix}{number}" in arr:
            number += 1

        return f"{prefix}{number}"
    
    def test_click(self, item):

        name = item.text(0)

        pos = self.cfg["positions"].get(name)

        if not pos:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Координаты не обучены"
            )
            return

        subprocess.call([
            "xdotool",
            "mousemove",
            str(pos["x"]),
            str(pos["y"])
        ])

        subprocess.call([
            "xdotool",
            "click",
            "1"
        ])