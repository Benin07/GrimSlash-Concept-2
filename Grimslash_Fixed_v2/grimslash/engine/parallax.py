"""Layered, looping environments for Grimslash's duels."""

import pygame

from settings import load_image


THEMES = {
    "forest": {
        "clear": (11, 19, 23),
        "layers": (
            ("assets/backgrounds/forest/parallax-forest-back-trees.png", 0.08, 18),
            ("assets/backgrounds/forest/parallax-forest-middle-trees.png", 0.18, 18),
            ("assets/backgrounds/forest/parallax-forest-lights.png", 0.31, 18),
            ("assets/backgrounds/forest/parallax-forest-front-trees.png", 0.45, 18),
        ),
        "ground": (20, 35, 31),
        "edge": (86, 118, 77),
        "mist": (113, 170, 134),
    },
    "mountain": {
        "clear": (19, 22, 42),
        "layers": (
            ("assets/backgrounds/mountain/parallax-mountain-bg.png", 0.05, 18),
            ("assets/backgrounds/mountain/parallax-mountain-montain-far.png", 0.12, 18),
            ("assets/backgrounds/mountain/parallax-mountain-mountains.png", 0.22, 18),
            ("assets/backgrounds/mountain/parallax-mountain-trees.png", 0.38, 18),
            ("assets/backgrounds/mountain/parallax-mountain-foreground-trees.png", 0.52, 18),
        ),
        "ground": (31, 28, 51),
        "edge": (130, 116, 162),
        "mist": (131, 127, 187),
    },
}


class ParallaxBackdrop:
    def __init__(self):
        self._themes = {}
        for name, config in THEMES.items():
            layers = []
            for path, speed, y in config["layers"]:
                try:
                    layers.append((load_image(path), speed, y))
                except (pygame.error, FileNotFoundError):
                    continue
            self._themes[name] = layers

    def draw(self, surface, theme, camera_x=0.0):
        config = THEMES[theme]
        surface.fill(config["clear"])
        width = surface.get_width()
        for image, speed, y in self._themes.get(theme, ()): 
            image_width = image.get_width()
            offset = int(camera_x * speed) % image_width
            for x in range(-image_width - offset, width + image_width, image_width):
                surface.blit(image, (x, y))

    @staticmethod
    def draw_ground(surface, ground_y, theme):
        config = THEMES[theme]
        ground_y = max(0, min(surface.get_height(), ground_y))
        pygame.draw.rect(surface, config["ground"],
                         (0, ground_y, surface.get_width(), surface.get_height() - ground_y))
        pygame.draw.line(surface, config["edge"], (0, ground_y),
                         (surface.get_width(), ground_y), 2)
        for x in range(-8, surface.get_width() + 8, 18):
            pygame.draw.line(surface, config["mist"], (x, ground_y + 4),
                             (x + 9, ground_y + 4), 1)
