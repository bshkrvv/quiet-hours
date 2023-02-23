#! /usr/bin/env python

import argparse
import pychromecast
import time

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

excluded_names: list[str] = args.exclude if args.exclude is not None else []
browser: pychromecast.CastBrowser = None
chromecasts: set[pychromecast.Chromecast] = set()

def discover():
    print("Discovering ...")
    global browser
    browser = pychromecast.get_chromecasts(blocking = False, callback = add_chromecast)

def add_chromecast(chromecast: pychromecast.Chromecast):
    print(f"Discovered new chromecast \"{chromecast.name}\"")

    if chromecast.name in excluded_names:
        print(f"\"{chromecast.name}\" is excluded")
    else:
        chromecasts.add(chromecast)

def mute():
    for chromecast in chromecasts:
        chromecast.wait()
        mc = chromecast.media_controller

        if mc.status.player_is_playing:
            print(f"\"{chromecast.name}\" is playing \"{mc.status.title}\" on \"{chromecast.app_display_name}\"")

            if not chromecast.status.volume_muted:
                chromecast.set_volume_muted(True)
                print(f"Muted \"{chromecast.name}\"")

try:
    discover()

    while True:
        mute()
        time.sleep(5)
except KeyboardInterrupt:
    browser.stop_discovery()
