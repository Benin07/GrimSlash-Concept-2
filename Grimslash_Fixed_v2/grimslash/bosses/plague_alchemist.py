import pygame

from bosses.boss import Boss
from entities.projectile import Flask
from engine.sprite_sheet import SpriteSheet, AnimationManager
from engine.art import load_cropped_frames

RUN_SPEED = 130.0
CLOSE_RANGE = 100
FAR_BAND = 260
TELEPORT_DISTANCE = 220
THROW_SPAWN_FRAME = 3
THROW_COOLDOWN = 1.0
TELEPORT_COOLDOWN = 0.6

PLACEHOLDER_COUNTS = {"idle": 6, "run": 8, "throw": 5,
                      "cast": 4, "hurt": 3, "death": 10}


def _placeholder_frames(n, size, color):
    frames = []
    for _ in range(n):
        s = pygame.Surface(size, pygame.SRCALPHA)
        s.fill(color)
        frames.append(s)
    return frames


class PlagueAlchemist(Boss):
    """Zoner: keeps 100-260px, lobs flasks, blinks away when cornered."""

    ATTACK_STATES = {"throw"}

    def __init__(self, x, y, player, assets_dir="assets/bosses/plague_alchemist"):
        super().__init__(x, y, player, hitbox_size=(16, 30),
                         max_hp=55, name="THE PLAGUE ALCHEMIST")
        self.assets_dir = assets_dir
        self.projectiles = None     # main injects the live list post-construct
        self.arena = (60, 1980)     # teleport clamp; main may override
        self._flask_thrown = False
        self.anims = self._load_animations()
        self.anims.play("idle")
        self.handlers = {
            "idle": self._update_idle,
            "run": self._update_run,
            "throw": self._update_throw,
            "cast": self._update_cast,
            "hurt": self._update_hurt,
            "death": self._update_death,
        }

    def _load_animations(self):
        cfg = {"idle": ("idle.png", 0.12, True), "run": ("run.png", 0.09, True),
               "throw": ("throw.png", 0.09, False), "cast": ("cast.png", 0.08, False),
               "hurt": ("hurt.png", 0.10, False), "death": ("death.png", 0.12, False)}
        am = AnimationManager()
        try:
            art_frames = load_cropped_frames(
                f"{self.assets_dir}/plague_alchemist_sheet.png", (175, 160),
                crop=(0, 0, 175, 160), scale=1.0, step=3)
        except (FileNotFoundError, pygame.error, ValueError):
            art_frames = None
        for state, (fname, dur, loop) in cfg.items():
            if art_frames:
                am.add(state, art_frames, frame_duration=0.05, loop=loop)
            else:
                try:
                    sheet = SpriteSheet(f"{self.assets_dir}/{fname}",
                                        frame_width=64, frame_height=64)
                    am.add(state, sheet.frames, frame_duration=dur, loop=loop)
                except (FileNotFoundError, pygame.error):
                    am.add(state, _placeholder_frames(
                        PLACEHOLDER_COUNTS[state], (64, 64), (80, 110, 80, 255)),
                        frame_duration=dur, loop=loop)
        return am

    # -------------------------------------------------- AI
    def think(self, distance):
        if distance < CLOSE_RANGE:
            self.change_state("cast")
        elif distance > FAR_BAND:
            self.change_state("run")
        else:
            self.change_state("throw")

    def _update_idle(self, dt):
        self.vel.x = 0.0
        self._face_player()
        if self.cooldown_timer <= 0:
            self.think(self.distance_to_player())

    def _update_run(self, dt):
        self._face_player()
        self.vel.x = self.facing * RUN_SPEED
        if self.distance_to_player() <= FAR_BAND - 30:
            self.end_attack(cooldown=0.2)

    def _update_throw(self, dt):
        self.vel.x = 0.0
        anim = self.anims._anims["throw"]
        if not self._flask_thrown and anim.frame_index >= THROW_SPAWN_FRAME:
            self._flask_thrown = True
            if self.projectiles is not None:
                self.projectiles.append(Flask(
                    x=self.hitbox.centerx + self.facing * 10,
                    y=self.hitbox.centery - 6,
                    target_x=self.player.hitbox.centerx,
                    on_hit=self._notify_flask_hit))
        if self.state_timer >= self.anim_duration():
            self._flask_thrown = False
            self.end_attack(cooldown=THROW_COOLDOWN)

    def _update_cast(self, dt):
        self.vel.x = 0.0
        if self.state_timer >= self.anim_duration():
            self._teleport()
            self.end_attack(cooldown=TELEPORT_COOLDOWN)

    def _teleport(self):
        px = self.player.hitbox.centerx
        side = -1 if self.hitbox.centerx >= px else 1
        new_x = px + side * TELEPORT_DISTANCE
        lo, hi = self.arena
        new_x = max(lo + 16, min(hi - 16, new_x))
        if abs(new_x - px) < CLOSE_RANGE * 0.7:
            new_x = px - side * TELEPORT_DISTANCE
            new_x = max(lo + 16, min(hi - 16, new_x))
        self.pos.x = new_x
        self.hitbox.midbottom = (round(self.pos.x), round(self.pos.y))
        self._face_player()
        print(f"[PlagueAlchemist] teleported to x={new_x}")

    def _notify_flask_hit(self):
        if self.on_player_hit:
            self.on_player_hit(self, 1)

    def _update_hurt(self, dt):
        self.vel.x = self._approach(self.vel.x, 0, 900 * dt)
        if self.state_timer >= self.HURT_STAGGER:
            self.change_state("idle")

    def _update_death(self, dt):
        self.vel.x = 0.0
