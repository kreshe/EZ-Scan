import json
import os
import shutil
from pathlib import Path


# ============================================================
# ПУТИ
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

APP_NAME = "EZ SCAN"

CONFIG_DIR = (
    Path.home()
    / ".config"
    / APP_NAME
)

CONFIG_FILE = CONFIG_DIR / "config.json"


# ============================================================
# ЗАДЕРЖКИ ПО УМОЛЧАНИЮ
# ============================================================

DEFAULT_DELAYS = {

    "click": 0.3,

    "paste": 1.0,

    "enter": 1.5,

    "before_buttons": 1.7,

    "button_click": 0.5,

    "after_batch": 2.0,

    "after_buttons": 1.0,

    "between_batches": 3.0
}


# ============================================================
# ПРОФИЛЬ ПО УМОЛЧАНИЮ
# ============================================================

DEFAULT_PROFILE = {

    "buffer_size": 24,

    "batch_size": 12,

    "auto_send": True,

    "press_enter": True,

    "ignore_duplicates": True,

    "workflow": {

        "input_stage": [],

        "button_stage": []
    },

    "positions": {},

    "delays": DEFAULT_DELAYS.copy()
}


# ============================================================
# ОСНОВНОЙ CONFIG
# ============================================================

DEFAULT_CONFIG = {
    "update_check": {
    "enabled": True,
    "interval_hours": 24,
    "last_check": 0
},
    "first_run": True,
    "show_welcome": True,
    "active_profile": "По умолчанию",
    "scanner": {
        "selected_device": ""
    },
    "hotkeys": {

        "send": "F1",

        "stop": "F2",

        "clear": "F3",

        "auto": "F4",

        "settings": "F5",

        "profile": "F6"
    },

    "profiles": {

        "По умолчанию": DEFAULT_PROFILE
    }
}


# ============================================================
# КОПИЯ DEFAULT CONFIG
# ============================================================

def default_config():

    return json.loads(
        json.dumps(
            DEFAULT_CONFIG,
            ensure_ascii=False
        )
    )


# ============================================================
# MERGE
# ============================================================

def merge_config(default, current):

    result = {}

    if not isinstance(current, dict):

        current = {}

    for key, value in default.items():

        if isinstance(value, dict):

            result[key] = merge_config(
                value,
                current.get(
                    key,
                    {}
                )
                if isinstance(
                    current.get(key),
                    dict
                )
                else {}
            )

        else:

            if key in current:

                result[key] = current[key]

            else:

                result[key] = value

    # --------------------------------------------------------
    # Сохраняем дополнительные поля
    # --------------------------------------------------------

    for key, value in current.items():

        if key not in result:

            result[key] = value

    return result


# ============================================================
# НОРМАЛИЗАЦИЯ ПРОФИЛЕЙ
# ============================================================

def normalize_profiles(cfg):

    profiles = cfg.setdefault(
        "profiles",
        {}
    )

    if not isinstance(
        profiles,
        dict
    ):

        profiles = {}

        cfg["profiles"] = profiles

    # --------------------------------------------------------
    # Если профилей вообще нет
    # --------------------------------------------------------

    if not profiles:

        profiles[
            "По умолчанию"
        ] = default_config()[
            "profiles"
        ][
            "По умолчанию"
        ]

    # --------------------------------------------------------
    # Обновляем каждый профиль
    # --------------------------------------------------------

    default_profile = default_config()[
        "profiles"
    ][
        "По умолчанию"
    ]

    for name in list(
        profiles.keys()
    ):

        profile = profiles[name]

        if not isinstance(
            profile,
            dict
        ):

            profile = {}

        profiles[name] = merge_config(
            default_profile,
            profile
        )

    # --------------------------------------------------------
    # Проверяем активный профиль
    # --------------------------------------------------------

    active = cfg.get(
        "active_profile",
        "По умолчанию"
    )

    if active not in profiles:

        active = "По умолчанию"

        if active not in profiles:

            profiles[active] = merge_config(
                default_profile,
                {}
            )

    cfg["active_profile"] = active

    return cfg


# ============================================================
# LOAD
# ============================================================

def load():

    CONFIG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # CONFIG НЕ СУЩЕСТВУЕТ
    # --------------------------------------------------------

    if not CONFIG_FILE.exists():

        cfg = default_config()

        save(cfg)

        return cfg

    # --------------------------------------------------------
    # ЧТЕНИЕ
    # --------------------------------------------------------

    try:

        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            cfg = json.load(f)

    except Exception as e:

        print(
            f"⚠ Ошибка config.json: {e}"
        )

        backup = CONFIG_FILE.with_name(
            "config.json.broken"
        )

        try:

            shutil.copy2(
                CONFIG_FILE,
                backup
            )

            print(
                f"📦 Резервная копия: {backup}"
            )

        except Exception as backup_error:

            print(
                "⚠ Не удалось создать резервную копию:",
                backup_error
            )

        cfg = default_config()

        save(cfg)

        print(
            "🔄 Создан новый config.json"
        )

        return cfg

    # --------------------------------------------------------
    # MERGE
    # --------------------------------------------------------

    defaults = default_config()

    cfg = merge_config(
        defaults,
        cfg
    )

    # --------------------------------------------------------
    # ПРОФИЛИ
    # --------------------------------------------------------

    cfg = normalize_profiles(
        cfg
    )

    # --------------------------------------------------------
    # Если конфигурация изменилась
    # --------------------------------------------------------

    try:

        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            old_cfg = json.load(f)

    except Exception:

        old_cfg = None

    if old_cfg != cfg:

        save(cfg)

    return cfg


# ============================================================
# SAVE
# ============================================================

def save(cfg):

    CONFIG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    temp = CONFIG_FILE.with_suffix(
        ".json.tmp"
    )

    with open(
        temp,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            cfg,
            f,
            indent=4,
            ensure_ascii=False
        )

        f.write("\n")

    os.replace(
        temp,
        CONFIG_FILE
    )


# ============================================================
# GET
# ============================================================

def get(
    key,
    default=None
):

    cfg = load()

    return cfg.get(
        key,
        default
    )


# ============================================================
# SET
# ============================================================

def set(
    key,
    value
):

    cfg = load()

    cfg[key] = value

    save(cfg)


# ============================================================
# ACTIVE PROFILE
# ============================================================

def get_active_profile():

    cfg = load()

    name = cfg.get(
        "active_profile",
        "По умолчанию"
    )

    profiles = cfg.get(
        "profiles",
        {}
    )

    profile = profiles.get(
        name
    )

    if profile is None:

        name = "По умолчанию"

        profile = profiles.setdefault(
            name,
            default_config()[
                "profiles"
            ][
                name
            ]
        )

        cfg["active_profile"] = name

        save(cfg)

    return profile


# ============================================================
# ACTIVE PROFILE NAME
# ============================================================

def get_active_profile_name():

    cfg = load()

    return cfg.get(
        "active_profile",
        "По умолчанию"
    )
    
from time import time

def should_check_updates():

    cfg = load()

    settings = cfg.setdefault(
        "update_check",
        {
            "enabled": True,
            "interval_hours": 24,
            "last_check": 0
        }
    )

    if not settings.get(
        "enabled",
        True
    ):

        return False

    now = time()

    last = settings.get(
        "last_check",
        0
    )

    interval = (
        settings.get(
            "interval_hours",
            24
        )
        * 3600
    )

    if now - last < interval:

        return False

    settings["last_check"] = now

    save(
        cfg
    )

    return True