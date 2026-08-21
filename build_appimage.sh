#!/bin/bash

set -e

APP_NAME="EZ Scan"
APP_VERSION="2.2"
ARCH="x86_64"

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

BUILD_DIR="$PROJECT_DIR/build"
APPDIR="$BUILD_DIR/AppDir"
VENV="$BUILD_DIR/venv"

OUTPUT_DIR="$PROJECT_DIR/dist"

APPIMAGE_NAME="${APP_NAME}V${APP_VERSION}.AppImage"


echo
echo "=========================================="
echo "       EZ SCAN AppImage Builder"
echo "=========================================="
echo


# ============================================================
# CHECK TOOLS
# ============================================================

echo "[0/10] Проверка инструментов..."

for COMMAND in python3 wget file pkexec; do

    if ! command -v "$COMMAND" >/dev/null 2>&1; then

        echo
        echo "❌ Не найдено: $COMMAND"
        echo
        echo "Установите:"
        echo
        echo "sudo apt install $COMMAND"
        echo

        exit 1

    fi

done

echo "✅ Инструменты найдены"


# ============================================================
# ICON
# ============================================================

echo
echo "Проверка иконки..."

if [ ! -f "$PROJECT_DIR/icon.png" ]; then

    echo
    echo "❌ Не найден:"
    echo "$PROJECT_DIR/icon.png"
    echo

    exit 1

fi

echo "✅ Иконка найдена"

file "$PROJECT_DIR/icon.png"


# ============================================================
# CLEAN
# ============================================================

echo
echo "[1/10] Очистка..."

rm -rf "$BUILD_DIR"

mkdir -p "$BUILD_DIR"
mkdir -p "$OUTPUT_DIR"


# ============================================================
# VENV
# ============================================================

echo
echo "[2/10] Создание Python окружения..."

python3 -m venv "$VENV"

source "$VENV/bin/activate"

python -m pip install --upgrade pip


# ============================================================
# DEPENDENCIES
# ============================================================

echo
echo "[3/10] Установка зависимостей..."

python -m pip install \
    PySide6 \
    evdev \
    pyperclip


echo
echo "Проверка зависимостей..."

"$VENV/bin/python" -c "
import PySide6
import evdev
import pyperclip

print('✅ PySide6')
print('✅ evdev')
print('✅ pyperclip')
"


# ============================================================
# PROJECT CHECK
# ============================================================

echo
echo "[4/10] Проверка проекта..."

REQUIRED_FILES=(
    "main.py"
    "bootstrap.py"
    "setup_window.py"

    "buffer.py"
    "scanner.py"
    "sender.py"
    "trainer.py"
    "settings.py"
    "config.py"

    "queue_window.py"
    "status_widget.py"

    "version.py"

    "profile_window.py"
    "profiles.py"

    "welcome.py"
    "guide.py"

    "updater.py"
    "update_window.py"
    "recovery_window.py"
    "app_menu_manager.py"
    "scanner_window.py"
)


for FILE in "${REQUIRED_FILES[@]}"; do

    if [ ! -f "$PROJECT_DIR/$FILE" ]; then

        echo
        echo "❌ Не найден:"
        echo "$FILE"
        echo

        exit 1

    fi

done


echo "✅ Все файлы найдены"


# ============================================================
# APPDIR
# ============================================================

echo
echo "[5/10] Создание AppDir..."

mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/lib"

mkdir -p \
    "$APPDIR/usr/share/applications"

mkdir -p \
    "$APPDIR/usr/share/icons/hicolor/128x128/apps"

mkdir -p \
    "$APPDIR/usr/share/icons/hicolor/256x256/apps"

mkdir -p \
    "$APPDIR/usr/share/icons/hicolor/512x512/apps"

mkdir -p \
    "$APPDIR/usr/share/metainfo"


# ============================================================
# PYTHON
# ============================================================

echo
echo "[6/10] Копирование Python..."

PYTHON_BIN="$VENV/bin/python"

cp \
    "$PYTHON_BIN" \
    "$APPDIR/usr/bin/python3"


PYTHON_VERSION=$(
    "$VENV/bin/python" -c \
    "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
)


SITE_PACKAGES="$VENV/lib/python${PYTHON_VERSION}/site-packages"

echo
echo "Python:"
echo "$PYTHON_VERSION"

echo
echo "Копирование библиотек..."


mkdir -p \
    "$APPDIR/usr/lib/python${PYTHON_VERSION}"


cp -r \
    "$SITE_PACKAGES" \
    "$APPDIR/usr/lib/python${PYTHON_VERSION}/"


# ============================================================
# APPLICATION
# ============================================================

APP="$APPDIR/usr/share/$APP_NAME"

mkdir -p "$APP"

echo
echo "Копирование приложения..."


cp \
    "$PROJECT_DIR"/*.py \
    "$APP/"


# ============================================================
# APPRUN
# ============================================================

echo
echo "Создание AppRun..."


cat > "$APPDIR/AppRun" <<EOF
#!/bin/bash

HERE="\$(dirname "\$(readlink -f "\$0")")"

export PATH="\$HERE/usr/bin:\$PATH"

export PYTHONPATH="\$HERE/usr/lib/python${PYTHON_VERSION}/site-packages"

cd "\$HERE/usr/share/$APP_NAME"

exec "\$HERE/usr/bin/python3" bootstrap.py "\$@"
EOF


chmod +x "$APPDIR/AppRun"


# ============================================================
# DESKTOP
# ============================================================

echo
echo "Создание desktop-файла..."


cat > "$APPDIR/ez-scan.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=EZ Scan
GenericName=QR Code Sender
Comment=Буферизация и автоматическая отправка QR-кодов
Exec=AppRun
Icon=qr-buffer
Terminal=false
Categories=Utility;
StartupNotify=true
StartupWMClass=EZ-SCAN
EOF


cp \
    "$APPDIR/ez-scan.desktop" \
    "$APPDIR/usr/share/applications/ez-scan.desktop"


# ============================================================
# ICONS
# ============================================================

echo
echo "Копирование иконок..."


cp \
    "$PROJECT_DIR/icon.png" \
    "$APPDIR/qr-buffer.png"


cp \
    "$PROJECT_DIR/icon.png" \
    "$APPDIR/usr/share/icons/hicolor/128x128/apps/qr-buffer.png"


cp \
    "$PROJECT_DIR/icon.png" \
    "$APPDIR/usr/share/icons/hicolor/256x256/apps/qr-buffer.png"


cp \
    "$PROJECT_DIR/icon.png" \
    "$APPDIR/usr/share/icons/hicolor/512x512/apps/qr-buffer.png"


echo "✅ Иконки установлены"


# ============================================================
# APPSTREAM
# ============================================================

echo
echo "Создание AppStream metadata..."


METADATA_DIR="$APPDIR/usr/share/metainfo"

mkdir -p "$METADATA_DIR"


cat > "$METADATA_DIR/com.ezscan.EZScan.metainfo.xml" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">

    <id>com.ezscan.EZScan</id>

    <name>EZ Scan</name>

    <summary>QR Code Buffer Sender</summary>

    <description>

        <p>
            EZ Scan — приложение для накопления
            QR-кодов и их автоматической отправки.
        </p>

        <p>
            Поддерживается работа со сканером,
            буферизация кодов, автоматическая отправка,
            профили, задержки, горячие клавиши
            и обучение координат мыши.
        </p>

    </description>

    <launchable type="desktop-id">
        ez-scan.desktop
    </launchable>

    <icon type="cached">
        qr-buffer
    </icon>

    <categories>
        <category>Utility</category>
    </categories>

    <provides>
        <binary>EZ-Scan</binary>
    </provides>

    <releases>

        <release
            version="2.1"
            date="2026-08-18">

            <description>

                <p>
                    EZ Scan 2.1.
                </p>

            </description>

        </release>

    </releases>

    <content_rating type="oars-1.1"/>

    <metadata_license>
        CC0-1.0
    </metadata_license>

</component>
EOF


echo "✅ AppStream metadata создан"


# ============================================================
# OPTIMIZATION
# ============================================================

echo
echo "[7/10] Оптимизация Python..."


find "$APPDIR" \
    -type d \
    -name "__pycache__" \
    -prune \
    -exec rm -rf {} +


find "$APPDIR" \
    -type f \
    \( \
        -name "*.pyc" \
        -o \
        -name "*.pyo" \
    \) \
    -delete


rm -rf \
    "$APPDIR/usr/lib/python${PYTHON_VERSION}/site-packages/pip" \
    "$APPDIR/usr/lib/python${PYTHON_VERSION}/site-packages/pip-"* \
    "$APPDIR/usr/lib/python${PYTHON_VERSION}/site-packages/setuptools" \
    "$APPDIR/usr/lib/python${PYTHON_VERSION}/site-packages/setuptools-"*


echo "✅ Оптимизация завершена"


# ============================================================
# APPIMAGETOOL
# ============================================================

echo
echo "[8/10] Подготовка appimagetool..."


APPIMAGETOOL="$BUILD_DIR/appimagetool"


if [ ! -f "$APPIMAGETOOL" ]; then

    wget -q \
        --show-progress \
        -O "$APPIMAGETOOL" \
        https://github.com/AppImage/appimagetool/releases/latest/download/appimagetool-x86_64.AppImage

    chmod +x "$APPIMAGETOOL"

fi


# ============================================================
# BUILD
# ============================================================

echo
echo "[9/10] Сборка AppImage..."


rm -f \
    "$OUTPUT_DIR/$APPIMAGE_NAME"


ARCH="$ARCH" \
    "$APPIMAGETOOL" \
    "$APPDIR" \
    "$OUTPUT_DIR/$APPIMAGE_NAME"


# ============================================================
# VERIFY
# ============================================================

echo
echo "[10/10] Проверка..."


if [ ! -f "$OUTPUT_DIR/$APPIMAGE_NAME" ]; then

    echo
    echo "❌ AppImage не создан!"
    exit 1

fi


chmod +x \
    "$OUTPUT_DIR/$APPIMAGE_NAME"


echo
echo "=========================================="
echo "          СБОРКА ЗАВЕРШЕНА"
echo "=========================================="
echo

echo "📦 AppImage:"
echo

ls -lh \
    "$OUTPUT_DIR/$APPIMAGE_NAME"

echo

echo "🎨 Иконка:"

ls -lh \
    "$APPDIR/qr-buffer.png"

echo

echo "🚀 Запуск:"

echo

printf './dist/%s\n' "$APPIMAGE_NAME"

echo
