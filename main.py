#! /usr/bin/env python

import argparse
import pychromecast
import time


class QuietHours:
    included: list[str]
    excluded: list[str]
    browser: pychromecast.CastBrowser
    casts: set[pychromecast.Chromecast] = set()

    def __init__(self, args):
        self.included = args.include if args.include is not None else []
        self.excluded = args.exclude if args.exclude is not None else []

    def discover(self):
        print("Discovering ...")
        self.browser = pychromecast.get_chromecasts(blocking = False, callback = self.add_cast)

    def stop_discovery(self):
        self.browser.stop_discovery()
        print("Stopped discovery")

    def add_cast(self, cast: pychromecast.Chromecast):
        def add():
            self.casts.add(cast)
            print(f"Added \"{cast.name}\" (uuid={cast.uuid}) to the list")

        print(f"Discovered new device \"{cast.name}\" (uuid={cast.uuid})")

        if len(self.included):
            if cast.name in self.included or str(cast.uuid) in self.included:
                add()
            else:
                print(f"\"{cast.name}\" (uuid={cast.uuid}) is not included")
        elif len(self.excluded):
            if cast.name not in self.excluded and str(cast.uuid) not in self.excluded:
                add()
            else:
                print(f"\"{cast.name}\" (uuid={cast.uuid}) is excluded")
        else:
            add()

    def mute(self):
        for cast in self.casts:
            print(f"Waiting for \"{cast.name}\" (uuid={cast.uuid}) to become ready")
            cast.wait()
            mc = cast.media_controller

            if mc.status.player_is_playing:
                print(f"\"{cast.name}\" (uuid={cast.uuid}) is playing \"{mc.status.title}\" on \"{cast.app_display_name}\"")

                if not cast.status.volume_muted:
                    cast.set_volume_muted(True)
                    print(f"Muted \"{cast.name}\" (uuid={cast.uuid})")


parser = argparse.ArgumentParser(
    prog = "Quiet Hours",
    description = "Mute Chromecast devices"
)

group = parser.add_mutually_exclusive_group()

group.add_argument(
    "-i",
    "--include",
    action = "extend",
    nargs = "+",
    type = str,
    metavar = "DEVICE",
    help = "list of devices to include"
)

group.add_argument(
    "-e",
    "--exclude",
    action = "extend",
    nargs = "+",
    type = str,
    metavar = "DEVICE",
    help = "list of devices to exclude"
)

args = parser.parse_args()

try:
    qh = QuietHours(args)
    qh.discover()

    while True:
        qh.mute()
        time.sleep(5)

except KeyboardInterrupt:
    qh.stop_discovery()
