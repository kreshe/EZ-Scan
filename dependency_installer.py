import importlib
import shutil
import subprocess
import os


PYTHON_MODULES = {
    "PySide6": "PySide6",
    "evdev": "evdev",
    "pyperclip": "pyperclip",
}


APT_PACKAGES = [
    "xdotool",
    "xclip",
    "policykit-1",
]


# ============================================================
# PYTHON
# ============================================================

def check_python():

    missing = []

    for module, package in PYTHON_MODULES.items():

        try:

            importlib.import_module(
                module
            )

        except ImportError:

            missing.append(
                package
            )

    return missing


# ============================================================
# APT
# ============================================================

def check_apt():

    missing = []

    for package in APT_PACKAGES:

        result = subprocess.run(
            [
                "dpkg",
                "-s",
                package
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if result.returncode != 0:

            missing.append(
                package
            )

    return missing


# ============================================================
# PKEXEC
# ============================================================

def has_pkexec():

    return shutil.which(
        "pkexec"
    ) is not None


# ============================================================
# INSTALL SYSTEM
# ============================================================

def install_apt(packages):

    if not packages:

        return True

    if not has_pkexec():

        raise RuntimeError(
            "Не найден pkexec."
        )

    result = subprocess.run(
        [
            "pkexec",
            "apt-get",
            "update"
        ]
    )

    if result.returncode != 0:

        raise RuntimeError(
            "Не удалось выполнить apt-get update."
        )

    result = subprocess.run(
        [
            "pkexec",
            "apt-get",
            "install",
            "-y",
            *packages
        ]
    )

    if result.returncode != 0:

        raise RuntimeError(
            "Не удалось установить системные зависимости."
        )

    return True


# ============================================================
# CHECK ALL
# ============================================================

def check_dependencies():

    return (
        check_python(),
        check_apt()
    )


# ============================================================
# INSTALL ALL SYSTEM
# ============================================================

def install_dependencies(
    missing_python,
    missing_apt
):

    if missing_apt:

        install_apt(
            missing_apt
        )


# ============================================================
# INPUT GROUP
# ============================================================

def in_input_group():

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
            in result.stdout.split()
        )

    except Exception:

        return False


# ============================================================
# ADD USER TO INPUT
# ============================================================

def add_to_input_group():

    if in_input_group():

        return {
            "success": True,
            "restart_required": False,
            "message": (
                "Пользователь уже состоит "
                "в группе input."
            )
        }

    username = (
        os.environ.get("USER")
        or
        os.environ.get("USERNAME")
    )

    if not username:

        return {
            "success": False,
            "restart_required": False,
            "message": (
                "Не удалось определить пользователя."
            )
        }

    if not has_pkexec():

        return {
            "success": False,
            "restart_required": False,
            "message": (
                "Не найден pkexec."
            )
        }

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
            "message": (
                "Не удалось добавить пользователя "
                "в группу input."
            )
        }

    return {
        "success": True,
        "restart_required": True,
        "message": (
            "Пользователь добавлен "
            "в группу input."
        )
    }