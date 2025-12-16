import dataclasses
from typing import Dict, List

import pygame

from . import io, types


@dataclasses.dataclass(frozen=True)
class SpriteOptions(io.Configurable):
    topleft: types.Coordinate = (0, 0)
    width: float = 0
    height: float = 0
    image: pygame.Surface | None = None
    layer: int = 0


@dataclasses.dataclass(frozen=True)
class AnimationOptions(io.Configurable):
    name: str
    repeat: int


@dataclasses.dataclass(frozen=True)
class SpriteSheetSettings(io.Configurable):
    sprite_sheet: pygame.Surface
    sprite_width: int
    sprite_height: int
    animation_opts: List[AnimationOptions]


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


# TODO:
class Animation(pygame.sprite.WeakSprite):

    def __init__(self, opts: AnimationOptions, frames: List[pygame.Surface]):
        self.repeat = opts.repeat
        self.frames = frames
        self.frames_inverted = [pygame.transform.flip(f, True, False) for f in frames]
        self.image = frames[0]
        self.rect = self.image.get_rect()

    def play(self, pos: types.Coordinate):
        pass


class SpriteSheet(io.Loadable):

    def __init__(self, opts: SpriteSheetSettings):
        self.sprite_sheet = opts.sprite_sheet
        self.sprite_width = opts.sprite_width
        self.sprite_height = opts.sprite_height
        self.animations = self._load_animations(opts.animation_opts)

    def _load_animations(
        self, animation_opts: List[AnimationOptions]
    ) -> Dict[str, Animation]:
        animations = {}
        # each row in the sprite sheet represents an animation
        for i, opts in enumerate(animation_opts):
            frames = self._split_frames(i)
            animations[opts.name] = Animation(opts, frames)
        return animations

    def _split_frames(self, idx: int) -> List:
        frames = []
        for i in range(self.sprite_sheet.get_width() // self.sprite_width):
            topleft = (i * self.sprite_width, idx * self.sprite_height)
            wh = (self.sprite_width, self.sprite_height)
            frame = self.sprite_sheet.subsurface(topleft, wh)
            # create a mask of the frame and check if it contains any
            # non-transparent pixels. if not, break and return
            mask = pygame.mask.from_surface(frame)
            if mask.count() == 0:
                break
            frames.append(frame)
        return frames
