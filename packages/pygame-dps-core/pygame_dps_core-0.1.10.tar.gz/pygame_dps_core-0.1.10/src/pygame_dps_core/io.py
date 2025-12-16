import dataclasses
import enum
import pathlib
from inspect import isclass
from types import UnionType
from typing import Any, Protocol, Type, TypeVar, Union, get_args, get_origin

import pygame
import yaml

from . import _conf, utils
from .logs import logger

ConfigurableT_co = TypeVar("ConfigurableT_co", bound="Configurable")


# XXX: this whole module uses a lot of reflection magic
@dataclasses.dataclass(frozen=True)
class Configurable:
    """Dataclass mixin to mark config objects as configurable from settings"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def from_config(cls: Type[ConfigurableT_co], data: dict) -> ConfigurableT_co:
        data = data or {}
        params = {}

        for field in dataclasses.fields(cls):
            if field.name in data:
                value = data[field.name]
                params[field.name] = cls._unmarshal_field(field.type, value)

        return cls(**params)

    @staticmethod
    def _unmarshal_field(type_, value) -> Any:
        if value is None:
            return None

        if isinstance(value, Configurable):
            # if the value is already a Configurable type
            # instance, no need to continue
            return value
        elif get_origin(type_) in (Union, UnionType):
            for t in get_args(type_):
                if isclass(t):
                    o = Configurable._unmarshal_class(t, value)
                    if o is not None:
                        return o
        elif isclass(type_):
            instance = Configurable._unmarshal_class(type_, value)
            if instance is not None:
                return instance

        # if the value is a list, expect the field type to be List[T]
        if isinstance(value, list) and hasattr(type_, "__args__"):
            type_ = type_.__args__[0]
            return list(Configurable._unmarshal_field(type_, o) for o in value)
        # similarly, expect dict values to be typed Dict[K, T]
        elif isinstance(value, dict):
            if hasattr(type_, "__args__") and len(type_.__args__) == 2:
                return {
                    k: Configurable._unmarshal_field(type_.__args__[1], v)
                    for k, v in value.items()
                }
        return value

    @staticmethod
    def _unmarshal_class(type_: type, value: Any) -> Any:
        # decode logic for special case clases
        # TODO: validation for values + error handling
        if issubclass(type_, enum.Enum):
            return type_(value)
        elif issubclass(type_, Configurable):
            return type_.from_config(value)
        elif type_ is pygame.font.Font:
            if isinstance(value, str):
                filename, size = value.replace(" ", "").split(",")
                file = utils.normalize_path_str(_conf.GAME.resource_dir / filename)
                return pygame.font.Font(file, int(size))
            return pygame.font.SysFont(**value)
        elif type_ is pygame.Surface:
            img_path = utils.normalize_path_str(_conf.GAME.resource_dir / value)
            img = pygame.image.load(img_path)
            # return a version of the image optimized
            # for blit with pixel alphas preserved
            return img.convert_alpha()
        elif type_ is pygame.Rect:
            return pygame.Rect(*value)
        return None


# pyright (and thus pylance) has a strict approach to abstract property types,
# (see discussion in https://github.com/microsoft/pyright/issues/2678)
# so instead of making Loadable an ABC with abstract properties, define a
# generic Protocol that Loadable subclasses must adhere to
class SupportsLoad(Protocol[ConfigurableT_co]):
    settings_file: str | pathlib.PurePath
    settings_type: Type[ConfigurableT_co]

    def __init__(self, settings: ConfigurableT_co, *args, **kwargs) -> None: ...

    @classmethod
    def instance(cls: "Type[LoadableT]", *args, **kwargs) -> "LoadableT": ...

    @classmethod
    def _load_settings(cls, file: str | None) -> ConfigurableT_co: ...


# define a type where upper bound is a SupportsLoad subtype (eg. Game) that
# expects a concrete Configurable subtype (eg. GameSettings) to reference below
LoadableT = TypeVar("LoadableT", bound=SupportsLoad[Configurable])


class Loadable:
    """Mixin to mark scenes as loadable from YAML"""

    __loaded = {}

    # needed for mixin as otherwise we may have super() conflicts with
    # subclasses that also inherit from another parent
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def instance(cls: Type[LoadableT], *args, **kwargs) -> LoadableT:
        settings_file = kwargs.pop("settings_file", None)
        settings = kwargs.get("settings") or cls._load_settings(file=settings_file)
        return cls(*args, **kwargs, settings=settings)

    @classmethod
    def load(cls: Type[LoadableT], *args, **kwargs) -> LoadableT:
        """Loads referencing class from settings file

        Passes given arguments to the class constructor.
        Caches classes and files so they are only loaded once.

        If a settings keyword argument is provided, creates an instance with
        the given values, otherwise loads values from defined settings_file.
        """
        if cls.__name__ in Loadable.__loaded:
            return Loadable.__loaded[cls.__name__]

        o = cls.instance(*args, **kwargs)
        Loadable.__loaded[cls.__name__] = o
        return o

    @classmethod
    def _load_settings(cls: Type[LoadableT], file: str | None = None) -> Configurable:
        settings_file = file if file else cls.settings_file
        filepath = utils.normalize_path_str(_conf.GAME.resource_dir / settings_file)
        filename = pathlib.PurePath(filepath).name
        # cache the settings file - useful for future objects that
        # may load multiple instances from the same settings
        if filepath in Loadable.__loaded:
            return Loadable.__loaded[filepath]

        user_settings = {}
        try:
            if _conf.GAME.config_dir is not None:
                path = utils.normalize_path_str(_conf.GAME.config_dir / settings_file)
                with open(path) as f:
                    user_settings: dict = yaml.safe_load(f)
        except OSError:
            logger.debug("No saved user settings file found: %s", filename)
        except Exception as e:
            logger.error("Error reading user settings at %s: %s", filename, e)

        try:
            with open(filepath) as f:
                settings: dict = yaml.safe_load(f)
                settings.update(user_settings)
                Loadable.__loaded[filepath] = settings
                return cls.settings_type.from_config(settings)
        except yaml.YAMLError as e:
            logger.error("Failed to read YAML from %s: %s", filepath, e)
        except (OSError, IOError) as e:
            logger.error("Error reading %s: %s", filepath, e)

        raise pygame.error(f"Failed to read configuration from {filepath}")

    @staticmethod
    def save_all():
        if _conf.GAME.config_dir is not None:
            for filepath in Loadable.__loaded.keys():
                Loadable._save(filepath)

    def save(self: SupportsLoad[Configurable]):
        Loadable._save(self.settings_file)

    @staticmethod
    def _save(filepath):
        if _conf.GAME.config_dir is None:
            return

        filepath = utils.normalize_path_str(_conf.GAME.config_dir / filepath)

        try:
            settings = Loadable.__loaded[filepath]
            with open(filepath, "w") as f:
                yaml.safe_dump(settings, f)
        except KeyError:
            logger.error("%s not found in loaded file cache", filepath)
        except yaml.YAMLError as e:
            logger.error("Failed to read YAML from %s: %s", filepath, e)
        except (OSError, IOError) as e:
            logger.error("Error reading %s: %s", filepath, e)
