import random
import pygame


class Camera:
    """
    Follows a target hitbox with deadzone + frame-rate-independent lerp.

    Screen shake: add_trauma() on impacts; apply() adds a decaying random
    offset. Trauma is squared -> gentle at low values, violent at high.
    decay_shake() must be called with RAW dt every frame (even hit-stop).
    """

    MAX_SHAKE = 5.0            # px at native resolution at full trauma
    TRAUMA_DECAY = 1.6         # trauma per second recovered

    def __init__(self, level_width, level_height, viewport_size=(320, 180),
                 deadzone=(120, 70), lerp_speed=6.0, lookahead=36):
        self.level_w = level_width
        self.level_h = level_height
        self.viewport_w, self.viewport_h = viewport_size
        self.deadzone_size = pygame.Vector2(*deadzone)
        self.lerp_speed = lerp_speed
        self.lookahead = lookahead

        self.offset = pygame.Vector2(0, 0)
        self.trauma = 0.0
        self._shake = pygame.Vector2(0, 0)
        self._target_facing = 1
        self._initialized = False

    def add_trauma(self, amount: float):
        self.trauma = min(1.0, self.trauma + amount)

    def decay_shake(self, raw_dt: float):
        self.trauma = max(0.0, self.trauma - self.TRAUMA_DECAY * raw_dt)
        shake_mag = (self.trauma ** 2) * self.MAX_SHAKE
        if shake_mag < 0.05:
            self._shake.update(0, 0)
        else:
            self._shake.update(random.uniform(-1, 1) * shake_mag,
                               random.uniform(-1, 1) * shake_mag)

    def update(self, dt, target_hitbox: pygame.Rect):
        # The deadzone is measured in screen space, centred in the full
        # viewport.  The previous camera used the deadzone itself as the view
        # size, which pushed the player to an edge and made large resolutions
        # show the wrong portion of the arena.
        deadzone = pygame.Rect(0, 0, *self.deadzone_size)
        deadzone.center = (self.viewport_w // 2, self.viewport_h // 2)
        target = pygame.Vector2(
            target_hitbox.centerx + self._target_facing * self.lookahead,
            target_hitbox.centery)
        on_screen = target - self.offset
        desired_offset = self.offset.copy()
        if not self._initialized:
            desired_offset = target - pygame.Vector2(self.viewport_w / 2,
                                                      self.viewport_h / 2)
        else:
            if on_screen.x < deadzone.left:
                desired_offset.x = target.x - deadzone.left
            elif on_screen.x > deadzone.right:
                desired_offset.x = target.x - deadzone.right
            if on_screen.y < deadzone.top:
                desired_offset.y = target.y - deadzone.top
            elif on_screen.y > deadzone.bottom:
                desired_offset.y = target.y - deadzone.bottom

        t = 1.0 - pow(2.718281828, -self.lerp_speed * dt)
        self.offset += (desired_offset - self.offset) * t

        max_x = max(0, self.level_w - self.viewport_w)
        max_y = max(0, self.level_h - self.viewport_h)
        self.offset.x = max(0, min(self.offset.x, max_x))
        self.offset.y = max(0, min(self.offset.y, max_y))
        self._initialized = True

    def note_facing(self, facing: int):
        self._target_facing = facing

    def apply(self, world_rect: pygame.Rect) -> pygame.Rect:
        return world_rect.move(
            -round(self.offset.x + self._shake.x),
            -round(self.offset.y + self._shake.y))
