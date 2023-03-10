#! /usr/bin/env python

import argparse
import pychromecast
import time


class QuietHours:
    excluded: list[str]
    browser: pychromecast.CastBrowser
    casts: set[pychromecast.Chromecast] = set()

    def __init__(self, args):
        self.excluded = args.exclude if args.exclude is not None else []

    def discover(self):
        print("Discovering ...")
        self.browser = pychromecast.get_chromecasts(blocking = False, callback = self.add_cast)

    def stop_discovery(self):
        self.browser.stop_discovery()
        print("Stopped discovery")

    def add_cast(self, cast: pychromecast.Chromecast):
        print(f"Discovered new device \"{cast.name}\"")

        if cast.name in self.excluded:
            print(f"\"{cast.name}\" is excluded")
        else:
            self.casts.add(cast)

    def mute(self):
        for cast in self.casts:
            print(f"Waiting for \"{cast.name}\" to become ready")
            cast.wait()
            mc = cast.media_controller

            if mc.status.player_is_playing:
                print(f"\"{cast.name}\" is playing \"{mc.status.title}\" on \"{cast.app_display_name}\"")

                if not cast.status.volume_muted:
                    cast.set_volume_muted(True)
                    print(f"Muted \"{cast.name}\"")


parser = argparse.ArgumentParser(
    prog = "Quiet Hours",
    description = "Mute Chromecast devices"
)

parser.add_argument(
    "-e",
    "--exclude",
    action = "extend",
    nargs = "+",
    type = str,
    metavar = "NAME",
    help = "list of device names to be excluded"
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
