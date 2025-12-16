import collections
import dataclasses
import enum
import functools
import itertools
from typing import Generator, Iterable, List, Sequence, Tuple, Type

import pygame

from . import const, io, keys, scenes, sprites, types


class Align(enum.Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class VerticalAlign(enum.Enum):
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"


@dataclasses.dataclass
class _PreparedText:
    line: str
    dest: types.Coordinate | pygame.Rect


@dataclasses.dataclass(frozen=True)
class Margins(io.Configurable):
    top: int = 0
    left: int = 0
    right: int = 0
    bottom: int = 0

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        """Returns a copy of the given Rect with margins applied

        Rect position is moved by (left, top) and size is shrunk by
        ((left + right), (top + bottom)).

        Args:
            rect (pygame.Rect): Rect to apply margins to

        Returns:
            pygame.Rect: the resulting Rect with updated position and size
        """
        return rect.inflate(-(self.left + self.right), -(self.top + self.bottom))


@dataclasses.dataclass(frozen=True)
class TextOptions(io.Configurable):
    font: pygame.font.Font
    color: types.ColorValue
    bg_color: types.ColorValue | None = None
    antialias: bool = True
    justify: bool = False
    align: Align = dataclasses.field(default=Align.LEFT)
    vertical_align: VerticalAlign = dataclasses.field(default=VerticalAlign.TOP)


@dataclasses.dataclass(frozen=True)
class TypewriterTextOptions(TextOptions):
    text_speed: int = const.DEFAULT_TEXT_SPEED
    framerate: int = const.DEFAULT_FRAMERATE
    keepalive: float = const.DEFAULT_TYPEWRITER_KEEPALIVE
    skip: keys.KeyBinding | None = None


@dataclasses.dataclass(frozen=True)
class TextBoxSettings(TypewriterTextOptions):
    auto_scroll: float = 0
    advance_text: keys.KeyBinding | None = None
    margins: Margins = dataclasses.field(default_factory=Margins)
    box_sprite: sprites.SpriteOptions = dataclasses.field(
        default_factory=sprites.SpriteOptions
    )
    indicator: sprites.SpriteOptions | None = None


# TODO: wrap this in a controller so that cache settings are configurable
# XXX: lru_cache requires all args/kwargs to be Hashable,
# so require specific args rather than a TextOptions object
@functools.lru_cache()
def create_text_surface(
    text: str,
    font: pygame.font.Font,
    antialias: bool,
    color: Tuple[int, int, int, int],
    bg_color: Tuple[int, int, int, int] | None,
) -> pygame.Surface:
    """Renders and caches text surfaces to be drawn to the screen"""
    return font.render(text, antialias, color, bg_color)


def text_sprite(
    text: str, opts: TextOptions, dest: types.Coordinate | pygame.Rect, layer: int = 0
) -> sprites.GameSprite:
    # XXX: ColorValue isn't a Hashable type, so use
    # Color.normalize() to create an RGBA tuple
    clr = pygame.Color(opts.color).normalize()
    bg_clr = (
        pygame.Color(opts.bg_color).normalize() if opts.bg_color is not None else None
    )
    img = create_text_surface(text, opts.font, opts.antialias, clr, bg_clr)
    text_w, text_h = img.get_size()

    if isinstance(dest, pygame.Rect):
        dx, dy = dest.topleft

        if opts.align is Align.CENTER:
            dx = dest.centerx - (text_w / 2)
        elif opts.align is Align.RIGHT:
            dx = dest.right - text_w

        if opts.vertical_align is VerticalAlign.CENTER:
            dy = dest.centery - (text_h / 2)
        elif opts.vertical_align is VerticalAlign.BOTTOM:
            dy = dest.bottom - text_h

        dest = (dx, dy)

    return sprites.GameSprite(
        opts=sprites.SpriteOptions(dest, text_w, text_h, img, layer)
    )


def multiline_text(
    text: str,
    opts: TextOptions,
    dest: pygame.Rect,
    layer: int = 0,
) -> List[sprites.GameSprite]:
    prepared_texts = _prepare_multiline(text, opts, dest)
    return [text_sprite(prep.line, opts, prep.dest, layer) for prep in prepared_texts]


def _prepare_multiline(
    text: str | Sequence[str],
    opts: TextOptions,
    rect: pygame.Rect,
) -> collections.deque[_PreparedText]:
    w, h = rect.size
    line_height = opts.font.get_linesize()
    prepared_texts: collections.deque[_PreparedText] = collections.deque()

    lines = text
    if isinstance(text, str):
        if opts.justify:
            lines = _split_and_justify(text, opts.font, rect)
        else:
            lines = text.splitlines()

    y_margin = 0
    if opts.vertical_align is VerticalAlign.CENTER:
        y_margin = (h - (len(lines) * line_height)) // 2
    elif opts.vertical_align is VerticalAlign.BOTTOM:
        y_margin = h - (len(lines) * line_height)

    for i, line in enumerate(lines):
        y = rect.top + (i * line_height) + y_margin
        line_rect = pygame.Rect(rect.left, y, w, line_height)
        prepared_texts.append(_PreparedText(line=line, dest=line_rect))

    return prepared_texts


def _split_and_justify(
    text: str, font: pygame.font.Font, rect: pygame.Rect
) -> List[str]:
    lines = []
    line = ""
    line_space = rect.w

    for word in text.split():
        word = f"{word} "
        text_width, _ = font.size(word)
        if text_width > line_space:
            lines.append(line)
            line = ""
            line_space = rect.w
        line += word
        line_space -= text_width

    lines.append(line)
    return lines


def typewriter(
    text: str | Iterable[_PreparedText],
    opts: TypewriterTextOptions,
    dest: pygame.Rect,
    group: pygame.sprite.LayeredUpdates | None = None,
) -> Generator[Tuple[pygame.sprite.LayeredUpdates, bool], None, None]:
    group = group or pygame.sprite.LayeredUpdates()
    text_layer = 0

    if len(group.sprites()) > 0:
        text_layer = group.get_top_layer() + 1

    if isinstance(text, str):
        prepared_texts = _prepare_multiline(text, opts, dest)
    else:
        prepared_texts = collections.deque(text)

    text_sprites = [
        text_sprite(prep.line, opts, prep.dest, text_layer) for prep in prepared_texts
    ]

    text_speed = pygame.math.clamp(opts.text_speed, 0, const.MAX_TEXT_SPEED)
    if text_speed > 0:
        tmp_group = group.copy()
        # store prepared_texts and line indices and track the
        # number of frames to wait to print each character
        # based on configured framerate and text speed
        char_idx = step_frames = 0
        current = prepared_texts.popleft()
        line = ""

        while prepared_texts or len(line) < len(current.line):
            if opts.skip and opts.skip.is_pressed():
                break

            # remove the currently typing line from the group
            tmp_group.remove_sprites_of_layer(text_layer + 1)

            if len(line) == len(current.line):
                tmp_group.add(text_sprite(current.line, opts, current.dest, text_layer))
                current = prepared_texts.popleft()
                line = ""
                char_idx = 0

            if step_frames == 0:
                line += current.line[char_idx]
                char_idx += 1
                # XXX: should the multiplier here be configurable?
                step_frames = opts.framerate // (text_speed * 6)
            step_frames -= 1

            # write the typing line to its own layer so we can replace it
            tmp_group.add(text_sprite(line, opts, current.dest, text_layer + 1))
            yield tmp_group, False

    group.add(*text_sprites)

    keepalive = int(opts.keepalive * opts.framerate)
    # special case - if keepalive is set to 0, continue to yield indefinitely
    wait_forever = keepalive == 0
    while wait_forever or keepalive > 0:
        yield group, True
        keepalive = max(keepalive - 1, 0)


class TextBox(scenes.Overlay):

    settings_type: Type[TextBoxSettings] = TextBoxSettings

    def __init__(self, settings: TextBoxSettings, screen: pygame.Surface):
        super().__init__(screen)
        self.settings = settings
        self._auto_scroll_timer = int(settings.auto_scroll * settings.framerate)
        self.auto_scroll = self._auto_scroll_timer > 0

        self.text_box = sprites.GameSprite(opts=settings.box_sprite)
        self.indicator = None
        self.text_rect = self.text_box.rect
        if self.settings.margins is not None:
            self.text_rect = self.settings.margins.apply(self.text_box.rect)

        # use a LayeredDirty group here so we can set the indicator visibility
        self.draw_group = pygame.sprite.LayeredDirty(self.text_box)  # type: ignore
        if settings.indicator is not None:
            self.indicator = sprites.GameSprite(opts=settings.indicator)
            self.indicator.layer = self.draw_group.get_top_layer() + 1
            self.draw_group.add(self.indicator)
            self.indicator.visible = False

        self._text_windows = collections.deque()
        self.writer = None

    def add_text(self, text: str):
        if not text:
            return

        if self.settings.justify:
            lines = _split_and_justify(text, self.settings.font, self.text_rect)
        else:
            lines = text.splitlines()

        lines_per_block = self.text_rect.h // self.settings.font.get_linesize()
        blocks = itertools.batched(lines, lines_per_block)
        for block in blocks:
            self._text_windows.append(
                _prepare_multiline(block, self.settings, self.text_rect)
            )

        if self.writer is None:
            self._new_writer(self._text_windows.popleft())

    def _new_writer(self, text: str):
        self.writer = typewriter(text, self.settings, self.text_rect, self.draw_group)

    def update(self, dt: float):
        if self.writer is None:
            return

        try:
            self.draw_group, finished_typing = next(self.writer)

            if finished_typing:
                self._auto_scroll_timer -= 1

                if self.indicator is not None:
                    # TODO: indicator animation
                    self.indicator.visible = True
                    self.indicator.dirty = 1

                if self._should_advance():
                    self._advance()
            else:
                # if we're still typing, the top sprite will be the
                # incomplete line - dirty it on each tick
                self.draw_group.get_top_sprite().dirty = 1
        except StopIteration:
            self._advance()

        self.draw_group.update()

    def _should_advance(self) -> bool:
        advance_text = self.auto_scroll and self._auto_scroll_timer <= 0
        advance_text_key = self.settings.advance_text
        if advance_text_key is not None and advance_text_key.is_pressed():
            advance_text = True
        return advance_text

    def _advance(self):
        if not self._text_windows:
            scenes.end_current_scene()
            return
        self._next_text_window()

    def _next_text_window(self):
        self.reset()
        self._new_writer(self._text_windows.popleft())

    def draw(self) -> List[pygame.Rect]:
        return self.draw_group.draw(self.screen)

    def dirty_all_sprites(self):
        for sprite in self.draw_group:
            sprite.dirty = 1

    def reset(self):
        super().reset()
        self.text_box.dirty = 1
        # XXX: is this faster than removing the text layer?
        self.draw_group.empty()
        self.draw_group.add(self.text_box, self.indicator)

        if self.indicator is not None:
            self.indicator.visible = False

        self._auto_scroll_timer = int(
            self.settings.auto_scroll * self.settings.framerate
        )
        self.writer = None
