#!/usr/bin/env python3
"""Check live and autostart policy before importing GTK."""

import argparse
import sys

from comm_welcome.environment import eligible, is_live
from comm_welcome.preferences import Preferences


def main() -> int:
    parser = argparse.ArgumentParser(description="BigCommunity Welcome")
    parser.add_argument("--autostart", action="store_true")
    args = parser.parse_args()
    if is_live():
        return 0
    if args.autostart and (not eligible() or Preferences().suppressed()):
        return 0
    from comm_welcome.application import WelcomeApplication

    return WelcomeApplication().run([sys.argv[0]])


if __name__ == "__main__":
    raise SystemExit(main())
