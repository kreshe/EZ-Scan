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
# ТЕКУЩЕЕ РАЗРЕШЕНИЕ ЭКРАНА
# ============================================================

def get_current_screen_size():

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

        return (
            width,
            height
        )

    except Exception as e:

        print(
            "⚠ Не удалось определить разрешение экрана:",
            e
        )

        return (
            None,
            None
        )


# ============================================================
# МАСШТАБИРОВАНИЕ КООРДИНАТ
# ============================================================

def scale_position(position):

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

    # --------------------------------------------------------
    # Старый профиль
    # --------------------------------------------------------

    if not saved_width or not saved_height:

        print(
            "ℹ Координаты без информации о разрешении."
        )

        return (
            x,
            y
        )

    # --------------------------------------------------------
    # Текущий экран
    # --------------------------------------------------------

    current_width, current_height = (
        get_current_screen_size()
    )

    if not current_width or not current_height:

        return (
            x,
            y
        )

    # --------------------------------------------------------
    # Разрешение не изменилось
    # --------------------------------------------------------

    if (
        current_width == saved_width
        and
        current_height == saved_height
    ):

        return (
            x,
            y
        )

    # --------------------------------------------------------
    # Масштабирование
    # --------------------------------------------------------

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
        "📐 Масштабирование координат:"
    )

    print(
        f"   Было: "
        f"({x}, {y})"
    )

    print(
        f"   Экран обучения: "
        f"{saved_width}x{saved_height}"
    )

    print(
        f"   Текущий экран: "
        f"{current_width}x{current_height}"
    )

    print(
        f"   Стало: "
        f"({scaled_x}, {scaled_y})"
    )

    return (
        scaled_x,
        scaled_y
    )


# ============================================================
# КЛИК ПО КООРДИНАТАМ
# ============================================================

def click_xy(
    x,
    y
):

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

def click_action(
    action,
    profile
):

    positions = profile.get(
        "positions",
        {}
    )

    # --------------------------------------------------------
    # Есть ли действие
    # --------------------------------------------------------

    if action not in positions:

        print(
            "❌ Нет координат:",
            action
        )

        return False

    position = positions[action]

    # --------------------------------------------------------
    # Исходные координаты
    # --------------------------------------------------------

    raw_x = position.get(
        "x",
        0
    )

    raw_y = position.get(
        "y",
        0
    )

    # --------------------------------------------------------
    # Координаты не обучены
    # --------------------------------------------------------

    if (
        raw_x == 0
        and
        raw_y == 0
    ):

        print(
            "❌ Не обучено:",
            action
        )

        return False

    # --------------------------------------------------------
    # Масштабируем
    # --------------------------------------------------------

    x, y = scale_position(
        position
    )

    print(
        f"🖱 Клик: "
        f"{action} → ({x}, {y})"
    )

    click_xy(
        x,
        y
    )

    return True


# ============================================================
# ВСТАВКА
# ============================================================

def paste_text(
    text
):

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

def is_running(
    thread
):

    if thread is None:

        return True

    return thread.running


# ============================================================
# ПРОВЕРКА WORKFLOW
# ============================================================

def validate_workflow(
    profile
):

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

    positions = profile.get(
        "positions",
        {}
    )

    # --------------------------------------------------------
    # Минимум два input
    # --------------------------------------------------------

    if len(inputs) < 2:

        return False, (
            "Нужно минимум 2 input-поля."
        )

    # --------------------------------------------------------
    # Проверяем input
    # --------------------------------------------------------

    for action in inputs:

        position = positions.get(
            action
        )

        if not position:

            return False, (
                f"Не обучено действие: {action}"
            )

        if (
            position.get("x", 0) == 0
            and
            position.get("y", 0) == 0
        ):

            return False, (
                f"Не обучено действие: {action}"
            )

    # --------------------------------------------------------
    # Проверяем кнопки
    # --------------------------------------------------------

    for action in buttons:

        position = positions.get(
            action
        )

        if not position:

            return False, (
                f"Не обучена кнопка: {action}"
            )

        if (
            position.get("x", 0) == 0
            and
            position.get("y", 0) == 0
        ):

            return False, (
                f"Не обучена кнопка: {action}"
            )

    return (
        True,
        ""
    )


# ============================================================
# ОТПРАВКА ПАЧКИ
# ============================================================

def execute_batch(
    codes,
    progress=None,
    thread=None
):

    # ========================================================
    # АКТИВНЫЙ ПРОФИЛЬ
    # ========================================================

    profile = get_active_profile()

    cfg = load()

    profile_name = cfg.get(
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
    # ПРОВЕРКА WORKFLOW
    # ========================================================

    valid, error = validate_workflow(
        profile
    )

    if not valid:

        print(
            "❌",
            error
        )

        if thread:

            try:

                thread.error.emit(
                    error
                )

            except Exception:

                pass

        return

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
    # ЭТАП 1
    # ЗАПОЛНЕНИЕ INPUT
    # ========================================================

    done = 0

    for index, code in enumerate(
        codes
    ):

        # ----------------------------------------------------
        # STOP
        # ----------------------------------------------------

        if not is_running(
            thread
        ):

            print(
                "🟠 Отправка остановлена"
            )

            return

        # ----------------------------------------------------
        # INPUT
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
        # CLICK INPUT
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
        # PROGRESS
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
    # ПЕРЕД КНОПКАМИ
    # ========================================================

    if not is_running(
        thread
    ):

        print(
            "🟠 Остановка перед кнопками"
        )

        return

    print()
    print(
        "⏳ Ожидание перед кнопками..."
    )

    time.sleep(
        before_buttons_delay
    )

    # ========================================================
    # КНОПКИ
    # ========================================================

    for button in buttons:

        if not is_running(
            thread
        ):

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
    # ПОСЛЕ ПАЧКИ
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