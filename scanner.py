import os
import glob
import time
import grp
import subprocess
import shutil

from evdev import InputDevice, ecodes

from config import load, save


# ============================================================
# НАСТРОЙКИ
# ============================================================

RECONNECT_INTERVAL = 2.0


# ============================================================
# KEY MAP
# ============================================================

KEY_MAP = {

    "KEY_A": "A",
    "KEY_B": "B",
    "KEY_C": "C",
    "KEY_D": "D",
    "KEY_E": "E",
    "KEY_F": "F",
    "KEY_G": "G",
    "KEY_H": "H",
    "KEY_I": "I",
    "KEY_J": "J",
    "KEY_K": "K",
    "KEY_L": "L",
    "KEY_M": "M",
    "KEY_N": "N",
    "KEY_O": "O",
    "KEY_P": "P",
    "KEY_Q": "Q",
    "KEY_R": "R",
    "KEY_S": "S",
    "KEY_T": "T",
    "KEY_U": "U",
    "KEY_V": "V",
    "KEY_W": "W",
    "KEY_X": "X",
    "KEY_Y": "Y",
    "KEY_Z": "Z",

    "KEY_0": "0",
    "KEY_1": "1",
    "KEY_2": "2",
    "KEY_3": "3",
    "KEY_4": "4",
    "KEY_5": "5",
    "KEY_6": "6",
    "KEY_7": "7",
    "KEY_8": "8",
    "KEY_9": "9",

    "KEY_SPACE": " ",
    "KEY_MINUS": "-",
    "KEY_DOT": ".",
    "KEY_COMMA": ",",
    "KEY_SLASH": "/",
    "KEY_SEMICOLON": ";",
}


# ============================================================
# РАСКЛАДКА
# ============================================================

RU = """
йцукенгшщзхъ
фывапролджэ
ячсмитьбю
"""

EN = """
qwertyuiop[]
asdfghjkl;'
zxcvbnm,.
"""

RU_TO_EN = {}

for ru, en in zip(
    RU.replace("\n", ""),
    EN.replace("\n", "")
):

    RU_TO_EN[ru] = en
    RU_TO_EN[ru.upper()] = en.upper()


def fix_layout(text):

    result = []

    for char in text:

        result.append(
            RU_TO_EN.get(
                char,
                char
            )
        )

    return "".join(
        result
    )


def normalize(text):

    text = fix_layout(
        text
    )

    text = text.upper()

    text = " ".join(
        text.split()
    )

    return text


# ============================================================
# USER / PERMISSIONS
# ============================================================

def get_current_user():

    return os.environ.get(
        "USER",
        ""
    )


def user_in_input_group():

    try:

        group = grp.getgrnam(
            "input"
        )

        return group.gr_gid in os.getgroups()

    except Exception:

        return False


def check_scanner_access():

    device_path = find_scanner()

    if not device_path:

        return False

    try:

        device = InputDevice(
            device_path
        )

        device.close()

        return True

    except (
        PermissionError,
        OSError
    ):

        return False

    except Exception:

        return False


def add_user_to_input_group():

    user = get_current_user()

    if not user:

        return (
            False,
            "Не удалось определить пользователя."
        )

    if not shutil.which(
        "pkexec"
    ):

        return (
            False,
            "pkexec не найден."
        )

    try:

        result = subprocess.run(
            [
                "pkexec",
                "usermod",
                "-aG",
                "input",
                user
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:

            return (
                True,
                "Пользователь добавлен в группу input."
            )

        return (
            False,
            result.stderr.strip()
            or
            "Не удалось добавить пользователя "
            "в группу input."
        )

    except Exception as e:

        return (
            False,
            str(e)
        )


def setup_scanner_permissions():

    if user_in_input_group():

        if check_scanner_access():

            return (
                True,
                "✅ Доступ к сканеру уже настроен."
            )

        return (
            False,
            "⚠ Пользователь в группе input, "
            "но устройство недоступно."
        )

    return add_user_to_input_group()


# ============================================================
# СПИСОК УСТРОЙСТВ
# ============================================================

def find_scanners():

    return glob.glob(
        "/dev/input/by-id/usb-*-event-kbd"
    )


def get_scanner_devices():

    devices = []

    for path in find_scanners():

        try:

            device = InputDevice(
                path
            )

            info = {
                "path": path,
                "name": device.name,
                "vendor": getattr(
                    device.info,
                    "vendor",
                    0
                ),
                "product": getattr(
                    device.info,
                    "product",
                    0
                ),
                "accessible": True
            }

            device.close()

        except PermissionError:

            info = {
                "path": path,
                "name": "Нет доступа",
                "vendor": 0,
                "product": 0,
                "accessible": False
            }

        except Exception as e:

            info = {
                "path": path,
                "name": str(e),
                "vendor": 0,
                "product": 0,
                "accessible": False
            }

        devices.append(
            info
        )

    return devices


# ============================================================
# СОХРАНЁННЫЙ СКАНЕР
# ============================================================

def get_selected_scanner():

    cfg = load()

    return cfg.get(
        "scanner",
        {}
    ).get(
        "selected_device",
        ""
    )


def set_selected_scanner(
    device_path
):

    cfg = load()

    cfg.setdefault(
        "scanner",
        {}
    )

    cfg["scanner"][
        "selected_device"
    ] = device_path

    save(
        cfg
    )


# ============================================================
# ПОИСК АКТИВНОГО СКАНЕРА
# ============================================================

def find_scanner():

    selected = get_selected_scanner()

    # --------------------------------------------------------
    # Если пользователь выбрал конкретный сканер
    # --------------------------------------------------------

    if selected:

        if os.path.exists(
            selected
        ):

            return selected

        # ВАЖНО:
        # не выбираем случайную клавиатуру.
        # Ждём именно выбранное устройство.

        return None

    # --------------------------------------------------------
    # Старый режим — автоматический выбор
    # --------------------------------------------------------

    devices = find_scanners()

    if not devices:

        return None

    scanner_devices = [
        device
        for device in devices
        if "scanner" in device.lower()
    ]

    if scanner_devices:

        return scanner_devices[0]

    return devices[0]


# ============================================================
# ПРОВЕРКА СКАНЕРА
# ============================================================

def check_scanner():

    return (
        find_scanner()
        is not None
    )


# ============================================================
# ИНФОРМАЦИЯ
# ============================================================

def get_scanner_info():

    path = find_scanner()

    if not path:

        return None

    try:

        device = InputDevice(
            path
        )

        info = {
            "path": path,
            "name": device.name,
            "phys": getattr(
                device,
                "phys",
                ""
            ),
            "vendor": getattr(
                device.info,
                "vendor",
                0
            ),
            "product": getattr(
                device.info,
                "product",
                0
            )
        }

        device.close()

        return info

    except Exception:

        return None


# ============================================================
# ОТКРЫТЬ СКАНЕР
# ============================================================

def open_scanner():

    device_path = find_scanner()

    if not device_path:

        return None

    try:

        device = InputDevice(
            device_path
        )

        print()
        print(
            "🟢 Сканер найден:"
        )

        print(
            "Path:",
            device_path
        )

        print(
            "Device:",
            device.name
        )

        return device

    except PermissionError:

        print(
            "🔐 Нет доступа к сканеру."
        )

        return None

    except Exception as e:

        print(
            "⚠ Ошибка открытия сканера:",
            e
        )

        return None


# ============================================================
# ЧТЕНИЕ
# ============================================================

def read_scanner(
    callback,
    status_callback=None,
    reconnect_interval=RECONNECT_INTERVAL
):

    while True:

        device = None

        # ====================================================
        # ЖДЁМ СКАНЕР
        # ====================================================

        while device is None:

            device = open_scanner()

            if device is not None:

                if status_callback:

                    status_callback(
                        "connected"
                    )

                break

            if status_callback:

                status_callback(
                    "disconnected"
                )

            time.sleep(
                reconnect_interval
            )

        # ====================================================
        # ЧТЕНИЕ
        # ====================================================

        buffer = ""

        try:

            for event in device.read_loop():

                if event.type != ecodes.EV_KEY:

                    continue

                if event.value != 1:

                    continue

                try:

                    key = ecodes.KEY[
                        event.code
                    ]

                except Exception:

                    continue

                if key == "KEY_ENTER":

                    if buffer:

                        code = normalize(
                            buffer
                        )

                        print(
                            "SCAN:",
                            code
                        )

                        callback(
                            code
                        )

                        buffer = ""

                    continue

                if key in KEY_MAP:

                    buffer += KEY_MAP[
                        key
                    ]

                time.sleep(
                    0.001
                )

        except (
            OSError,
            IOError,
            EOFError
        ):

            print(
                "🔴 Сканер отключён."
            )

            if status_callback:

                status_callback(
                    "disconnected"
                )

        except Exception as e:

            print(
                "⚠ Ошибка сканера:",
                e
            )

            if status_callback:

                status_callback(
                    (
                        "error",
                        str(e)
                    )
                )

        finally:

            if device:

                try:

                    device.close()

                except Exception:

                    pass

        time.sleep(
            reconnect_interval
        )