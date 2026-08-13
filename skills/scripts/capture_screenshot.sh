#!/usr/bin/env bash
# Portable rendered-screenshot fallback for GameCraft-style Godot projects.
# Adapted from GameCraft-Bench tools/screenshot.sh:
# https://github.com/FreedomIntelligence/gamecraft-bench
# Licensed under Apache-2.0.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CAPTURE_GD="${SCRIPT_DIR}/capture_screenshot.gd"

project_path=""
forward_args=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --path)
            [[ $# -ge 2 ]] || { echo "--path requires a value" >&2; exit 2; }
            project_path="$2"
            shift 2
            ;;
        --path=*)
            project_path="${1#--path=}"
            shift
            ;;
        --)
            shift
            forward_args+=("$@")
            break
            ;;
        *)
            forward_args+=("$1")
            shift
            ;;
    esac
done

if [[ -z "$project_path" ]]; then
    echo "capture_screenshot.sh: --path <project> is required" >&2
    exit 2
fi
if [[ ! -f "$project_path/project.godot" ]]; then
    echo "capture_screenshot.sh: project.godot not found under $project_path" >&2
    exit 2
fi
for tool in godot Xvfb; do
    command -v "$tool" >/dev/null 2>&1 || {
        echo "capture_screenshot.sh: required command not found: $tool" >&2
        exit 3
    }
done

free_display() {
    local bound
    bound="$(awk '$NF ~ /^@\/tmp\/\.X11-unix\/X[0-9]+$/ {
        sub(/.*X/, "", $NF); print $NF
    }' /proc/net/unix 2>/dev/null | sort -n || true)"
    local number
    for number in $(seq 99 250); do
        if ! grep -qx "$number" <<<"$bound" && [[ ! -e "/tmp/.X11-unix/X${number}" ]]; then
            echo "$number"
            return 0
        fi
    done
    return 1
}

display_number="$(free_display)" || {
    echo "capture_screenshot.sh: no free X display in :99..:250" >&2
    exit 3
}
export DISPLAY=":${display_number}"

Xvfb "$DISPLAY" -screen 0 1280x720x24 -nolisten tcp >/dev/null 2>&1 &
xvfb_pid=$!
cleanup() {
    kill "$xvfb_pid" 2>/dev/null || true
    wait "$xvfb_pid" 2>/dev/null || true
}
trap cleanup EXIT

for _attempt in $(seq 1 60); do
    [[ -e "/tmp/.X11-unix/X${display_number}" ]] && break
    kill -0 "$xvfb_pid" 2>/dev/null || {
        echo "capture_screenshot.sh: Xvfb exited before creating $DISPLAY" >&2
        exit 3
    }
    sleep 0.05
done
[[ -e "/tmp/.X11-unix/X${display_number}" ]] || {
    echo "capture_screenshot.sh: Xvfb did not become ready" >&2
    exit 3
}

godot \
    --path "$project_path" \
    --display-driver x11 \
    --rendering-driver opengl3 \
    --audio-driver Dummy \
    --resolution 1280x720 \
    --script "$CAPTURE_GD" \
    -- "${forward_args[@]}"
