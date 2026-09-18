import pygame

from entities.entity import Entity

FLASH_DURATION = 0.12


class DummyEnemy(Entity):
    """Motionless training target: hurtbox, knockback, white flash."""

    def __init__(self, x, y, hp=10):
        super().__init__(x, y, hitbox_size=(20, 40))
        self.max_hp = hp
        self.hp = hp
        self.flash_timer = 0.0

        self._base_image = pygame.Surface(self.hitbox.size, pygame.SRCALPHA)
        self._base_image.fill((140, 60, 60))
        self._flash_image = pygame.Surface(self.hitbox.size, pygame.SRCALPHA)
        self._flash_image.fill((255, 255, 255))
        self.image = self._base_image
        self.rect = self.image.get_rect()

    @property
    def hurtbox(self) -> pygame.Rect:
        return self.hitbox

    @property
    def is_invincible(self) -> bool:
        return False

    def take_damage(self, amount: int, knockback_dir=1):
        if self.hp <= 0:
            return False
        self.hp -= amount
        self.flash_timer = FLASH_DURATION
        self.vel.x = knockback_dir * 160
        self.vel.y = -140
        print(f"[DummyEnemy] took {amount} damage, hp {self.hp}/{self.max_hp}")
        if self.hp <= 0:
            print("[DummyEnemy] destroyed!")
        return True

    def update(self, dt, colliders):
        self.flash_timer -= dt
        self.apply_gravity(dt)
        self.move_and_collide(dt, colliders)
        self.image = (self._flash_image if self.flash_timer > 0
                      else self._base_image)
        self.sync_rect_to_hitbox()
