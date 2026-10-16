#!/bin/bash
# Build the signed Connect IQ store package for every device in monkey.jungle.
#
#   ./export_iq.sh              # ask how to bump the version
#   ./export_iq.sh patch        # 0.1.0 -> 0.1.1, then compile
#   ./export_iq.sh minor
#   ./export_iq.sh major
#   ./export_iq.sh 1.2.3        # set this version, then compile
#   ./export_iq.sh skip         # compile the current version
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SDK_DIR="$HOME/Library/Application Support/Garmin/ConnectIQ/Sdks"
SDK_PATH="$(ls -td "$SDK_DIR"/connectiq-sdk-mac-* 2>/dev/null | head -n 1)"
KEY_PATH="$ROOT/developer_key.der"
OUTPUT_IQ="$ROOT/bin/Fluida.iq"
MANIFEST="$ROOT/manifest.xml"

if [ -z "${SDK_PATH}" ]; then
    echo "No Connect IQ SDK found in $SDK_DIR"
    exit 1
fi

BUMP_TYPE="${1:-}"
CUSTOM_VERSION=""

if [[ "$BUMP_TYPE" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    CUSTOM_VERSION="$BUMP_TYPE"
    BUMP_TYPE="custom"
fi

if [ -z "$BUMP_TYPE" ]; then
    if [ -t 0 ]; then
        echo "Select a version bump for this store release:"
        select opt in \
            "patch (0.1.0 -> 0.1.1)" \
            "minor (0.1.0 -> 0.2.0)" \
            "major (0.1.0 -> 1.0.0)" \
            "custom (specify an exact version)" \
            "skip (keep the current version)"
        do
            case $opt in
                "patch (0.1.0 -> 0.1.1)") BUMP_TYPE="patch"; break ;;
                "minor (0.1.0 -> 0.2.0)") BUMP_TYPE="minor"; break ;;
                "major (0.1.0 -> 1.0.0)") BUMP_TYPE="major"; break ;;
                "custom (specify an exact version)") BUMP_TYPE="custom"; break ;;
                "skip (keep the current version)") BUMP_TYPE="skip"; break ;;
                *) echo "Invalid option." ;;
            esac
        done
    else
        BUMP_TYPE="patch"
    fi
fi

if [ "$BUMP_TYPE" = "custom" ] && [ -z "$CUSTOM_VERSION" ]; then
    read -r -p "Enter the version (for example 1.0.1): " CUSTOM_VERSION
fi

VERSION="$(python3 "$ROOT/tools/export_version.py" "$MANIFEST" "$BUMP_TYPE" "$CUSTOM_VERSION")"

if [ ! -f "$KEY_PATH" ]; then
    echo "Generating a local developer key..."
    openssl genrsa -out "$ROOT/developer_key.pem" 4096
    openssl pkcs8 -topk8 -inform PEM -outform DER -in "$ROOT/developer_key.pem" -out "$KEY_PATH" -nocrypt
fi

mkdir -p "$ROOT/bin"
echo "Using $SDK_PATH"
echo "Exporting Fluida $VERSION"
"$SDK_PATH/bin/monkeyc" \
    -e \
    -r \
    -O 2 \
    -w \
    -y "$KEY_PATH" \
    -f "$ROOT/monkey.jungle" \
    -o "$OUTPUT_IQ"

python3 - "$ROOT" "$VERSION" <<'PY'
import sys
from pathlib import Path

root, version = sys.argv[1], sys.argv[2]
sys.path.insert(0, str(Path(root) / "tools"))
from export_version import release_notes

notes = Path(root) / "bin" / "RELEASE_NOTES.txt"
notes.write_text(release_notes(version))
print(notes.read_text(), end="")
PY

echo "Built $OUTPUT_IQ"
echo "Release notes: $ROOT/bin/RELEASE_NOTES.txt"
