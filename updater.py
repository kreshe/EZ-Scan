import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request

from pathlib import Path


GITHUB_API = (
    "https://api.github.com/repos/"
    "kreshe/EZ-Scan/releases/latest"
)

APP_NAME = "EZ SCAN"

CONFIG_DIR = (
    Path.home()
    / ".config"
    / APP_NAME
)

UPDATE_STATE_FILE = (
    CONFIG_DIR
    / "update_state.json"
)

APPIMAGE_PATTERN = re.compile(
    r"\.AppImage$",
    re.IGNORECASE
)


# ============================================================
# VERSION
# ============================================================

def normalize_version(version):

    version = str(
        version or ""
    ).strip()

    if version.lower().startswith("v"):

        version = version[1:]

    result = []

    for part in version.split("."):

        match = re.match(
            r"\d+",
            part
        )

        if match:

            result.append(
                int(
                    match.group()
                )
            )

        else:

            result.append(
                0
            )

    while len(result) < 3:

        result.append(
            0
        )

    return tuple(
        result[:3]
    )


def is_newer(
    current,
    remote
):

    return (
        normalize_version(remote)
        >
        normalize_version(current)
    )


# ============================================================
# APPIMAGE
# ============================================================

def get_current_appimage():

    value = os.environ.get(
        "APPIMAGE"
    )

    if not value:

        return None

    path = Path(
        value
    ).resolve()

    if path.exists():

        return path

    return None


def running_as_appimage():

    return (
        get_current_appimage()
        is not None
    )


# ============================================================
# GITHUB
# ============================================================

def fetch_latest_release():

    request = urllib.request.Request(
        GITHUB_API,
        headers={
            "Accept":
                "application/vnd.github+json",

            "User-Agent":
                "EZ-Scan-Updater"
        }
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:

            return json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

    except Exception as e:

        print(
            "GitHub update check error:",
            e
        )

        return None


def find_appimage_asset(
    release
):

    if not release:

        return None

    for asset in release.get(
        "assets",
        []
    ):

        name = asset.get(
            "name",
            ""
        )

        if APPIMAGE_PATTERN.search(
            name
        ):

            return asset

    return None


def get_update_info(
    current_version
):

    release = fetch_latest_release()

    if not release:

        return None

    remote_version = release.get(
        "tag_name",
        ""
    )

    if not is_newer(
        current_version,
        remote_version
    ):

        return {
            "update_available": False,
            "version": remote_version
        }

    asset = find_appimage_asset(
        release
    )

    if not asset:

        return {
            "update_available": False,
            "version": remote_version,
            "error":
                "В Release отсутствует AppImage."
        }

    return {
        "update_available": True,

        "version":
            remote_version,

        "name":
            release.get(
                "name",
                remote_version
            ),

        "notes":
            release.get(
                "body",
                ""
            ),

        "download_url":
            asset.get(
                "browser_download_url"
            ),

        "asset_name":
            asset.get(
                "name"
            ),

        "digest":
            asset.get(
                "digest"
            ),

        "release_url":
            release.get(
                "html_url"
            ),

        "size":
            asset.get(
                "size",
                0
            )
    }


# ============================================================
# SHA-256
# ============================================================

def sha256_file(
    path
):

    sha256 = hashlib.sha256()

    with open(
        path,
        "rb"
    ) as file:

        while True:

            chunk = file.read(
                1024 * 1024
            )

            if not chunk:

                break

            sha256.update(
                chunk
            )

    return sha256.hexdigest()


def verify_digest(
    path,
    digest
):

    if not digest:

        # Старый Release без digest
        return True

    if ":" in digest:

        algorithm, expected = (
            digest.split(
                ":",
                1
            )
        )

    else:

        algorithm = "sha256"
        expected = digest

    if algorithm.lower() != "sha256":

        return False

    actual = sha256_file(
        path
    )

    return (
        actual.lower()
        ==
        expected.lower()
    )


# ============================================================
# DOWNLOAD
# ============================================================

def download_update(
    info,
    progress_callback=None
):

    url = info.get(
        "download_url"
    )

    if not url:

        raise RuntimeError(
            "URL обновления отсутствует."
        )

    temp_dir = Path(
        tempfile.mkdtemp(
            prefix="ez-scan-update-"
        )
    )

    filename = info.get(
        "asset_name",
        "EZ-SCAN-update.AppImage"
    )

    destination = (
        temp_dir
        / filename
    )

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent":
                "EZ-Scan-Updater"
        }
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=60
        ) as response:

            total = response.headers.get(
                "Content-Length"
            )

            total = (
                int(total)
                if total
                else 0
            )

            downloaded = 0

            with open(
                destination,
                "wb"
            ) as file:

                while True:

                    chunk = response.read(
                        1024 * 1024
                    )

                    if not chunk:

                        break

                    file.write(
                        chunk
                    )

                    downloaded += len(
                        chunk
                    )

                    if (
                        progress_callback
                        and total
                    ):

                        progress_callback(
                            int(
                                downloaded
                                * 100
                                / total
                            )
                        )

    except Exception:

        shutil.rmtree(
            temp_dir,
            ignore_errors=True
        )

        raise

    # --------------------------------------------------------
    # VERIFY
    # --------------------------------------------------------

    if not verify_digest(
        destination,
        info.get(
            "digest"
        )
    ):

        shutil.rmtree(
            temp_dir,
            ignore_errors=True
        )

        raise RuntimeError(
            "❌ SHA-256 проверка обновления "
            "не пройдена."
        )

    try:

        os.chmod(
            destination,
            destination.stat().st_mode
            | 0o111
        )

    except Exception:
        pass

    return destination


# ============================================================
# UPDATE STATE
# ============================================================

def save_update_state(
    state
):

    CONFIG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    UPDATE_STATE_FILE.write_text(
        json.dumps(
            state,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def load_update_state():

    if not UPDATE_STATE_FILE.exists():

        return None

    try:

        return json.loads(
            UPDATE_STATE_FILE.read_text(
                encoding="utf-8"
            )
        )

    except Exception:

        return None


def clear_update_state():

    try:

        UPDATE_STATE_FILE.unlink(
            missing_ok=True
        )

    except Exception:
        pass


# ============================================================
# UPDATE SUCCESS MARKER
# ============================================================

def get_success_marker(
    token
):

    return (
        CONFIG_DIR
        / f"update_success_{token}"
    )


def mark_update_success():

    token = os.environ.get(
        "EZSCAN_UPDATE_TOKEN"
    )

    if not token:

        return

    CONFIG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    marker = get_success_marker(
        token
    )

    marker.write_text(
        "ok",
        encoding="utf-8"
    )


# ============================================================
# EXTERNAL UPDATE HELPER
# ============================================================

def create_update_helper(
    current_appimage,
    downloaded_appimage,
    token,
    new_version
):

    current_appimage = Path(
        current_appimage
    ).resolve()

    downloaded_appimage = Path(
        downloaded_appimage
    ).resolve()

    backup = Path(
        str(current_appimage)
        + ".bak"
    )

    marker = get_success_marker(
        token
    )

    helper_dir = Path(
        tempfile.mkdtemp(
            prefix="ez-scan-helper-"
        )
    )

    helper = (
        helper_dir
        / "update.sh"
    )

    script = f"""#!/bin/bash

set -u

CURRENT="{current_appimage}"
NEW="{downloaded_appimage}"
BACKUP="{backup}"
MARKER="{marker}"

sleep 1

rm -f "$MARKER"

if [ -f "$CURRENT" ]; then
    cp -f "$CURRENT" "$BACKUP"
fi

cp -f "$NEW" "$CURRENT"

chmod +x "$CURRENT"

rm -f "$NEW"

EZSCAN_UPDATE_TOKEN="{token}" \\
"$CURRENT" --updated >/dev/null 2>&1 &

NEW_PID=$!

for i in $(seq 1 30); do

    if [ -f "$MARKER" ]; then

        rm -f "$MARKER"

        echo "UPDATE_OK"

        exit 0

    fi

    if ! kill -0 "$NEW_PID" 2>/dev/null; then

        break

    fi

    sleep 1

done

echo "UPDATE_FAILED"

if [ -f "$BACKUP" ]; then

    FAILED="${{CURRENT}}.failed"

    mv -f "$CURRENT" "$FAILED"

    mv -f "$BACKUP" "$CURRENT"

    chmod +x "$CURRENT"

    rm -f "$FAILED"

    rm -f "$MARKER"

    exec "$CURRENT"

fi

exit 1
"""

    helper.write_text(
        script,
        encoding="utf-8"
    )

    os.chmod(
        helper,
        0o755
    )

    save_update_state(
        {
            "token":
                token,

            "new_version":
                new_version,

            "current_appimage":
                str(
                    current_appimage
                ),

            "backup":
                str(
                    backup
                ),

            "status":
                "pending"
        }
    )

    return helper, backup


# ============================================================
# START UPDATE
# ============================================================

def start_update(
    downloaded_appimage,
    new_version
):

    current = get_current_appimage()

    if not current:

        raise RuntimeError(
            "EZ Scan не запущен как AppImage."
        )

    token = (
        os.urandom(16).hex()
    )

    helper, backup = (
        create_update_helper(
            current,
            downloaded_appimage,
            token,
            new_version
        )
    )

    subprocess.Popen(
        [
            "bash",
            str(helper)
        ],
        start_new_session=True
    )

    return backup


# ============================================================
# ROLLBACK
# ============================================================

def create_rollback_helper(
    current_appimage
):

    current_appimage = Path(
        current_appimage
    ).resolve()

    backup = Path(
        str(current_appimage)
        + ".bak"
    )

    if not backup.exists():

        raise RuntimeError(
            "Резервная версия отсутствует."
        )

    helper_dir = Path(
        tempfile.mkdtemp(
            prefix="ez-scan-rollback-"
        )
    )

    helper = (
        helper_dir
        / "rollback.sh"
    )

    script = f"""#!/bin/bash

set -u

CURRENT="{current_appimage}"
BACKUP="{backup}"

sleep 1

FAILED="${{CURRENT}}.failed"

if [ -f "$CURRENT" ]; then

    mv -f "$CURRENT" "$FAILED"

fi

mv -f "$BACKUP" "$CURRENT"

chmod +x "$CURRENT"

rm -f "$FAILED"

exec "$CURRENT"

"""

    helper.write_text(
        script,
        encoding="utf-8"
    )

    os.chmod(
        helper,
        0o755
    )

    return helper


def start_rollback():

    current = get_current_appimage()

    if not current:

        raise RuntimeError(
            "EZ Scan не запущен как AppImage."
        )

    helper = (
        create_rollback_helper(
            current
        )
    )

    subprocess.Popen(
        [
            "bash",
            str(helper)
        ],
        start_new_session=True
    )

    return True