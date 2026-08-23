#!/usr/bin/env bash
set -euo pipefail

# Mi Create - Linux Distributable Build Script
# Builds Nuitka standalone distribution, portable tarball, and AppImage.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${ROOT_DIR}"

# 1. Select Python environment
if [[ -z "${PYTHON:-}" ]]; then
    if [[ -f "${ROOT_DIR}/.venv/bin/python3" ]]; then
        PYTHON="${ROOT_DIR}/.venv/bin/python3"
    elif [[ -f "${ROOT_DIR}/.venv/bin/python" ]]; then
        PYTHON="${ROOT_DIR}/.venv/bin/python"
    else
        PYTHON="python3"
    fi
fi

echo "==> Using Python: $(${PYTHON} --version) (${PYTHON})"
export PATH="$(dirname "${PYTHON}"):${PATH}"

# 2. Setup build & dist directories
BUILD_DIR="${ROOT_DIR}/build"
DIST_DIR="${ROOT_DIR}/dist"
NUITKA_OUTPUT_DIR="${BUILD_DIR}/nuitka"
APPDIR="${BUILD_DIR}/AppDir"

mkdir -p "${BUILD_DIR}" "${DIST_DIR}"

# Clean previous build artifacts
rm -rf "${NUITKA_OUTPUT_DIR}" "${APPDIR}"

echo "==> Compiling Mi Create with Nuitka..."
JOBS="${BUILD_JOBS:-$(nproc 2>/dev/null || echo 4)}"

"${PYTHON}" -m nuitka \
    --standalone \
    --lto=no \
    --jobs="${JOBS}" \
    --enable-plugin=pyqt6 \
    --include-package=PyQt6.Qsci \
    --include-data-dir="src/data=data" \
    --include-data-dir="src/themes=themes" \
    --include-data-dir="src/locales=locales" \
    --include-data-files="src/compiler/*=compiler/" \
    --include-data-dir="src/resources=resources" \
    --include-data-dir="src/plugins=plugins" \
    --output-dir="${NUITKA_OUTPUT_DIR}" \
    --output-filename=mi-create \
    --assume-yes-for-downloads \
    --remove-output \
    src/main.py

DIST_FOLDER="${NUITKA_OUTPUT_DIR}/main.dist"
if [[ ! -d "${DIST_FOLDER}" ]]; then
    echo "Error: Nuitka output directory '${DIST_FOLDER}' not found!"
    exit 1
fi

# Ensure data directories are fully copied in case Nuitka skipped any file types
mkdir -p "${DIST_FOLDER}/data" "${DIST_FOLDER}/themes" "${DIST_FOLDER}/locales" "${DIST_FOLDER}/compiler" "${DIST_FOLDER}/plugins"
cp -r src/data/* "${DIST_FOLDER}/data/" 2>/dev/null || true
cp -r src/themes/* "${DIST_FOLDER}/themes/" 2>/dev/null || true
cp -r src/locales/* "${DIST_FOLDER}/locales/" 2>/dev/null || true
cp -r src/compiler/* "${DIST_FOLDER}/compiler/" 2>/dev/null || true
cp -r src/plugins/* "${DIST_FOLDER}/plugins/" 2>/dev/null || true


# Ensure executable is named mi-create
if [[ -f "${DIST_FOLDER}/main.bin" && ! -f "${DIST_FOLDER}/mi-create" ]]; then
    mv "${DIST_FOLDER}/main.bin" "${DIST_FOLDER}/mi-create"
elif [[ -f "${DIST_FOLDER}/main" && ! -f "${DIST_FOLDER}/mi-create" ]]; then
    mv "${DIST_FOLDER}/main" "${DIST_FOLDER}/mi-create"
fi

# Ensure compiler binaries have proper permissions
chmod +x "${DIST_FOLDER}/mi-create" || true
if [[ -d "${DIST_FOLDER}/compiler" ]]; then
    chmod +x "${DIST_FOLDER}/compiler"/* || true
fi

echo "==> Creating portable tarball..."
TARBALL_PATH="${DIST_DIR}/Mi-Create-Linux-x86_64.tar.gz"
tar -czf "${TARBALL_PATH}" -C "${NUITKA_OUTPUT_DIR}" --transform 's|^main\.dist|mi-create|' main.dist
echo "--> Created: ${TARBALL_PATH}"

echo "==> Preparing AppDir for AppImage..."
mkdir -p "${APPDIR}/usr/bin"
mkdir -p "${APPDIR}/usr/share/applications"
mkdir -p "${APPDIR}/usr/share/icons/hicolor/256x256/apps"

# Copy standalone bundle into AppDir
cp -a "${DIST_FOLDER}"/* "${APPDIR}/usr/bin/"

# Copy desktop icon
cp "${ROOT_DIR}/src/resources/MiCreate.png" "${APPDIR}/usr/share/icons/hicolor/256x256/apps/mi-create.png"
cp "${ROOT_DIR}/src/resources/MiCreate.png" "${APPDIR}/mi-create.png"

# Create desktop entry
cat <<'EOF' > "${APPDIR}/mi-create.desktop"
[Desktop Entry]
Type=Application
Name=Mi Create
Comment=Unofficial watchface creator for Xiaomi Wearables
Exec=mi-create %F
Icon=mi-create
Categories=Utility;Graphics;Development;
Terminal=false
StartupNotify=true
EOF

cp "${APPDIR}/mi-create.desktop" "${APPDIR}/usr/share/applications/mi-create.desktop"

# Create AppRun script
cat <<'EOF' > "${APPDIR}/AppRun"
#!/usr/bin/env bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/bin:${LD_LIBRARY_PATH:-}"
export QT_PLUGIN_PATH="${HERE}/usr/bin/PyQt6/Qt6/plugins:${QT_PLUGIN_PATH:-}"
exec "${HERE}/usr/bin/mi-create" "$@"
EOF

chmod +x "${APPDIR}/AppRun"
chmod +x "${APPDIR}/usr/bin/mi-create"

echo "==> Building AppImage..."
APPIMAGE_PATH="${DIST_DIR}/Mi-Create-x86_64.AppImage"

# Find or download appimagetool
APPIMAGETOOL_BIN=""
if command -v appimagetool &>/dev/null; then
    APPIMAGETOOL_BIN="appimagetool"
elif [[ -f "${BUILD_DIR}/appimagetool-x86_64.AppImage" ]]; then
    APPIMAGETOOL_BIN="${BUILD_DIR}/appimagetool-x86_64.AppImage"
else
    echo "--> Downloading appimagetool..."
    curl -fsSL -o "${BUILD_DIR}/appimagetool-x86_64.AppImage" \
        https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage || true
    if [[ -f "${BUILD_DIR}/appimagetool-x86_64.AppImage" ]]; then
        chmod +x "${BUILD_DIR}/appimagetool-x86_64.AppImage"
        APPIMAGETOOL_BIN="${BUILD_DIR}/appimagetool-x86_64.AppImage"
    fi
fi

if [[ -n "${APPIMAGETOOL_BIN}" ]]; then
    export ARCH=x86_64
    # Use --appimage-extract-and-run if appimagetool is an AppImage to avoid FUSE requirement in containers/CI
    if [[ "${APPIMAGETOOL_BIN}" == *.AppImage* ]]; then
        "${APPIMAGETOOL_BIN}" --appimage-extract-and-run "${APPDIR}" "${APPIMAGE_PATH}"
    else
        "${APPIMAGETOOL_BIN}" "${APPDIR}" "${APPIMAGE_PATH}"
    fi
    chmod +x "${APPIMAGE_PATH}"
    echo "--> Created: ${APPIMAGE_PATH}"
else
    echo "Warning: appimagetool could not be run. AppDir is ready at ${APPDIR} and tarball is at ${TARBALL_PATH}."
fi

echo "==> Linux build complete!"
