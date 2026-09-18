from pathlib import Path

import pygame

# Resolve all bundled assets relative to this file, not the caller's
# current working directory. This makes the game runnable from the project
# folder, the ZIP's parent folder, or an IDE launcher.
PROJECT_ROOT = Path(__file__).resolve().parent


def resolve_path(path: str) -> str:
    p = Path(path)
    return str(p if p.is_absolute() else PROJECT_ROOT / p)


# --- Display ---
# The game world stays at a fixed logical size.  The window can be resized;
# main.py fits this surface into it without stretching or cropping.
LOGICAL_WIDTH, LOGICAL_HEIGHT = 320, 180
SCREEN_WIDTH, SCREEN_HEIGHT = 960, 540
WINDOW_TITLE = "Grimslash"
FPS_CAP = 0  # 0 = uncapped; dt-driven movement

# --- Pixel art ---
# Preferred launch size (320 x 180 at 3x).  Rendering no longer assumes it.
PIXEL_SCALE = 3

# --- Physics (units: pixels / second) ---
GRAVITY = 2200.0
MAX_FALL_SPEED = 900.0

# --- Colors ---
BG_COLOR = (18, 18, 24)


def load_image(path: str) -> pygame.Surface:
    """Load an image using a project-relative path when needed."""
    return pygame.image.load(resolve_path(path)).convert_alpha()
