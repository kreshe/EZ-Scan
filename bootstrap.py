import os
import sys

from dependency_installer import (
    check_python,
    check_apt,
    install_python,
)

# Проверяем зависимости
missing_python = check_python()
missing_apt = check_apt()

# Если отсутствует PySide6, сначала ставим его
if "PySide6" in missing_python:
    try:
        install_python(["PySide6"])
    except Exception as e:
        print(f"Не удалось установить PySide6:\n{e}")
        sys.exit(1)

    os.execv(sys.executable, [sys.executable] + sys.argv)
    sys.exit()

# Теперь можно использовать GUI
if missing_python or missing_apt:
    from installer_gui import show_installer

    ok = show_installer(
        missing_python,
        missing_apt
    )

    if not ok:
        sys.exit()

    os.execv(sys.executable, [sys.executable] + sys.argv)
    sys.exit()

# Всё установлено — запускаем программу
import main