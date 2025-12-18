# Copyright 2025 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import sys
from pathlib import Path
from typing import Optional

import webbrowser
from AppKit import (
    NSApplication,
    NSImage,
    NSMenu,
    NSMenuItem,
    NSSelectorFromString,
    NSSize,
    NSStatusBar,
    NSVariableStatusItemLength,
)
from Foundation import NSObject, NSTimer
from importlib import resources


from ..utils import design_plist, exit_plist, get_gui_domain, get_plist_path, get_serve_loaded_models, run


FAVICON = str(resources.files("transformers_app") / "static" / "favicon.png")
SERVE_LABEL = "org.huggingface.transformers.serve"
TRAY_LABEL = "org.huggingface.transformers.tray"

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8000


def set_status_icon(button, png_path: str):
    img = NSImage.alloc().initWithContentsOfFile_(png_path)
    if img is None:
        raise FileNotFoundError(png_path)

    # Makes it render correctly in light/dark mode (expects a monochrome-ish icon)
    img.setTemplate_(True)
    img.setSize_(NSSize(18, 18))

    button.setImage_(img)
    # Optional: remove text
    button.setTitle_("")


def write_plist(host: str, port: int) -> Path:
    plist = design_plist(["--tray", "--host", host, "--port", str(port)], log_id="tray", label=TRAY_LABEL)
    p = get_plist_path(TRAY_LABEL)
    p.write_text(plist)
    return p


def tray_install(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    plist = write_plist(host=host, port=port)
    domain = get_gui_domain()

    # idempotency: unload first if already loaded
    run(["launchctl", "bootout", domain, str(plist)], check=False)
    run(["launchctl", "bootstrap", domain, str(plist)], check=True)
    run(["launchctl", "enable", f"{domain}/{TRAY_LABEL}"], check=False)


def tray_stop() -> None:
    exit_plist(TRAY_LABEL)


class TrayApp(NSObject):
    def initWithHost_port_(self, host: str, port: int):
        if self is None:
            return None

        self.host = host
        self.port = port

        return self

    def applicationDidFinishLaunching_(self, notification):
        self.statusItem = NSStatusBar.systemStatusBar().statusItemWithLength_(NSVariableStatusItemLength)
        self.button = self.statusItem.button()
        set_status_icon(self.button, FAVICON)

        self.model_loaded = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("No model loaded.", "noop:", "")

        self.settings_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Settings…", None, "")
        self.settings_item.setTarget_(self)
        self.settings_item.setAction_(NSSelectorFromString("openSettings:"))

        self.stop_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Stop server", None, "")
        self.stop_item.setTarget_(self)
        self.stop_item.setAction_(NSSelectorFromString("stopServer:"))

        self.menu = NSMenu.alloc().init()
        self.menu.addItem_(self.model_loaded)
        self.menu.insertItem_atIndex_(self.settings_item, 1)  # or addItem_
        self.menu.addItem_(NSMenuItem.separatorItem())
        self.menu.addItem_(self.stop_item)

        self.statusItem.setMenu_(self.menu)

        self.timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.5, self, "refreshStatus:", None, True
        )
        self.refreshStatus_(None)

    def noop_(self, _):
        # A noop on which we link the "model_loaded" action so that it's not greyed-out.
        return

    def openSettings_(self, sender):
        url = f"http://{self.host}:{self.port}/settings"
        webbrowser.open(url, new=1, autoraise=True)

    def refreshStatus_(self, _):
        loaded_models = get_serve_loaded_models(self.host, self.port)
        if not len(loaded_models):
            self.model_loaded.setTitle_("No model loaded.")
        else:
            if len(loaded_models) == 1:
                self.model_loaded.setTitle_(f"Model loaded: {loaded_models[0]}")
            else:
                line_return = " - "
                self.model_loaded.setTitle_(f"Models loaded: {line_return.join(loaded_models)}")

    def stopServer_(self, _):
        exit_plist(SERVE_LABEL)
        exit_plist(TRAY_LABEL)
        NSApplication.sharedApplication().terminate_(None)


def tray_start(argv: Optional[list[str]] = None) -> None:
    if sys.platform != "darwin":
        raise SystemExit("Tray is supported only on macOS for now.")

    p = argparse.ArgumentParser(prog="transformers tray")
    p.add_argument("--host", default=DEFAULT_HOST)
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = p.parse_args(argv)

    app = NSApplication.sharedApplication()
    delegate = TrayApp.alloc().initWithHost_port_(args.host, args.port)
    app.setDelegate_(delegate)
    app.run()
