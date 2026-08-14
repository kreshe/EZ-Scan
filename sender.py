import time
import subprocess
import pyperclip

from config import load


# ============================================================
# АКТИВНЫЙ ПРОФИЛЬ
# ============================================================

def get_active_profile():

    cfg = load()

    profile_name = cfg.get(
        "active_profile",
        "По умолчанию"
    )

    profiles = cfg.get(
        "profiles",
        {}
    )

    profile = profiles.get(
        profile_name
    )

    if profile is None:

        raise RuntimeError(
            f"Активный профиль не найден: {profile_name}"
        )

    return profile


# ============================================================
# КЛИК ПО КООРДИНАТАМ
# ============================================================

def click_xy(x, y):

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


# ============================================================
# КЛИК ПО ОБУЧЕННОМУ ДЕЙСТВИЮ
# ============================================================

def click_action(action, profile):

    positions = profile.get(
        "positions",
        {}
    )

    if action not in positions:

        print(
            "❌ Нет координат:",
            action
        )

        return False

    pos = positions[action]

    x = pos.get(
        "x",
        0
    )

    y = pos.get(
        "y",
        0
    )

    if x == 0 and y == 0:

        print(
            "❌ Не обучено:",
            action
        )

        return False

    print(
        f"🖱 Клик: {action} → ({x}, {y})"
    )

    click_xy(
        x,
        y
    )

    return True


# ============================================================
# ВСТАВКА
# ============================================================

def paste_text(text):

    pyperclip.copy(
        str(text)
    )

    subprocess.call(
        [
            "xdotool",
            "key",
            "--clearmodifiers",
            "ctrl+v"
        ]
    )


# ============================================================
# ENTER
# ============================================================

def press_enter():

    print(
        ">>> ENTER"
    )

    subprocess.call(
        [
            "xdotool",
            "key",
            "Return"
        ]
    )


# ============================================================
# ОСТАНОВКА
# ============================================================

def is_running(thread):

    if thread is None:

        return True

    return thread.running


# ============================================================
# ОТПРАВКА ПАЧКИ
# ============================================================

def execute_batch(
    codes,
    progress=None,
    thread=None
):

    # ========================================================
    # ЗАГРУЖАЕМ ИМЕННО АКТИВНЫЙ ПРОФИЛЬ
    # ========================================================

    profile = get_active_profile()

    profile_name = load().get(
        "active_profile",
        "По умолчанию"
    )

    print()
    print(
        "=" * 50
    )

    print(
        "ПРОФИЛЬ:",
        profile_name
    )

    print(
        "QR В ПАЧКЕ:",
        len(codes)
    )

    print(
        "=" * 50
    )

    # ========================================================
    # НАСТРОЙКИ
    # ========================================================

    delays = profile.get(
        "delays",
        {}
    )

    click_delay = delays.get(
        "click",
        0.3
    )

    paste_delay = delays.get(
        "paste",
        1.0
    )

    enter_delay = delays.get(
        "enter",
        1.5
    )

    before_buttons_delay = delays.get(
        "before_buttons",
        1.7
    )

    button_delay = delays.get(
        "button_click",
        0.5
    )

    after_batch_delay = delays.get(
        "after_batch",
        2.0
    )

    # ========================================================
    # ENTER
    # ========================================================

    press_enter_enabled = profile.get(
        "press_enter",
        True
    )

    # ========================================================
    # WORKFLOW
    # ========================================================

    workflow = profile.get(
        "workflow",
        {}
    )

    inputs = workflow.get(
        "input_stage",
        []
    )

    buttons = workflow.get(
        "button_stage",
        []
    )

    # ========================================================
    # ПРОВЕРКА INPUT
    # ========================================================

    if len(inputs) < 2:

        print(
            "❌ Нужно минимум 2 input-поля"
        )

        return

    # ========================================================
    # ЭТАП 1
    # ЗАПОЛНЕНИЕ INPUT
    # ========================================================

    done = 0

    for index, code in enumerate(codes):

        # ----------------------------------------------------
        # ПРОВЕРКА ОСТАНОВКИ
        # ----------------------------------------------------

        if not is_running(thread):

            print(
                "🟠 Отправка остановлена"
            )

            return

        # ----------------------------------------------------
        # ВЫБИРАЕМ INPUT
        # ----------------------------------------------------

        if index == 0:

            field = inputs[0]

        else:

            field = inputs[1]

        print()
        print(
            f"📦 QR {index + 1}/{len(codes)}"
        )

        print(
            "INPUT:",
            field
        )

        print(
            "CODE:",
            code
        )

        # ----------------------------------------------------
        # КЛИК
        # ----------------------------------------------------

        if not click_action(
            field,
            profile
        ):

            print(
                "❌ Не удалось нажать:",
                field
            )

            return

        time.sleep(
            click_delay
        )

        # ----------------------------------------------------
        # PASTE
        # ----------------------------------------------------

        paste_text(
            code
        )

        time.sleep(
            paste_delay
        )

        # ----------------------------------------------------
        # ENTER
        # ----------------------------------------------------

        if press_enter_enabled:

            time.sleep(
                enter_delay
            )

            press_enter()

        # ----------------------------------------------------
        # ПРОГРЕСС
        # ----------------------------------------------------

        done += 1

        if progress:

            progress.emit(
                done
            )

        time.sleep(
            click_delay
        )

    # ========================================================
    # ЭТАП 2
    # КНОПКИ
    # ========================================================

    print()
    print(
        "⏳ Ожидание перед кнопками..."
    )

    time.sleep(
        before_buttons_delay
    )

    # ========================================================
    # НАЖАТИЕ КНОПОК
    # ========================================================

    for button in buttons:

        if not is_running(thread):

            print(
                "🟠 Остановка перед кнопками"
            )

            return

        print(
            "BUTTON:",
            button
        )

        if not click_action(
            button,
            profile
        ):

            print(
                "❌ Не удалось нажать кнопку:",
                button
            )

            return

        time.sleep(
            button_delay
        )

    # ========================================================
    # ЗАВЕРШЕНИЕ ПАЧКИ
    # ========================================================

    print(
        "⏳ Ожидание после пачки..."
    )

    time.sleep(
        after_batch_delay
    )

    print(
        "✅ Пачка завершена"
    )

    print(
        "=" * 50
    )