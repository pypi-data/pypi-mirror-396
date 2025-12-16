import dataclasses
import os
import pathlib
import platform
import tempfile
from typing import Any

import pygame

from . import logs, utils

_DEFAULT_GAME_NAME = "My Game"


@dataclasses.dataclass
class _PlatformDirSpec:
    xdg_var: str
    unix: str
    darwin: str
    # Windows uses %APPDATA% / %PROGRAMDATA% for all data
    # so this value is used as a subdirectory name
    windows: str
    subdirectory: str = "pygame"


__CACHE = _PlatformDirSpec(
    xdg_var="XDG_CACHE_HOME", unix=".cache", darwin="Caches", windows=".cache"
)
# XXX: consider using a .plist file for MacOS?
__CONFIG = _PlatformDirSpec(
    xdg_var="XDG_CONFIG_HOME", unix=".config", darwin="Preferences", windows="config"
)
__DATA = _PlatformDirSpec(
    xdg_var="XDG_DATA_HOME", unix=".local/share", darwin="", windows="data"
)


def _get_local_dir(
    dir_spec: _PlatformDirSpec, game_dir: str
) -> pathlib.PurePath | None:
    local_dir = os.environ.get(dir_spec.xdg_var)
    subdirectory = pathlib.PurePath(dir_spec.subdirectory) / game_dir

    match platform.system():
        case "Windows":
            local_dir = os.environ.get("APPDATA") or os.environ.get("PROGRAMDATA")
            subdirectory /= dir_spec.windows
        case "Darwin":
            # if XDG_*_HOME is unset, fall back to Library default on MacOS
            if local_dir is None:
                local_dir = pathlib.Path.home() / "Library" / dir_spec.darwin
        case _:
            local_dir = pathlib.Path.home() / dir_spec.unix

    if local_dir is None:
        return None

    local_dir = pathlib.Path(local_dir) / subdirectory
    if not local_dir.exists():
        try:
            local_dir.mkdir(parents=True)
        except OSError:
            print("Failed to find or create configuration directory; using defaults")
            return None

    return local_dir


# values set by module init() method
@dataclasses.dataclass
class _GameLocal:
    name: str = _DEFAULT_GAME_NAME

    resource_dir: pathlib.PurePath = pathlib.PurePath()

    # if a local directory can't be found or created, the
    # value will be None and only defaults will be used
    cache_dir: pathlib.PurePath | None = None
    config_dir: pathlib.PurePath | None = None
    data_dir: pathlib.PurePath | None = None

    initialized: bool = False

    def __getattribute__(self, name: str) -> Any:
        # XXX: this is pretty awful; probably better to implement
        # this with properties instead
        initialized = super().__getattribute__("initialized")
        if name == "initialized":
            return initialized
        if not initialized:
            raise pygame.error(
                "Using dps.core extension, but core.init() was never called!"
            )
        return super().__getattribute__(name)


GAME = _GameLocal()


# XXX: pretty janky approach - probably better ways to implement this
def init(resource_dir: str | pathlib.PurePath, game_name: str = _DEFAULT_GAME_NAME):
    pygame.init()

    if GAME.initialized:
        return

    game_dir_name = game_name.lower().replace(" ", "_")
    resource_dir = utils.normalize_path_str(resource_dir)

    GAME.name = game_name
    GAME.resource_dir = resource_dir
    GAME.cache_dir = _get_local_dir(__CACHE, game_dir_name)
    GAME.config_dir = _get_local_dir(__CONFIG, game_dir_name)
    data_dir = _get_local_dir(__DATA, game_dir_name)
    GAME.data_dir = data_dir
    log_dir = data_dir or pathlib.PurePath(tempfile.gettempdir())
    logs.setup_game_logger(log_dir / "game.log", game_dir_name)
    GAME.initialized = True
