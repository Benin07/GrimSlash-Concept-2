import pygame
from settings import load_image


class SpriteSheet:
    """
    Loads a PNG and slices it into frames.

    Two modes:
      1. Grid mode:        SpriteSheet(path, frame_width=32, frame_height=32)
         - Sheet is a strict grid; empty padding cells are skipped.
      2. Auto-strip mode:  SpriteSheet(path, frame_size=(57, 88), scale=1)
         - Every frame is exactly frame_size; count inferred from sheet width.
    """

    def __init__(self, path, frame_width=None, frame_height=None,
                 frame_size=None, scale=1):
        self.sheet = load_image(path)
        self.scale = scale

        if frame_size is not None:
            fw, fh = frame_size
        else:
            fw, fh = frame_width, frame_height
        assert fw and fh, "SpriteSheet needs frame dimensions."

        self.frame_w, self.frame_h = fw, fh
        self.frames = self._slice()

    def _slice(self):
        sheet_w, sheet_h = self.sheet.get_size()
        frames = []
        for y in range(0, sheet_h, self.frame_h):
            for x in range(0, sheet_w, self.frame_w):
                frame = self._cut(x, y)
                if self._is_blank(frame):
                    continue
                frames.append(frame)
        return frames

    def _cut(self, x, y):
        frame = pygame.Surface((self.frame_w, self.frame_h), pygame.SRCALPHA)
        frame.blit(self.sheet, (0, 0), (x, y, self.frame_w, self.frame_h))
        if self.scale != 1:
            frame = pygame.transform.scale_by(frame, self.scale)
        return frame

    @staticmethod
    def _is_blank(surface) -> bool:
        # A transparent frame has no bounding box with alpha >= 1.
        # This is deterministic and avoids relying on transform-average
        # behavior that has varied across pygame versions.
        return surface.get_bounding_rect(min_alpha=1).width == 0

    def get_frame(self, index: int) -> pygame.Surface:
        return self.frames[index % len(self.frames)]

    def __len__(self):
        return len(self.frames)


class Animation:
    """One named animation: frames + timing + loop policy."""
    __slots__ = ("frames", "frame_duration", "loop",
                 "elapsed", "frame_index", "finished")

    def __init__(self, frames, frame_duration=0.1, loop=True):
        assert frames, "Animation needs at least one frame."
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop
        self.elapsed = 0.0
        self.frame_index = 0
        self.finished = False

    def update(self, dt: float):
        if self.finished:
            return
        self.elapsed += dt
        while self.elapsed >= self.frame_duration:
            self.elapsed -= self.frame_duration
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                if self.loop:
                    self.frame_index = 0
                else:
                    self.frame_index = len(self.frames) - 1
                    self.finished = True

    def reset(self):
        self.elapsed = 0.0
        self.frame_index = 0
        self.finished = False

    @property
    def current_frame(self) -> pygame.Surface:
        return self.frames[self.frame_index]


class AnimationManager:
    """
    Owns all of an entity's animations and enforces one active state.
    play() without force is a no-op if already playing -> animations never
    restart mid-state; only genuine state changes trigger resets.
    """

    def __init__(self):
        self._anims = {}
        self._current = None
        self._current_name = None

    def add(self, name: str, frames, frame_duration=0.1, loop=True):
        self._anims[name] = Animation(frames, frame_duration, loop)

    def play(self, name: str, force: bool = False):
        if name == self._current_name and not force:
            return
        anim = self._anims.get(name)
        assert anim, f"Animation '{name}' not registered."
        anim.reset()
        self._current = anim
        self._current_name = name

    def update(self, dt: float):
        if self._current:
            self._current.update(dt)

    @property
    def current_frame(self) -> pygame.Surface:
        assert self._current, "No animation playing."
        return self._current.current_frame

    @property
    def frame_index(self) -> int:
        return self._current.frame_index if self._current else 0

    @property
    def finished(self) -> bool:
        return self._current.finished if self._current else False

    @property
    def current_name(self):
        return self._current_name
