#!/bin/bash
# Compile Fluida and open it in the simulator.
#   ./build.sh enduro4
#   ./build.sh sim enduro4
set -euo pipefail

LAUNCH=1
if [ "${1:-}" = "sim" ]; then
    DEVICE="${2:-fenix7}"
elif [ "${1:-}" = "--no-sim" ]; then
    LAUNCH=0
    DEVICE="${2:-fenix7}"
else
    DEVICE="${1:-fenix7}"
fi
ROOT="$(cd "$(dirname "$0")" && pwd)"
SDK_DIR="$HOME/Library/Application Support/Garmin/ConnectIQ/Sdks"
SDK_PATH="$(ls -td "$SDK_DIR"/connectiq-sdk-mac-* 2>/dev/null | head -n 1)"

if [ -z "${SDK_PATH}" ]; then
    echo "No Connect IQ SDK found in $SDK_DIR"
    exit 1
fi

if [ ! -f "$ROOT/developer_key.der" ]; then
    echo "Generating a local developer key..."
    openssl genrsa -out "$ROOT/developer_key.pem" 4096
    openssl pkcs8 -topk8 -inform PEM -outform DER -in "$ROOT/developer_key.pem" -out "$ROOT/developer_key.der" -nocrypt
fi

mkdir -p "$ROOT/bin"
echo "Using $SDK_PATH"
echo "Building Fluida for $DEVICE..."
"$SDK_PATH/bin/monkeyc" \
    -d "$DEVICE" \
    -f "$ROOT/monkey.jungle" \
    -o "$ROOT/bin/Fluida.prg" \
    -y "$ROOT/developer_key.der" \
    -w
echo "Built $ROOT/bin/Fluida.prg"

# Same simulator settings folder Lunara uses. The compiler writes
# bin/Fluida-settings.json; the simulator reads FLUIDA.JSON and FLUIDA.SET.
SIM_SETTINGS="$TMPDIR/com.garmin.connectiq/GARMIN/APPS/SETTINGS"
mkdir -p "$SIM_SETTINGS"
cp "$ROOT/bin/Fluida-settings.json" "$SIM_SETTINGS/FLUIDA.SET"
cp "$ROOT/bin/Fluida-settings.json" "$SIM_SETTINGS/FLUIDA.JSON"
echo "Installed simulator settings in $SIM_SETTINGS"

if [ "$LAUNCH" -eq 0 ]; then
    exit 0
fi

simulator_is_running() {
    pgrep -f "ConnectIQ.app/Contents/MacOS/simulator" >/dev/null 2>&1
}

if ! simulator_is_running; then
    echo "Starting Connect IQ Simulator..."
    "$SDK_PATH/bin/connectiq" >/tmp/fluida-connectiq.log 2>&1
    tries=0
    while ! simulator_is_running; do
        tries=$((tries + 1))
        if [ "$tries" -gt 30 ]; then
            echo "Connect IQ Simulator did not start. See /tmp/fluida-connectiq.log"
            exit 1
        fi
        sleep 1
    done
    sleep 3
fi

echo "Launching $DEVICE..."
"$SDK_PATH/bin/monkeydo" "$ROOT/bin/Fluida.prg" "$DEVICE"
