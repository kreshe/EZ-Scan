import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

from pathlib import Path


GITHUB_API = (
    "https://api.github.com/repos/"
    "kreshe/EZ-Scan/releases/latest"
)

APPIMAGE_PATTERN = re.compile(
    r"\.AppImage$",
    re.IGNORECASE
)


def normalize_version(value):

    value = str(value or "").strip()

    if value.lower().startswith("v"):
        value = value[1:]

    result = []

    for part in value.split("."):

        match = re.match(
            r"\d+",
            part
        )

        if match:
            result.append(
                int(match.group())
            )
        else:
            result.append(0)

    while len(result) < 3:
        result.append(0)

    return tuple(
        result[:3]
    )


def is_newer(current, remote):

    return normalize_version(
        remote
    ) > normalize_version(
        current
    )


def fetch_latest_release():

    request = urllib.request.Request(
        GITHUB_API,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "EZ-Scan-Updater"
        }
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:

            data = json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

        return data

    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        json.JSONDecodeError
    ):

        return None


def find_appimage_asset(release):

    if not release:
        return None

    assets = release.get(
        "assets",
        []
    )

    for asset in assets:

        name = asset.get(
            "name",
            ""
        )

        if APPIMAGE_PATTERN.search(name):

            return asset

    return None


def get_sha256(path):

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


def download_file(
    url,
    destination,
    progress_callback=None
):

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "EZ-Scan-Updater"
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=30
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

                    percent = int(
                        downloaded
                        * 100
                        / total
                    )

                    progress_callback(
                        percent
                    )


def get_current_appimage_path():

    # AppImage запускается через /tmp/.mount...
    # поэтому ищем реальный путь через APPIMAGE.

    appimage = os.environ.get(
        "APPIMAGE"
    )

    if appimage:

        return Path(
            appimage
        ).resolve()

    return None


def get_update_info(current_version):

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
            "error": (
                "В релизе нет AppImage."
            )
        }

    return {
        "update_available": True,
        "version": remote_version,
        "name": release.get(
            "name",
            remote_version
        ),
        "notes": release.get(
            "body",
            ""
        ),
        "download_url": asset.get(
            "browser_download_url"
        ),
        "size": asset.get(
            "size",
            0
        ),
        "digest": asset.get(
            "digest"
        ),
        "release_url": release.get(
            "html_url"
        )
    }


def download_update(
    info,
    progress_callback=None
):

    if not info:
        return None

    url = info.get(
        "download_url"
    )

    if not url:
        return None

    temp_dir = Path(
        tempfile.mkdtemp(
            prefix="ez-scan-update-"
        )
    )

    filename = info.get(
        "name",
        "EZ-Scan-update"
    )

    asset_name = Path(
        url.split("/")[-1]
    ).name

    if asset_name:
        filename = asset_name

    destination = (
        temp_dir
        / filename
    )

    download_file(
        url,
        destination,
        progress_callback
    )

    os.chmod(
        destination,
        0o755
    )

    return destination