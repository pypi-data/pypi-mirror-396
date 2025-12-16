import dataclasses
import itertools
from typing import Any, Dict, List, Type

import pygame

from . import scenes, text


@dataclasses.dataclass(frozen=True)
class DiagnosticsSettings(text.TextOptions):
    margins: text.Margins = dataclasses.field(default_factory=text.Margins)


class Diagnostics(scenes.Overlay):

    settings_type: Type[DiagnosticsSettings] = DiagnosticsSettings

    def __init__(self, settings: DiagnosticsSettings, screen: pygame.Surface):
        super().__init__(screen)
        self.diagnostics: Dict[str, Any] = {}
        self.settings = settings
        self.rect = self.screen.get_rect()
        if self.settings.margins:
            self.rect = self.settings.margins.apply(self.rect)
        self.draw_group = pygame.sprite.LayeredUpdates()

    def add(self, name: str, value: Any):
        self.diagnostics[name] = value

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_F12, pygame.K_ESCAPE):
                scenes.end_current_scene()
                return
        super().handle_event(event)

    def update(self, dt: float):
        super().update(dt)
        self.draw_group.empty()
        self._create_diag_sprites()
        self.draw_group.update()

    def _create_diag_sprites(self):
        diag_strings = "\n".join([f"{k}: {v}" for k, v in self.diagnostics.items()])
        lines_per_block = self.rect.h // self.settings.font.get_linesize()
        text_cols = itertools.batched(diag_strings, lines_per_block)

        x, y = self.rect.topleft

        for col in text_cols:
            col_rect = pygame.Rect(x, y, self.rect.w - x, self.rect.h)
            diags = text.multiline_text("\n".join(col), self.settings, col_rect)
            x += max(*diags, key=lambda d: d.rect.w).rect.w
            self.draw_group.add(*diags)

    def draw(self) -> List[pygame.Rect]:
        return super().draw() + self.draw_group.draw(self.screen)

    def dirty_all_sprites(self):
        super().dirty_all_sprites()
