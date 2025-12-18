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

from pathlib import Path

from ..tray import tray_install, tray_stop
from ..utils import (
    daemon_status,
    design_plist,
    exit_plist,
    get_gui_domain,
    get_plist_path,
    is_serve_running,
    logs_dir,
    run,
)


SERVE_LABEL = "org.huggingface.transformers.serve"


def write_plist(host: str, port: int) -> Path:
    plist = design_plist(["--host", host, "--port", str(port)], log_id="serve", label=SERVE_LABEL)
    p = get_plist_path(SERVE_LABEL)
    p.write_text(plist)
    return p


def daemon_install_and_start(host: str = "localhost", port: int = 8000) -> None:
    daemon_running = daemon_status(SERVE_LABEL)["loaded"]
    if daemon_running:
        print("Daemon is already running.")
        return

    if is_serve_running(host, port):
        print(
            f"Transformers serve is already running on http://{host}:{port} outside of daemon. \n\nPlease either "
            "kill the running transformers serve instance or launch the daemon on a separate port."
        )
        return

    print("Installing and starting daemon...")
    plist = write_plist(host=host, port=port)
    domain = get_gui_domain()

    # Avoid "already bootstrapped" by booting out first if present.
    run(["launchctl", "bootout", domain, str(plist)], check=False)

    run(["launchctl", "bootstrap", domain, str(plist)], check=True)
    run(["launchctl", "enable", f"{domain}/{SERVE_LABEL}"], check=False)
    run(["launchctl", "kickstart", "-k", f"{domain}/{SERVE_LABEL}"], check=True)

    print(f"Transformers Serve daemon started on http://{host}:{port}")

    tray_install(host=host, port=port)


def daemon_stop() -> None:
    daemon_running = daemon_status(SERVE_LABEL).get("loaded", False)

    if daemon_running:
        exit_plist(SERVE_LABEL)
        print("Daemon stopped.")
    else:
        print("Daemon already stopped.")

    tray_stop()


def daemon_uninstall(delete_logs: bool = False) -> None:
    daemon_stop()

    plist = get_plist_path(SERVE_LABEL)
    if plist.exists():
        plist.unlink()

    if delete_logs:
        # optional: only delete our file, not the whole dir
        log_file = logs_dir() / "transformers-serve.log"
        if log_file.exists():
            log_file.unlink()

    print("Daemon uninstalled.")
