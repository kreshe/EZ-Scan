from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import pyperclip


class QueueWindow(QDialog):

    def __init__(self, buffer, parent=None):

        super().__init__(parent)

        self.buffer = buffer

        self.setWindowTitle(
            "📦 Очередь QR"
        )

        self.resize(
            450,
            500
        )


        self.search = QLineEdit()

        self.search.setPlaceholderText(
            "🔍 Поиск QR..."
        )


        self.count_label = QLabel()


        self.list = QListWidget()

        self.list.setSelectionMode(
            QListWidget.SingleSelection
        )


        self.list.itemDoubleClicked.connect(
            self.delete_item
        )


        self.list.setContextMenuPolicy(
            Qt.CustomContextMenu
        )

        self.list.customContextMenuRequested.connect(
            self.context_menu
        )


        layout = QVBoxLayout()

        layout.addWidget(
            self.search
        )

        layout.addWidget(
            self.count_label
        )

        layout.addWidget(
            self.list
        )


        self.setLayout(
            layout
        )


        self.search.textChanged.connect(
            self.update_list
        )


        self.timer = QTimer()

        self.timer.timeout.connect(
            self.update_list
        )

        self.timer.start(
            500
        )


        self.old_items = []


        self.update_list()



    def get_items(self):

        return self.buffer.all()



    def update_list(self):


        items = self.get_items()


        self.count_label.setText(
            f"Всего QR: {len(items)}"
        )


        text = self.search.text().upper()


        self.list.clear()



        for code in items:


            if text and text not in code.upper():

                continue



            item = QListWidgetItem(
                code
            )


            #
            # новые QR
            #

            if code not in self.old_items:

                font = item.font()

                font.setBold(
                    True
                )

                item.setFont(
                    font
                )


                item.setToolTip(
                    "Новый QR"
                )


            self.list.addItem(
                item
            )



        self.old_items = items



    def delete_item(self,item):

        code = item.text()


        self.buffer.remove_code(
            code
)


        self.update_list()



    def context_menu(self, pos):

        item = self.list.itemAt(pos)

        if not item:
            return


        code = item.text()


        menu = QMenu(self)


        copy_action = menu.addAction(
            "📋 Копировать"
        )


        delete_action = menu.addAction(
            "❌ Удалить"
        )


        clear_action = menu.addAction(
            "🗑 Очистить очередь"
        )


        action = menu.exec(
            self.list.mapToGlobal(pos)
        )


        if action == copy_action:

            pyperclip.copy(
                code
            )


        elif action == delete_action:

            self.buffer.remove_code(
                code
            )

            self.update_list()



        elif action == clear_action:

            self.buffer.clear()

            self.update_list()