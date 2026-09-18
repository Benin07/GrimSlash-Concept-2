"""Helpers for presenting the supplied animation art in the game."""

import pygame

from engine.sprite_sheet import SpriteSheet


def load_cropped_frames(path, frame_size, crop, scale=1.0, step=1):
    """Load a baked sheet, keep a stable visual window, and pixel-scale it."""
    sheet = SpriteSheet(path, frame_size=frame_size)
    left, top, width, height = crop
    frames = []
    for source in sheet.frames[::step]:
        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        frame.blit(source, (-left, -top))
        if scale != 1.0:
            frame = pygame.transform.scale_by(frame, scale)
        frames.append(frame)
    if not frames:
        raise ValueError(f"No frames found in {path}")
    return frames


class FrameLoop:
    """Small timing utility for title-screen portrait loops."""

    def __init__(self, frames, frame_duration=0.06):
        self.frames = frames
        self.frame_duration = frame_duration
        self.elapsed = 0.0
        self.index = 0

    def update(self, dt):
        self.elapsed += dt
        while self.elapsed >= self.frame_duration:
            self.elapsed -= self.frame_duration
            self.index = (self.index + 1) % len(self.frames)

    @property
    def frame(self):
        return self.frames[self.index]
