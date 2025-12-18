from fastapi import FastAPI

from .settings import Settings, SettingsPayload
from fastapi.staticfiles import StaticFiles
from importlib import resources

static_ref = resources.files("transformers_app") / "static"


def mount_static_files(app: FastAPI):
    with resources.as_file(static_ref) as static_dir:
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


__all__ = ["Settings", "SettingsPayload", "mount_static_files"]
