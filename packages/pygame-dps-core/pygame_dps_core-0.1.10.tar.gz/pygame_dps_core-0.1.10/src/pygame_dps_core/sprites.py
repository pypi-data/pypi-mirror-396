import dataclasses

import pygame

from . import io, types


@dataclasses.dataclass(frozen=True)
class SpriteOptions(io.Configurable):
    topleft: types.Coordinate = (0, 0)
    width: float = 0
    height: float = 0
    image: pygame.Surface | None = None
    layer: int = 0


class GameSprite(pygame.sprite.WeakDirtySprite):

    def __init__(self, opts: SpriteOptions):
        super().__init__()
        self._layer = opts.layer
        self.origin = opts.topleft
        image_size = (opts.width, opts.height)
        self.image = opts.image if opts.image else pygame.Surface(image_size)

        # source image from its bounding rect
        # (inner rect at first non-transparent pixels)
        self.source_rect = self.image.get_bounding_rect()
        self.rect = self.image.get_rect()
        self.rect.update(self.origin, self.source_rect.size)

        # store last x, y position for use in collision detection
        self.last_pos: types.Coordinate = self.rect.topleft

    def reset(self):
        self.rect.update(self.origin, self.source_rect.size)
        self.last_pos = self.rect.topleft
