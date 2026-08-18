import glob
import os
import subprocess
import time

from evdev import InputDevice, ecodes


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
    "KEY_SEMICOLON": ";"
}


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

for r, e in zip(
    RU.replace("\n", ""),
    EN.replace("\n", "")
):

    RU_TO_EN[r] = e
    RU_TO_EN[r.upper()] = e.upper()


def fix_layout(text):

    result = ""

    for char in text:

        result += RU_TO_EN.get(
            char,
            char
        )

    return result


def normalize(text):

    text = fix_layout(text)

    text = text.upper()

    text = " ".join(
        text.split()
    )

    return text


# ============================================================
# УСТРОЙСТВА
# ============================================================

def get_input_devices():

    devices = []

    for path in glob.glob(
        "/dev/input/event*"
    ):

        try:

            device = InputDevice(
                path
            )

            devices.append(
                {
                    "path": path,
                    "name": device.name or "",
                    "phys": device.phys or "",
                    "uniq": device.uniq or ""
                }
            )

            device.close()

        except PermissionError:

            devices.append(
                {
                    "path": path,
                    "name": "Нет доступа",
                    "phys": "",
                    "uniq": ""
                }
            )

        except Exception:

            continue

    return devices


def get_by_id_devices():

    result = []

    for path in glob.glob(
        "/dev/input/by-id/*"
    ):

        if not os.path.islink(
            path
        ):

            continue

        try:

            real_path = os.path.realpath(
                path
            )

            if real_path.startswith(
                "/dev/input/event"
            ):

                result.append(
                    {
                        "link": path,
                        "path": real_path
                    }
                )

        except Exception:

            continue

    return result


# ============================================================
# ПОИСК СКАНЕРОВ
# ============================================================

def find_scanners():

    devices = get_input_devices()

    by_id = get_by_id_devices()

    by_id_map = {}

    for item in by_id:

        by_id_map[
            item["path"]
        ] = item["link"]

    keywords = (
        "scanner",
        "barcode",
        "qr",
        "honeywell",
        "zebra",
        "symbol",
        "datalogic"
    )

    result = []

    for device in devices:

        name = (
            device["name"]
            or ""
        ).lower()

        link = by_id_map.get(
            device["path"]
        )

        link_name = (
            os.path.basename(link).lower()
            if link
            else ""
        )

        score = 0

        for word in keywords:

            if word in name:

                score += 10

            if word in link_name:

                score += 10

        if "event-kbd" in link_name:

            score += 3

        if score > 0:

            result.append(
                {
                    **device,
                    "link": link,
                    "score": score
                }
            )

    result.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return result


# ============================================================
# ЛУЧШИЙ СКАНЕР
# ============================================================

def find_scanner():

    scanners = find_scanners()

    if not scanners:

        return None

    return (
        scanners[0].get("link")
        or
        scanners[0]["path"]
    )


# ============================================================
# ДОСТУП
# ============================================================

def check_scanner_access():

    device_path = find_scanner()

    if not device_path:

        return {
            "found": False,
            "access": False,
            "device": None,
            "message": "Сканер не найден"
        }

    try:

        device = InputDevice(
            device_path
        )

        device.close()

        return {
            "found": True,
            "access": True,
            "device": device_path,
            "message": "Доступ разрешён"
        }

    except PermissionError:

        return {
            "found": True,
            "access": False,
            "device": device_path,
            "message": "Нет доступа"
        }

    except Exception as e:

        return {
            "found": True,
            "access": False,
            "device": device_path,
            "message": str(e)
        }


# ============================================================
# INPUT GROUP
# ============================================================

def user_in_input_group():

    try:

        result = subprocess.run(
            [
                "id",
                "-nG"
            ],
            capture_output=True,
            text=True
        )

        return (
            "input"
            in
            result.stdout.split()
        )

    except Exception:

        return False


# ============================================================
# ПРАВА
# ============================================================

def setup_scanner_permissions():

    username = os.environ.get(
        "USER"
    )

    if not username:

        return {
            "success": False,
            "restart_required": False,
            "message": "Не удалось определить пользователя."
        }

    if user_in_input_group():

        return {
            "success": True,
            "restart_required": False,
            "message": "Доступ к input уже настроен."
        }

    try:

        result = subprocess.run(
            [
                "pkexec",
                "usermod",
                "-aG",
                "input",
                username
            ]
        )

        if result.returncode != 0:

            return {
                "success": False,
                "restart_required": False,
                "message": "Не удалось добавить пользователя в input."
            }

        return {
            "success": True,
            "restart_required": True,
            "message": (
                "Пользователь добавлен в группу input."
            )
        }

    except FileNotFoundError:

        return {
            "success": False,
            "restart_required": False,
            "message": "pkexec не найден."
        }

    except Exception as e:

        return {
            "success": False,
            "restart_required": False,
            "message": str(e)
        }


# ============================================================
# ЧТЕНИЕ
# ============================================================

def read_scanner(callback):

    device_path = find_scanner()

    if not device_path:

        raise RuntimeError(
            "QR-сканер не найден."
        )

    try:

        dev = InputDevice(
            device_path
        )

    except PermissionError:

        raise PermissionError(
            "Нет доступа к QR-сканеру."
        )

    print(
        "Scanner:",
        dev.name
    )

    print(
        "Device:",
        device_path
    )

    print(
        "Ожидание QR..."
    )

    buffer = ""

    try:

        for event in dev.read_loop():

            if event.type != ecodes.EV_KEY:
                continue

            if event.value != 1:
                continue

            key = ecodes.KEY.get(
                event.code
            )

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

            elif key in KEY_MAP:

                buffer += KEY_MAP[key]

            time.sleep(
                0.001
            )

    finally:

        dev.close()