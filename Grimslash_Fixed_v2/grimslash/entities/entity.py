import pygame
from settings import GRAVITY, MAX_FALL_SPEED


class Entity(pygame.sprite.Sprite):
    """
    Base class for anything that moves in the world.

    Design rule: self.hitbox (the small discrete box) is the ONLY thing
    that exists in physics space. self.image/self.rect exist only for
    drawing -- rect is re-anchored from the hitbox every frame.
    """

    def __init__(self, x, y, hitbox_size=(16, 30), gravity_scale=1.0):
        super().__init__()
        self.pos = pygame.Vector2(x, y)          # hitbox CENTER-BOTTOM point
        self.vel = pygame.Vector2(0, 0)
        self.gravity_scale = gravity_scale

        self.hitbox = pygame.Rect(0, 0, *hitbox_size)
        self.hitbox.midbottom = (round(self.pos.x), round(self.pos.y))

        self.on_ground = False
        self.facing = 1                          # 1 = right, -1 = left

        self.image = pygame.Surface(hitbox_size, pygame.SRCALPHA)
        self.rect = self.image.get_rect()

    def apply_gravity(self, dt):
        self.vel.y += GRAVITY * self.gravity_scale * dt
        if self.vel.y > MAX_FALL_SPEED:
            self.vel.y = MAX_FALL_SPEED

    def move_and_collide(self, dt, colliders):
        """Axis-separated collision: move X, resolve, then move Y, resolve."""
        self.pos.x += self.vel.x * dt
        self.hitbox.midbottom = (round(self.pos.x), round(self.pos.y))
        for col in colliders:
            if self.hitbox.colliderect(col):
                if self.vel.x > 0:
                    self.hitbox.right = col.left
                elif self.vel.x < 0:
                    self.hitbox.left = col.right
                self.pos.x = self.hitbox.centerx
                self.vel.x = 0

        self.pos.y += self.vel.y * dt
        self.hitbox.midbottom = (round(self.pos.x), round(self.pos.y))
        self.on_ground = False
        for col in colliders:
            if self.hitbox.colliderect(col):
                if self.vel.y > 0:
                    self.hitbox.bottom = col.top
                    self.on_ground = True
                elif self.vel.y < 0:
                    self.hitbox.top = col.bottom
                self.pos.y = self.hitbox.bottom
                self.vel.y = 0

    def sync_rect_to_hitbox(self, anim_frame=None):
        if anim_frame is not None:
            self.image = anim_frame
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.hitbox.midbottom

    def draw(self, surface, camera=None):
        img = self.image
        if self.facing < 0:
            img = pygame.transform.flip(img, True, False)
        draw_pos = self.rect
        if camera is not None:
            draw_pos = camera.apply(self.rect)
        surface.blit(img, draw_pos)

    @property
    def is_invincible(self) -> bool:
        return False
