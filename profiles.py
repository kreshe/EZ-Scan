from copy import deepcopy

from config import load, save
from config import (
    load,
    save,
    DEFAULT_CONFIG
)


PROFILE_KEYS = [
    "buffer_size",
    "batch_size",
    "auto_send",
    "press_enter",
    "ignore_duplicates",
    "workflow",
    "positions",
    "delays"
]



def rename_profile(old_name, new_name):

    old_name = old_name.strip()
    new_name = new_name.strip()

    if not old_name or not new_name:
        return False

    if old_name == new_name:
        return True

    cfg = load()

    profiles = cfg.setdefault(
        "profiles",
        {}
    )

    # Старого профиля нет
    if old_name not in profiles:
        return False

    # Новое имя уже занято
    if new_name in profiles:
        return False

    # Переносим настройки под новым именем
    profiles[new_name] = profiles.pop(
        old_name
    )

    # Если переименовали активный профиль —
    # меняем и active_profile
    if cfg.get("active_profile") == old_name:

        cfg["active_profile"] = new_name

    save(cfg)

    return True

def get_profiles():

    cfg = load()

    return cfg.setdefault(
        "profiles",
        {}
    )


def get_active_profile():

    cfg = load()

    return cfg.get(
        "active_profile",
        "По умолчанию"
    )


def get_profile(name):

    cfg = load()

    profiles = cfg.setdefault(
        "profiles",
        {}
    )

    if name not in profiles:

        profiles[name] = create_profile_from_config(
            cfg
        )

        save(cfg)

    return profiles[name]


def create_profile_from_config(cfg):

    profile = {}

    for key in PROFILE_KEYS:

        if key in cfg:

            profile[key] = deepcopy(
                cfg[key]
            )

    return profile


def save_current_to_profile(name):

    cfg = load()

    profiles = cfg.setdefault(
        "profiles",
        {}
    )

    profiles[name] = create_profile_from_config(
        cfg
    )

    cfg["active_profile"] = name

    save(cfg)


def load_profile(name):

    cfg = load()

    profiles = cfg.setdefault(
        "profiles",
        {}
    )

    if name not in profiles:

        return False

    profile = profiles[name]

    for key in PROFILE_KEYS:

        if key in profile:

            cfg[key] = deepcopy(
                profile[key]
            )

    cfg["active_profile"] = name

    save(cfg)

    return True


def create_profile(name):

    cfg = load()

    profiles = cfg.setdefault(
        "profiles",
        {}
    )

    if not name:

        return False

    if name in profiles:

        return False

    profiles[name] = create_profile_from_config(
        cfg
    )

    cfg["active_profile"] = name

    save(cfg)

    return True


def delete_profile(name):

    cfg = load()

    profiles = cfg.setdefault(
        "profiles",
        {}
    )

    if name == "По умолчанию":

        return False

    if name not in profiles:

        return False

    del profiles[name]

    if cfg.get("active_profile") == name:

        cfg["active_profile"] = "По умолчанию"

        if "По умолчанию" in profiles:

            for key in PROFILE_KEYS:

                if key in profiles["По умолчанию"]:

                    cfg[key] = deepcopy(
                        profiles["По умолчанию"][key]
                    )

    save(cfg)

    return True