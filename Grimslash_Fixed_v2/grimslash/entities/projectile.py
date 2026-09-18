import pygame


class Projectile:
    """Hazard with a lifespan. Not an Entity -- no axis-collision commit."""

    def __init__(self, x, y, vx, vy, size=(8, 8), color=(120, 220, 80),
                 damage=1, lifespan=2.0, gravity=0.0, on_hit=None):
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = (round(x), round(y))
        self.vel = pygame.Vector2(vx, vy)
        self.color = color
        self.damage = damage
        self.lifespan = lifespan
        self.gravity = gravity
        self.on_hit = on_hit
        self.alive = True

    def update(self, dt, colliders, player):
        if not self.alive:
            return
        self.lifespan -= dt
        if self.lifespan <= 0:
            self.alive = False
            return
        self.vel.y += self.gravity * dt
        self.rect.x += round(self.vel.x * dt)
        self.rect.y += round(self.vel.y * dt)

        for col in colliders:
            if self.rect.colliderect(col):
                self.alive = False
                return
        if player and player.state != "death" \
                and self.rect.colliderect(player.hitbox):
            direction = 1 if self.vel.x >= 0 else -1
            landed = player.take_damage(self.damage, knockback_dir=direction)
            if landed and self.on_hit:
                self.on_hit()
            self.alive = False

    def draw(self, surface, camera=None):
        r = camera.apply(self.rect) if camera else self.rect
        pygame.draw.rect(surface, self.color, r)
        pygame.draw.rect(surface, (235, 255, 210), r, 1)


class Flask(Projectile):
    """The Alchemist's toxin flask -- straight-line, fast, green."""

    SPEED = 300.0

    def __init__(self, x, y, target_x, on_hit=None):
        vx = self.SPEED if target_x >= x else -self.SPEED
        super().__init__(x, y, vx, 0, size=(8, 10),
                         color=(110, 210, 70), damage=1, lifespan=2.0,
                         on_hit=on_hit)
