import random
import pygame

from bosses.boss import Boss
from engine.sprite_sheet import SpriteSheet, AnimationManager
from engine.art import load_cropped_frames

WALK_SPEED = 42.0
ATTACK_RANGE = 80
STOP_DISTANCE = 66
SLAM_HOP = -210.0

ATTACK_HITBOXES = {
    "attack_1": ((0.42, 0.62), (60, 50), "front"),    # Forward Cleave
    "attack_2": ((0.50, 0.70), (100, 40), "center"),  # AoE Ground Slam
}
ATTACK_DAMAGE = 1

# Fallback frame counts when art has not been dropped in yet
PLACEHOLDER_COUNTS = {"idle": 6, "walk": 8, "attack_1": 7,
                      "attack_2": 9, "hurt": 3, "death": 12}


def _placeholder_frames(n, size, color):
    frames = []
    for _ in range(n):
        s = pygame.Surface(size, pygame.SRCALPHA)
        s.fill(color)
        frames.append(s)
    return frames


class IronVanguard(Boss):
    """Boss 1 -- slow, armored, telegraphed. Teaches dash-dodging."""

    ATTACK_STATES = {"attack_1", "attack_2"}

    def __init__(self, x, y, player, assets_dir="assets/bosses/iron_vanguard"):
        super().__init__(x, y, player, hitbox_size=(32, 64),
                         max_hp=60, name="THE IRON VANGUARD")
        self.assets_dir = assets_dir
        self.anims = self._load_animations()
        self.anims.play("idle")
        self.handlers = {
            "idle": self._update_idle,
            "walk": self._update_walk,
            "attack_1": self._update_attack,
            "attack_2": self._update_attack,
            "hurt": self._update_hurt,
            "death": self._update_death,
        }

    def _load_animations(self):
        cfg = {"idle": ("idle.png", 0.14, True), "walk": ("walk.png", 0.13, True),
               "attack_1": ("attack_1.png", 0.11, False),
               "attack_2": ("attack_2.png", 0.13, False),
               "hurt": ("hurt.png", 0.10, False), "death": ("death.png", 0.12, False)}
        am = AnimationManager()
        # The supplied GIF is baked into a transparent sheet at setup time.
        # Reusing its energized loop across states keeps the original motion
        # alive while the game AI supplies the combat timing.
        try:
            art_frames = load_cropped_frames(
                f"{self.assets_dir}/iron_vanguard_sheet.png", (186, 177),
                crop=(0, 0, 186, 177), scale=1.0, step=1)
        except (FileNotFoundError, pygame.error, ValueError):
            art_frames = None
        for state, (fname, dur, loop) in cfg.items():
            if art_frames:
                am.add(state, art_frames, frame_duration=0.045, loop=loop)
            else:
                try:
                    sheet = SpriteSheet(f"{self.assets_dir}/{fname}",
                                        frame_width=128, frame_height=128)
                    am.add(state, sheet.frames, frame_duration=dur, loop=loop)
                except (FileNotFoundError, pygame.error):
                    am.add(state, _placeholder_frames(
                        PLACEHOLDER_COUNTS[state], (128, 128), (90, 90, 110, 255)),
                        frame_duration=dur, loop=loop)
        return am

    # -------------------------------------------------- state entries
    def on_state_enter(self, state):
        if state == "attack_1":
            self._face_player()
            self.vel.x = self.facing * 140         # heavy lunge
        elif state == "attack_2":
            self._face_player()
            self.vel.x = 0.0
            if self.on_ground:
                self.vel.y = SLAM_HOP
        elif state == "death":
            self.vel.x = 0.0

    # -------------------------------------------------- AI + handlers
    def think(self, distance):
        if distance > ATTACK_RANGE:
            self.change_state("walk")
        else:
            self.change_state(random.choice(["attack_1", "attack_2"]))

    def _update_idle(self, dt):
        self.vel.x = 0.0
        if self.cooldown_timer <= 0:
            self.think(self.distance_to_player())

    def _update_walk(self, dt):
        self._face_player()
        self.vel.x = self.facing * WALK_SPEED
        if self.distance_to_player() <= STOP_DISTANCE:
            self.change_state(random.choice(["attack_1", "attack_2"]))

    def _update_attack(self, dt):
        self.vel.x = self._approach(self.vel.x, 0, 500 * dt)
        self._update_attack_hitbox()
        if self.state_timer >= self.anim_duration():
            self.end_attack()                      # 1.5s punish window

    def _update_attack_hitbox(self):
        (start, end), (w, h), placement = ATTACK_HITBOXES[self.state]
        progress = self.state_timer / max(self.anim_duration(), 0.001)
        if not (start <= progress <= end):
            self.attack_hitbox = None
            return
        if placement == "front":
            x = self.hitbox.centerx if self.facing > 0 else self.hitbox.centerx - w
            y = self.hitbox.centery - h // 2
        else:
            x = self.hitbox.centerx - w // 2
            y = self.hitbox.bottom - h
        self.attack_hitbox = pygame.Rect(x, y, w, h)

        if not self._struck_player and self.player is not None:
            if self.attack_hitbox.colliderect(self.player.hitbox):
                self._struck_player = True
                direction = 1 if self.player.hitbox.centerx >= self.hitbox.centerx else -1
                self.damage_player(ATTACK_DAMAGE, knockback_dir=direction)

    def _update_hurt(self, dt):
        self.vel.x = self._approach(self.vel.x, 0, 600 * dt)
        if self.state_timer >= self.HURT_STAGGER:
            self.change_state("idle")

    def _update_death(self, dt):
        self.vel.x = 0.0
