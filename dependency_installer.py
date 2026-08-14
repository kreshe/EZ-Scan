import importlib
import shutil
import subprocess
import sys


# ============================================================
# PYTHON MODULES
# ============================================================

PYTHON_MODULES = {

    "PySide6": "PySide6",
    "evdev": "evdev",
    "pyperclip": "pyperclip",

}


# ============================================================
# APT PACKAGES
# ============================================================

APT_PACKAGES = [

    "xdotool",
    "xclip",

    "libxcb-cursor0",
    "libxcb-xinerama0",
    "libxcb-icccm4",
    "libxcb-image0",
    "libxcb-keysyms1",
    "libxcb-randr0",
    "libxcb-render-util0",
    "libxcb-shape0",
    "libxcb-xfixes0",

]


# ============================================================
# CHECK PYTHON
# ============================================================

def check_python():

    missing = []

    for module, pip_name in PYTHON_MODULES.items():

        try:

            importlib.import_module(
                module
            )

        except ImportError:

            missing.append(
                pip_name
            )

    return missing


# ============================================================
# CHECK APT
# ============================================================

def check_apt():

    missing = []

    # Проверяем наличие dpkg

    if shutil.which("dpkg") is None:

        return APT_PACKAGES.copy()


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
# INSTALL PYTHON
# ============================================================

def install_python(packages):

    if not packages:

        return


    print()
    print("Установка Python-зависимостей...")
    print()


    command = [

        sys.executable,
        "-m",
        "pip",
        "install",

        *packages

    ]


    subprocess.check_call(
        command
    )


# ============================================================
# INSTALL APT
# ============================================================

def install_apt(packages):

    if not packages:

        return


    print()
    print("Установка системных зависимостей...")
    print()


    # Проверяем pkexec

    if shutil.which("pkexec") is None:

        raise RuntimeError(
            "Не найден pkexec. "
            "Установите policykit-1."
        )


    # Обновляем список пакетов

    subprocess.check_call(

        [
            "pkexec",
            "apt",
            "update"
        ]

    )


    # Устанавливаем ТОЛЬКО отсутствующие

    subprocess.check_call(

        [
            "pkexec",
            "apt",
            "install",
            "-y",

            *packages

        ]

    )


# ============================================================
# CHECK ALL
# ============================================================

def check_dependencies():

    missing_python = check_python()

    missing_apt = check_apt()

    return (
        missing_python,
        missing_apt
    )


# ============================================================
# INSTALL ALL
# ============================================================

def install_dependencies(
    missing_python,
    missing_apt
):

    if missing_apt:

        install_apt(
            missing_apt
        )


    if missing_python:

        install_python(
            missing_python
        )


# ============================================================
# PRINT RESULT
# ============================================================

def print_dependencies(
    missing_python,
    missing_apt
):

    print()
    print("=" * 50)
    print("ПРОВЕРКА ЗАВИСИМОСТЕЙ")
    print("=" * 50)


    if missing_python:

        print()
        print("❌ Python:")

        for package in missing_python:

            print(
                f"   - {package}"
            )

    else:

        print()
        print("✅ Python-зависимости установлены")


    if missing_apt:

        print()
        print("❌ Системные:")

        for package in missing_apt:

            print(
                f"   - {package}"
            )

    else:

        print()
        print("✅ Системные зависимости установлены")


    print()
    print("=" * 50)
