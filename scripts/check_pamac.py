#!/usr/bin/env python3
"""Inspect and discard a browser plan. Never call ApplyTransaction."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "usr/share/comm-welcome"))
os.environ["GIO_USE_VFS"] = "local"
os.environ["ADW_DISABLE_PORTAL"] = "1"

from comm_welcome.gtk import Gio, GLib  # noqa: E402
from comm_welcome.install_policy import validate_plan  # noqa: E402
from comm_welcome.installer import BUS_NAME, BUS_PATH, INTERFACE, repository_browsers  # noqa: E402

reference = repository_browsers().get("vivaldi")
if reference is None:
    raise SystemExit("Vivaldi is unavailable in the configured repositories")
connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)
request = GLib.Variant("(a{sv})", ({"install": GLib.Variant("as", [reference])},))
result = connection.call_sync(
    BUS_NAME,
    BUS_PATH,
    INTERFACE,
    "PrepareTransaction",
    request,
    None,
    Gio.DBusCallFlags.NONE,
    30000,
    None,
)
tx_id, plan = result.unpack()
try:
    for _round in range(20):
        if not plan.get("preparation_interactions"):
            break
        interaction = plan["preparation_interactions"][0]
        if interaction.get("kind") != "optdep-choose":
            break
        response = {"selected": GLib.Variant("as", [])}
        result = connection.call_sync(
            BUS_NAME,
            BUS_PATH,
            INTERFACE,
            "ResolvePreparation",
            GLib.Variant("(ssa{sv})", (tx_id, interaction["request_id"], response)),
            None,
            Gio.DBusCallFlags.NONE,
            30000,
            None,
        )
        plan = result.unpack()[0]
    print(json.dumps(plan, indent=2))
    print(f"accepted_by_welcome={validate_plan(plan, reference)}")
finally:
    connection.call_sync(
        BUS_NAME,
        BUS_PATH,
        INTERFACE,
        "CancelTransaction",
        GLib.Variant("(s)", (tx_id,)),
        None,
        Gio.DBusCallFlags.NONE,
        10000,
        None,
    )
    print("Preview discarded; no packages installed.")
