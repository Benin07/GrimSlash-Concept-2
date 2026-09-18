import random
import pygame


class Particle:
    """A single fading, shrinking, gravity-bound colored rect."""

    __slots__ = ("rect", "vel", "color", "base_size",
                 "life", "max_life", "gravity", "drag")

    def __init__(self, x, y, vx, vy, size, color,
                 life=0.5, gravity=600.0, drag=0.0):
        self.base_size = size
        self.rect = pygame.Rect(0, 0, size, size)
        self.rect.center = (round(x), round(y))
        self.vel = pygame.Vector2(vx, vy)
        self.color = color
        self.life = self.max_life = life
        self.gravity = gravity
        self.drag = drag

    @property
    def alive(self):
        return self.life > 0

    @property
    def alpha_fraction(self):
        return self.life / self.max_life

    def update(self, dt):
        self.life -= dt
        self.vel.y += self.gravity * dt
        if self.drag:
            self.vel *= (1.0 - self.drag * dt)
        self.rect.x += round(self.vel.x * dt)
        self.rect.y += round(self.vel.y * dt)
        s = max(1, int(self.base_size * self.alpha_fraction))
        center = self.rect.center
        self.rect.size = (s, s)
        self.rect.center = center


class ParticleManager:
    def __init__(self, max_particles=400):
        self.particles = []
        self.max_particles = max_particles

    def spawn(self, x, y, vx, vy, size, color,
              life=0.5, gravity=600.0, drag=0.0):
        if len(self.particles) >= self.max_particles:
            self.particles.pop(0)
        self.particles.append(Particle(x, y, vx, vy, size, color,
                                       life, gravity, drag))

    def burst(self, x, y, colors, count=12, speed=180.0, size=4,
              life=0.5, gravity=600.0, up_bias=0.8, drag=0.0):
        for _ in range(count):
            mag = random.uniform(0.4, 1.0) * speed
            vx = mag * random.choice([-1, 1]) * random.uniform(0.3, 1.0)
            vy = -abs(mag) * random.uniform(0.2, 1.0) * up_bias
            self.spawn(x + random.uniform(-3, 3), y + random.uniform(-3, 3),
                       vx, vy, size + random.randint(-1, 1),
                       random.choice(colors),
                       life * random.uniform(0.6, 1.2), gravity, drag)

    # ---- convenience presets (tune these, not the call sites) ----
    def dash_dust(self, x, y, facing):
        for _ in range(6):
            self.spawn(x + random.uniform(-6, 6), y - random.uniform(0, 2),
                       vx=-facing * random.uniform(30, 90) + random.uniform(-15, 15),
                       vy=-random.uniform(10, 50),
                       size=random.randint(2, 4),
                       color=random.choice([(200, 200, 200),
                                            (160, 160, 160), (220, 220, 220)]),
                       life=random.uniform(0.25, 0.45),
                       gravity=250.0, drag=2.0)

    def hit_sparks(self, x, y):
        self.burst(x, y,
                   colors=[(220, 50, 40), (240, 110, 30), (255, 180, 60)],
                   count=random.randint(10, 15), speed=220.0, size=3,
                   life=0.45, gravity=900.0, up_bias=0.8, drag=1.2)

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surface, camera=None):
        for p in self.particles:
            r = camera.apply(p.rect) if camera else p.rect
            pygame.draw.rect(surface, p.color, r)
