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

import os
import shutil
import subprocess
import sys
from pathlib import Path

import httpx


def get_gui_domain() -> str:
    return f"gui/{os.getuid()}"


def launch_agents_dir() -> Path:
    return Path.home() / "Library" / "LaunchAgents"


def logs_dir() -> Path:
    return Path.home() / "Library" / "Logs" / "Transformers"


def get_plist_path(label: str) -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{label}.plist"


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


def exit_plist(label):
    plist = get_plist_path(label)
    domain = get_gui_domain()

    if plist.exists():
        run(["launchctl", "bootout", domain, str(plist)], check=False)
    else:
        run(["launchctl", "remove", label], check=False)


def resolve_transformers_exe() -> str:
    p = Path(sys.argv[0])
    if p.exists():
        return str(p.resolve())
    w = shutil.which("transformers")
    if w:
        return str(Path(w).resolve())
    return str(Path(sys.executable).resolve())


def design_plist(arguments: list[str], log_id: str, label: str) -> str:
    launch_agents_dir().mkdir(parents=True, exist_ok=True)
    logs_dir().mkdir(parents=True, exist_ok=True)

    log_file = logs_dir() / f"transformers-{log_id}.log"
    exe = resolve_transformers_exe()
    use_python_module = exe == str(Path(sys.executable).resolve())
    string_arguments = "\n".join([f"<string>{argument}</string>" for argument in arguments])

    if use_python_module:
        program_arguments = f"""
            <array>
              <string>{exe}</string>
              <string>-m</string>
              <string>transformers</string>
              <string>serve</string>
              {string_arguments}
            </array>
            """
    else:
        program_arguments = f"""
            <array>
              <string>{exe}</string>
              <string>serve</string>
              {string_arguments}
            </array>
            """

    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
      <dict>
        <key>Label</key>
        <string>{label}</string>

        <key>ProgramArguments</key>
        {program_arguments}

        <key>RunAtLoad</key>
        <true/>

        <key>KeepAlive</key>
        <true/>

        <key>ThrottleInterval</key>
        <integer>5</integer>

        <key>StandardOutPath</key>
        <string>{log_file}</string>
        <key>StandardErrorPath</key>
        <string>{log_file}</string>

        <key>EnvironmentVariables</key>
        <dict>
          <key>PYTHONUNBUFFERED</key>
          <string>1</string>
        </dict>
      </dict>
    </plist>
    """
    return plist


def is_serve_running(host: str, port: int) -> bool:
    url = f"http://{host}:{port}/health"
    try:
        response = httpx.get(url)
        return response.status_code == 200
    except Exception:
        return False


def get_serve_loaded_models(host: str, port: int) -> list[str]:
    url = f"http://{host}:{port}/status"
    try:
        response = httpx.get(url)
        return response.json().get("loaded_models")
    except Exception:
        return []


def daemon_status(label) -> dict:
    """
    Returns a small status payload you can print as text or json.
    """
    domain = get_gui_domain()
    plist = get_plist_path(label)
    loaded = False

    # launchctl print is the easiest probe; it fails if not loaded.
    cp = run(["launchctl", "print", f"{domain}/{label}"], check=False)
    if cp.returncode == 0:
        loaded = True
        details = cp.stdout
    else:
        details = (cp.stdout or "") + (cp.stderr or "")

    return {
        "label": label,
        "plist_path": str(plist),
        "plist_exists": plist.exists(),
        "loaded": loaded,
        "launchctl_print": details.strip(),
    }
