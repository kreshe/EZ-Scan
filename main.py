import sys
import time
import json
import os
from profile_window import ProfileWindow
from dependency_installer import (
    check_dependencies,
    install_dependencies,
    print_dependencies
)
from welcome import WelcomeWindow

missing_python, missing_apt = check_dependencies()


if missing_python or missing_apt:

    print_dependencies(
        missing_python,
        missing_apt
    )


    answer = input(
        "\nУстановить отсутствующие зависимости? [Y/n]: "
    )


    if answer.lower() in ("", "y", "yes", "д", "да"):

        try:

            install_dependencies(
                missing_python,
                missing_apt
            )

            print()
            print("✅ Все зависимости установлены.")
            print("🔄 Перезапуск программы...")


            os.execv(
                sys.executable,
                [
                    sys.executable,
                    *sys.argv
                ]
            )


        except Exception as e:

            print()
            print("❌ Ошибка установки:")
            print(e)

            input(
                "\nНажмите Enter для выхода..."
            )

            sys.exit(1)


    else:

        print()
        print("❌ Без необходимых зависимостей программа не может запуститься.")

        input(
            "\nНажмите Enter для выхода..."
        )

        sys.exit(1)


from PySide6.QtWidgets import *
from PySide6.QtCore import *

from buffer import QRBuffer
from scanner import read_scanner
from sender import execute_batch
from trainer import Trainer
from PySide6.QtGui import QShortcut, QKeySequence
from version import VERSION
from config import load, save, set
from settings import Settings
from queue_window import QueueWindow
from status_widget import StatusWidget

def get_active_profile():

    cfg = load()

    profile_name = cfg.get(
        "active_profile",
        "По умолчанию"
    )

    profiles = cfg.setdefault(
        "profiles",
        {}
    )

    profile = profiles.setdefault(
        profile_name,
        {}
    )

    return profile

profile = get_active_profile()

cfg = load()


BUFFER_SIZE = profile["buffer_size"]
SEND_BATCH_SIZE = profile["batch_size"]
AUTO_SEND = profile["auto_send"]

buffer = QRBuffer(
    BUFFER_SIZE
)

buffer = QRBuffer(BUFFER_SIZE)


def reload_settings():

    global BUFFER_SIZE
    global SEND_BATCH_SIZE
    global AUTO_SEND
    global buffer

    profile = get_active_profile()

    BUFFER_SIZE = profile["buffer_size"]

    SEND_BATCH_SIZE = profile["batch_size"]

    AUTO_SEND = profile["auto_send"]

    buffer = QRBuffer(
        BUFFER_SIZE
    )


class ClickProgressBar(QProgressBar):

    clicked = Signal()


    def mousePressEvent(self, event):

        self.clicked.emit()

        super().mousePressEvent(event)

class ScannerThread(QThread):

    scanned = Signal(str)
    error = Signal(str)


    def run(self):

        try:

            read_scanner(
                self.new_code
            )

        except Exception as e:

            self.error.emit(
                str(e)
            )



    def new_code(self, code):

        if not code:
            return


        # защита от управляющих клавиш
        if len(code) < 3:
            return


        self.scanned.emit(code)





class SendThread(QThread):

    progress = Signal(int)
    finished = Signal()
    batch_info = Signal(int,int)
    stage = Signal(str)
    qr_started = Signal(str)
    qr_finished = Signal(str)
    error = Signal(str)

    def __init__(self):

        super().__init__()

        self.running = True



    def stop(self):

        self.running = False



    def run(self):

        while buffer.count() and self.running:


            codes = []


            for _ in range(
                min(
                    SEND_BATCH_SIZE,
                    buffer.count()
                )
            ):

                if not self.running:
                    break


                codes.append(
                    buffer.get()
                )



            if not codes:
                break

            self.batch_info.emit(
                1,
                len(codes)
            )


            self.stage.emit(
                "🔵 Отправка пачки"
            )


            for code in codes:

                self.qr_started.emit(
                    code
    )

            execute_batch(
                codes,
                self.progress,
                self
            )
            for code in codes:

                self.qr_finished.emit(
                    code
                )


            self.stage.emit(
                "✅ Пачка завершена"
            )
            
        self.finished.emit()
        
        print("ВСЕ QR:", len(codes))
        print(codes)



class Window(QWidget):


    def __init__(self):

        super().__init__()


        self.setWindowTitle(
            f"QR Buffer v{VERSION}"
        )

        self.sending = False
        
        self.resize(
            350,
            220
        )
        
        self.progress = ClickProgressBar()

        self.progress.clicked.connect(
            self.open_queue
        )
        self.progress.setMaximum(BUFFER_SIZE)
        
        self.progress.setFormat(
            f"{buffer.count()} / {BUFFER_SIZE}")

        self.progress.setTextVisible(
            True
        )
        
        self.setup_hotkeys()
        
        self.status = StatusWidget()
        self.status.set_auto(AUTO_SEND)
        cfg = load()

        self.status.set_profile(
            cfg.get(
                "active_profile",
                "По умолчанию"
            )
        )
        
        self.send=QPushButton(
            "▶ Отправить"
        )

        self.settings = QPushButton(
            "⚙ Настройки")
        
        self.auto=QPushButton(
            "⚡ Авто: ВКЛ"
        )

        self.profile = QPushButton(
        "👤 Профиль"
        )

        self.profile.clicked.connect(
            self.open_profile
        )

        self.auto.setCheckable(True)
        self.auto.setChecked(AUTO_SEND)
        if AUTO_SEND:

                self.auto.setText(
                    "⚡ Авто: ВКЛ"
                )

        else:

                self.auto.setText(
                    "⚡ Авто: ВЫКЛ"
                )
        
        
        self.stop=QPushButton(
            "⏹ Стоп"
        )

        self.clear=QPushButton(
            "🗑 Очистить"
        )
        # ==================================================
        # ФОКУС
        # ==================================================

        self.setFocusPolicy(
            Qt.StrongFocus
        )

        # Кнопки не должны получать фокус
        # от мыши или клавиатуры.
        for button in (
            self.send,
            self.stop,
            self.settings,
            self.auto,
            self.profile,
            self.clear
        ):

            button.setFocusPolicy(
                Qt.NoFocus
            )

        self.progress.setFocusPolicy(
            Qt.NoFocus
        )
        

        
        self.settings.clicked.connect(
            self.open_settings)
        
        self.send.clicked.connect(
            self.start_send
        )

        self.auto.clicked.connect(
            self.toggle_auto
        )
        
        self.stop.clicked.connect(
            self.stop_send
        )
        

        self.clear.clicked.connect(
            self.clear_buffer
        )



        layout=QVBoxLayout()


        layout.addWidget(
            self.progress
        )


        # ==========================================
        # ОТПРАВКА / СТОП
        # ==========================================

        send_stop = QHBoxLayout()

        send_stop.addWidget(
            self.send
        )

        send_stop.addWidget(
            self.stop
        )


        # ==========================================
        # НАСТРОЙКИ / ПРОФИЛЬ
        # ==========================================

        settings_profile = QHBoxLayout()

        settings_profile.addWidget(
            self.settings
        )

        settings_profile.addWidget(
            self.profile
        )


        # ==========================================
        # АВТО / ОЧИСТКА
        # ==========================================

        auto_clear = QHBoxLayout()

        auto_clear.addWidget(
            self.auto
        )

        auto_clear.addWidget(
            self.clear
        )


        layout = QVBoxLayout()

        layout.addWidget(
            self.progress
        )

        layout.addLayout(
            send_stop
        )

        layout.addLayout(
            settings_profile
        )

        layout.addLayout(
            auto_clear
        )

        layout.addWidget(
            self.status
        )


        self.setLayout(
            layout
        )

        #
        # Scanner
        #

        self.scanner=ScannerThread()


        self.scanner.scanned.connect(
            self.add_scan
        )


        self.scanner.error.connect(
            self.show_error
        )


        self.scanner.start()
        self.activateWindow()
        self.raise_()
        self.setFocus()

    def open_settings(self):

        dialog = Settings()

        if dialog.exec():

            reload_settings()

            self.setup_hotkeys()

            self.progress.setMaximum(
                BUFFER_SIZE
            )

            self.update_progress()

            self.auto.setChecked(
                AUTO_SEND
            )

            self.auto.setText(
                "⚡ Авто: ВКЛ"
                if AUTO_SEND
                else
                "⚡ Авто: ВЫКЛ"
            )
        
            self.status.setText(
                "✅ Настройки применены"
            )
            
    def open_queue(self):

        self.queue_window = QueueWindow(
            buffer,
            self
        )

        self.queue_window.show()
    
    def add_scan(self, code):


        self.setFocus()


        if buffer.add(code):


            self.update_progress()


            self.status.set_stage(
                f"📦 Буфер {buffer.count()} / {BUFFER_SIZE}"
            )


            #
            # Автоотправка
            #

            if (
                AUTO_SEND
                and buffer.count() >= SEND_BATCH_SIZE
                and not self.sending
            ):

                self.start_send()



        else:


            self.status.setText(
                "Дубликат или полный буфер"
            )


    def update_progress(self):

        self.progress.setValue(
            buffer.count()
        )

        self.progress.setFormat(
            f"{buffer.count()} / {BUFFER_SIZE}"
        )

    def open_profile(self):

        dialog = ProfileWindow(
            self
        )

        if dialog.exec():

            reload_settings()

            self.setup_hotkeys()

            self.progress.setMaximum(
                BUFFER_SIZE
            )

            self.update_progress()

            self.auto.setChecked(
                AUTO_SEND
            )

            self.auto.setText(
                "⚡ Авто: ВКЛ"
                if AUTO_SEND
                else
                "⚡ Авто: ВЫКЛ"
            )

            cfg = load()

            profile_name = cfg.get(
                "active_profile",
                "По умолчанию"
            )

            self.status.set_profile(
                profile_name
            )

            self.status.setText(
                "👤 Профиль применён"
            )
    def clear_buffer(self):

        buffer.clear()

        self.update_progress()

        self.status.set_stage(
            "🗑 Буфер очищен"
        )






    def start_send(self):


        if buffer.count()==0:

            return

        
        if self.sending:
            return


        self.sending = True
        
        self.send_thread=SendThread()

        self.send_thread.stage.connect(
            self.status.set_stage
        )


        self.send_thread.qr_started.connect(
            self.status.set_qr
        )


        self.send_thread.progress.connect(
            self.status.set_progress
        )


        self.send_thread.batch_info.connect(
            self.status.set_batch
        )

        self.send_thread.finished.connect(
            self.send_finished
        )


        self.send_thread.start()
        self.send.setEnabled(False)
        self.stop.setEnabled(True)


    def send_progress(self,value):

        self.status.setText(
            f"Отправлено {value}"
        )





    def send_finished(self):


        self.sending = False


        self.update_progress()


        self.stop.setEnabled(False)

        self.send.setEnabled(True)



        self.status.setText(
            f"Готово. Буфер: {buffer.count()} / {BUFFER_SIZE}"
        )



        #
        # если за время отправки накопилось ещё 12
        #

        if (
            AUTO_SEND
            and buffer.count() >= SEND_BATCH_SIZE
        ):

            self.start_send()

    def show_error(self,msg):

        self.status.setText(
            msg
        )


    def keyPressEvent(self, event):

            if event.key() in (
                Qt.Key_Return,
                Qt.Key_Enter
            ):
                return

            super().keyPressEvent(event)
        
    def stop_send(self):


            if hasattr(
                self,
                "send_thread"
            ):

                self.send_thread.stop()


                self.status.setText(
                    "Остановка..."
                )
    
    def setup_hotkeys(self):

        if hasattr(
            self,
            "shortcuts"
        ):

            for shortcut in self.shortcuts:

                shortcut.deleteLater()

        self.shortcuts = []

        cfg = load()

        hotkeys = cfg.get(
            "hotkeys",
            {}
        )

        actions = {

            "send": self.start_send,
            "stop": self.stop_send,
            "clear": self.clear_buffer,
            "auto": self.toggle_auto,
            "settings": self.open_settings,
            "profile": self.open_profile
        }

        for name, callback in actions.items():

            key = hotkeys.get(
                name
            )

            if not key:
                continue

            shortcut = QShortcut(
                QKeySequence(key),
                self
            )

            shortcut.setContext(
                Qt.ApplicationShortcut
            )

            shortcut.activated.connect(
                callback
            )

            self.shortcuts.append(
                shortcut
            )
        
    def toggle_auto(self):

        global AUTO_SEND


        AUTO_SEND = self.auto.isChecked()
        set(
            "auto_send",
            AUTO_SEND
        )
        self.status.set_auto(AUTO_SEND)

        if AUTO_SEND:

            self.auto.setText(
                "⚡ Авто: ВКЛ"
            )

            self.status.set_auto(
                True
            )

            self.status.set_stage(
                "Автоотправка включена"
            )

        else:

            self.auto.setText(
                "⚡ Авто: ВЫКЛ"
            )

            self.status.set_auto(
                False
            )

            self.status.set_stage(
                "Ручная отправка"
            )


app = QApplication(sys.argv)

window = Window()

window.show()

cfg = load()

if cfg.get(
    "show_welcome",
    True
):

    welcome = WelcomeWindow(
        window
    )

    result = welcome.exec()

    if not welcome.show_again.isChecked():

        cfg["show_welcome"] = False

        save(
            cfg
        )

sys.exit(
    app.exec()
)

