#!/usr/bin/env bash
# Isolated Broadway audit; no access to the desktop session bus.
set -euo pipefail
audit_dir="${1:-${WELCOME_AUDIT_DIR:-/tmp/comm-welcome-audit}}"
mkdir -p "$audit_dir"
export WELCOME_AUDIT_DIR="$audit_dir"
gtk4-broadwayd --address 127.0.0.1 --port 8097 :7 >"$audit_dir/broadway.log" 2>&1 &
broadway_pid=$!
trap 'kill "$broadway_pid" 2>/dev/null || true' EXIT
export GDK_BACKEND=broadway BROADWAY_DISPLAY=:7 GTK_A11Y=none
export GSK_RENDERER=cairo
export GIO_USE_VFS=local GSETTINGS_BACKEND=memory ADW_DISABLE_PORTAL=1
if [[ "${2:-}" == "--actions-only" ]]; then
    timeout 30s dbus-run-session -- python3 scripts/check_actions.py >"$audit_dir/actions.log" 2>&1
else
    timeout 45s dbus-run-session -- python3 scripts/visual_check.py "${2:-}" >"$audit_dir/app.log" 2>&1
fi
