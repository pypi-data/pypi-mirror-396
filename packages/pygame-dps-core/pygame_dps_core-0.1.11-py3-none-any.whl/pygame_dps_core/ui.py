import dataclasses
from typing import Callable, List

import pygame
from pygame.sprite import LayeredDirty

from . import scenes, sprites, types
from .text import TextOptions, text_sprite


@dataclasses.dataclass(frozen=True)
class ButtonOptions(sprites.SpriteOptions):
    text: str = ""
    hover_color: types.ColorValue = ""
    text_opts: TextOptions | None = None


class Button(sprites.GameSprite):
    """Clickable image or text button

    Args:
        opts (ButtonOptions): configuration options for the button
        on_click (Callable): on-click callback
    """

    _hovered: bool = False

    def __init__(self, opts: ButtonOptions, on_click: Callable):
        super().__init__(opts)
        self.text = opts.text
        self.text_opts = opts.text_opts
        if self.text_opts is not None:
            self.hover_opts = dataclasses.replace(
                self.text_opts, color=opts.hover_color
            )
        self.on_click = on_click

    @property
    def hovered(self):
        return self._hovered

    @hovered.setter
    def hovered(self, hovered):
        # only dirty the sprite if we're changing state
        if self._hovered is not hovered:
            self.dirty = 1
        self._hovered = hovered

    def update(self):
        if self.text and self.text_opts is not None:
            opts = self.hover_opts if self.hovered else self.text_opts
            sprite = text_sprite(self.text, opts, self.rect.move(0, 0))
            self.image.blit(sprite.image, sprite.rect)


class Menu(scenes.Scene):
    """Base class for in-game menus

    Args:
        screen (pygame.Surface): draw surface for rendering the menu
    """

    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        # need https://github.com/pygame/pygame/pull/4635 to be merged
        # to get rid of the pylance type assignment error here
        self.buttons: LayeredDirty[Button] = LayeredDirty()  # type: ignore

    def _on_enter(self):
        self.dirty_all_sprites()
        return super()._on_enter()

    def handle_event(self, event: pygame.event.Event):
        # XXX: should this be button up/click instead of down?
        # best would be to catch buttondown and then trigger on
        # buttonup if mouse is inside button rect, as this is
        # normal behaviour for buttons in most applications
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            for button in self.buttons:
                if button.rect.collidepoint(event.pos):
                    button.on_click()
        elif event.type == pygame.MOUSEMOTION:
            for button in self.buttons:
                button.hovered = button.rect.collidepoint(event.pos)

    def update(self, dt: float):
        self.buttons.update()

    def draw(self) -> List[pygame.Rect]:
        return self.buttons.draw(self.screen)

    def dirty_all_sprites(self):
        for btn in self.buttons:
            if btn.visible:
                btn.dirty = 1
