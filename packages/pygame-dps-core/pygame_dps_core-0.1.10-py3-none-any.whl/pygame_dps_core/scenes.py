import abc
from collections import deque
from typing import List

import pygame

from . import io


class Scene(io.Loadable, abc.ABC):
    """Defines methods for game scenes

    Args:
        screen (pygame.Surface): draw surface for rendering the scene
    """

    def __init__(self, screen: pygame.Surface):
        super().__init__()
        self.screen = screen
        # setup default background as just a black screen
        self.background = pygame.Surface(screen.get_size())

    def _on_enter(self):
        # draw to the screen once when the scene is loaded
        # FIXME: need a way to set background coords
        self.screen.blit(self.background, (0, 0))
        pygame.display.update()

    @abc.abstractmethod
    def draw(self) -> List[pygame.Rect]:
        pass

    @abc.abstractmethod
    def handle_event(self, event: pygame.event.Event):
        pass

    @abc.abstractmethod
    def update(self, dt: float):
        pass

    @abc.abstractmethod
    def dirty_all_sprites(self):
        pass

    def reset(self):
        # dirty sprites after update so they are
        # updated when we re-enter the scene
        self.dirty_all_sprites()


class Overlay(Scene):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self._active_scene: Scene

    def _on_enter(self):
        self._active_scene = get_active_scene()

    def handle_event(self, event: pygame.event.Event):
        self._active_scene.handle_event(event)

    def update(self, dt: float):
        self._active_scene.update(dt)

    def draw(self) -> List[pygame.Rect]:
        return self._active_scene.draw()

    def dirty_all_sprites(self):
        pass


__scenes: deque[Scene] = deque()


def get_active_scene() -> Scene:
    """Returns the currently active scene"""
    if not __scenes:
        raise pygame.error("No active scene!")
    return __scenes[0]


def new_scene(scene: Scene):
    """Starts a new scene as the active scene"""
    scene._on_enter()
    __scenes.appendleft(scene)


def end_current_scene() -> Scene:
    """Ends the currently active scene and returns the next in the stack"""
    ending_scene = __scenes.popleft()
    ending_scene.reset()
    active_scene = get_active_scene()
    active_scene._on_enter()
    return active_scene


__all__ = [
    "Scene",
    "get_active_scene",
    "new_scene",
    "end_current_scene",
]
