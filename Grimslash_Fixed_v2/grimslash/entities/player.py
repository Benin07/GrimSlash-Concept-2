import os
import pygame

from entities.entity import Entity
from engine.sprite_sheet import SpriteSheet, AnimationManager

# --- Movement tuning ---
MOVE_SPEED = 170.0
GROUND_ACCEL = 1800.0
GROUND_DECEL = 2400.0
AIR_ACCEL = 1100.0
AIR_DECEL = 400.0

JUMP_VELOCITY = -560.0
JUMP_CUT_MULTIPLIER = 0.45
COYOTE_TIME = 0.09
JUMP_BUFFER = 0.12

DASH_SPEED = 460.0
DASH_DURATION = 0.16
DASH_COOLDOWN = 0.55
DASH_IFRAMES = 0.22

# --- Combat tuning ---
COMBO_OPEN_FRAC = 0.55
ATTACK_HITBOX_SIZE = (32, 40)
ATTACK_ACTIVE_FRAMES = {"attack_1": (2, 3), "attack_2": (3, 4)}
ATTACK_DAMAGE = {"attack_1": 2, "attack_2": 4}
ATTACK_HITSTOP = {"attack_1": 0.08, "attack_2": 0.12}
ATTACK_TRAUMA = {"attack_1": 0.35, "attack_2": 0.65}

# --- Hero strips: state -> (start_frame, end_frame, frame_dur, loop) ---
# Verify/adjust indices against assets/hero_*/_preview.png contact sheets.
PLAYER_PLACEHOLDER_COUNTS = {
    "hero_female": {"idle": 13, "attack_1": 14, "run": 11, "jump_up": 12,
                    "fall": 12, "attack_2": 16, "dash": 12, "death": 22},
    "hero_male": {"idle": 10, "attack_1": 10, "attack_2": 9, "run": 9,
                  "jump_up": 15, "fall": 15, "dash": 15, "death": 24},
}

HERO_SEGMENTS = {
    "hero_female": {
        "idle":       (0,  13, 0.09, True),
        "attack_1":   (13, 27, 0.07, False),
        "run":        (27, 38, 0.08, True),
        "jump_up":    (38, 50, 0.07, False),
        "fall":       (38, 50, 0.07, False),
        "attack_2":   (50, 66, 0.08, False),
        "dash":       (38, 50, 0.05, False),
        "death":      (66, 88, 0.09, False),
    },
    "hero_male": {
        "idle":       (0, 10, 0.09, True),
        "attack_1":   (10, 20, 0.06, False),
        "attack_2":   (20, 29, 0.07, False),
        "run":        (29, 38, 0.08, True),
        "jump_up":    (38, 53, 0.05, False),
        "fall":       (38, 53, 0.05, False),
        "dash":       (38, 53, 0.05, False),
        "death":      (53, 77, 0.08, False),
    },
}


class Player(Entity):
    def __init__(self, x, y, assets_dir="assets/hero_male"):
        super().__init__(x, y, hitbox_size=(16, 30))
        self.assets_dir = assets_dir

        self.max_hp = 100
        self.hp = 100

        self.state = "idle"
        self.state_timer = 0.0
        self.coyote_timer = 0.0
        self.jump_buffer_timer = 0.0
        self.dash_timer = 0.0
        self.dash_cooldown_timer = 0.0
        self.invuln_timer = 0.0
        self.dash_direction = 1

        self.queued_attack = False
        self.current_attack = None
        self.attack_hitbox = None
        self._hit_enemies = set()
        self._enemies_ref = []

        self.keys = pygame.key.get_pressed()
        self._prev_keys = self.keys

        # External hooks (assigned by main)
        self.on_hit = None
        self.on_dash = None
        self.on_damaged = None
        self.audio = None

        self.LOCKED_STATES = {"dash", "attack_1", "attack_2", "death"}

        self.anims = self._load_animations()
        self.anims.play("idle")

    # ------------------------------------------------------ loading
    def _load_animations(self):
        hero_id = os.path.basename(self.assets_dir.rstrip("/\\"))
        if hero_id not in HERO_SEGMENTS:
            raise ValueError(f"Unknown hero asset set: {hero_id!r}")

        am = AnimationManager()
        segments = HERO_SEGMENTS[hero_id]
        try:
            strip = SpriteSheet(f"{self.assets_dir}/strip_all.png",
                                frame_size=(192, 192), scale=1 / 3)
            for state, (a, b, dur, loop) in segments.items():
                frames = strip.frames[a:b]
                if not frames:
                    raise ValueError(
                        f"Hero animation {state!r} is empty "
                        f"(frames {a}:{b}, sheet has {len(strip.frames)})."
                    )
                am.add(state, frames, frame_duration=dur, loop=loop)
        except (FileNotFoundError, pygame.error, ValueError, AssertionError) as exc:
            # The gameplay remains usable even when optional art is missing
            # or a custom strip has the wrong frame layout.
            print(f"[Player] animation sheet unavailable ({exc}); "
                  "using built-in placeholders.")
            colors = {
                "idle": (80, 100, 150, 255),
                "attack_1": (110, 125, 180, 255),
                "attack_2": (140, 110, 170, 255),
                "run": (80, 150, 120, 255),
                "jump_up": (100, 140, 190, 255),
                "dash": (180, 150, 80, 255),
                "death": (100, 70, 80, 255),
            }
            for state, (a, b, dur, loop) in segments.items():
                n = PLAYER_PLACEHOLDER_COUNTS[hero_id][state]
                frames = []
                for _ in range(n):
                    frame = pygame.Surface((64, 64), pygame.SRCALPHA)
                    frame.fill(colors.get(state, (100, 100, 100, 255)))
                    frames.append(frame)
                am.add(state, frames, frame_duration=dur, loop=loop)
        return am

    # ------------------------------------------------------ input
    def handle_keydown(self, key):
        if key in (pygame.K_z, pygame.K_j):
            self._on_attack_press()
        elif key in (pygame.K_LSHIFT, pygame.K_k):
            self._try_dash()

    def handle_keyup(self, key):
        if key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
            if self.vel.y < 0:
                self.vel.y *= JUMP_CUT_MULTIPLIER

    def _pressed_this_frame(self, *keycodes):
        return any(self.keys[k] and not self._prev_keys[k] for k in keycodes)

    # ------------------------------------------------------ state machine
    def change_state(self, new_state: str):
        self.state = new_state
        self.state_timer = 0.0
        self.anims.play(new_state, force=True)

        if new_state == "dash":
            self.dash_timer = DASH_DURATION
            self.dash_cooldown_timer = DASH_COOLDOWN
            self.invuln_timer = max(self.invuln_timer, DASH_IFRAMES)
            if self.keys[pygame.K_a] or self.keys[pygame.K_LEFT]:
                self.dash_direction = -1
            elif self.keys[pygame.K_d] or self.keys[pygame.K_RIGHT]:
                self.dash_direction = 1
            else:
                self.dash_direction = self.facing
            self.facing = self.dash_direction
            self.vel.x = self.dash_direction * DASH_SPEED
            self.vel.y = 0.0
            if self.on_dash:
                self.on_dash()
        elif new_state in ("attack_1", "attack_2"):
            self._hit_enemies.clear()

    # ------------------------------------------------------ actions
    def _try_dash(self):
        if self.state in self.LOCKED_STATES:
            return
        if self.dash_cooldown_timer > 0:
            return
        self.change_state("dash")

    def _on_attack_press(self):
        if self.state == "attack_1":
            frac = self.state_timer / self._attack_duration("attack_1")
            if frac >= COMBO_OPEN_FRAC:
                self.queued_attack = True
            return
        if self.state in ("attack_2", "dash", "death"):
            return
        self.current_attack = "attack_1"
        self.change_state("attack_1")

    def _attack_duration(self, name) -> float:
        anim = self.anims._anims[name]
        return anim.frame_duration * len(anim.frames)

    # ------------------------------------------------------ update
    def update(self, dt, colliders, enemies=None):
        self._enemies_ref = enemies or []
        self.state_timer += dt
        self.coyote_timer -= dt
        self.jump_buffer_timer -= dt
        self.dash_cooldown_timer -= dt
        self.invuln_timer -= dt

        if self._pressed_this_frame(pygame.K_SPACE, pygame.K_w, pygame.K_UP):
            self.jump_buffer_timer = JUMP_BUFFER

        handler = {
            "idle": self._update_grounded,
            "run": self._update_grounded,
            "jump_up": self._update_air,
            "fall": self._update_air,
            "dash": self._update_dash,
            "attack_1": self._update_attack,
            "attack_2": self._update_attack,
            "death": self._update_death,
        }[self.state]
        handler(dt)

        self._prev_keys = self.keys

        if self.state != "dash":
            self.apply_gravity(dt)
        self.move_and_collide(dt, colliders)

        if self.on_ground:
            self.coyote_timer = COYOTE_TIME

        if self.state in ("jump_up", "fall") and self.on_ground:
            self.change_state("idle")
        elif self.state in ("idle", "run") and not self.on_ground:
            self.change_state("fall")

        self.anims.update(dt)
        self.sync_rect_to_hitbox(self.anims.current_frame)

    # ------------------------------------------------------ state handlers
    def _horizontal_control(self, dt, accel, decel):
        left = self.keys[pygame.K_a] or self.keys[pygame.K_LEFT]
        right = self.keys[pygame.K_d] or self.keys[pygame.K_RIGHT]
        target = (right - left) * MOVE_SPEED
        if target != 0:
            self.facing = 1 if target > 0 else -1
            self.vel.x = self._approach(self.vel.x, target, accel * dt)
        else:
            self.vel.x = self._approach(self.vel.x, 0, decel * dt)

    @staticmethod
    def _approach(value, target, step):
        if value < target:
            return min(value + step, target)
        return max(value - step, target)

    def _try_buffered_jump(self):
        if self.jump_buffer_timer > 0 and self.coyote_timer > 0:
            self.vel.y = JUMP_VELOCITY
            self.jump_buffer_timer = 0
            self.coyote_timer = 0
            self.change_state("jump_up")
            return True
        return False

    def _update_grounded(self, dt):
        self._horizontal_control(dt, GROUND_ACCEL, GROUND_DECEL)
        moving = abs(self.vel.x) > 1.0
        if self.state != "run" and moving:
            self.change_state("run")
        elif self.state != "idle" and not moving:
            self.change_state("idle")
        self._try_buffered_jump()

    def _update_air(self, dt):
        self._horizontal_control(dt, AIR_ACCEL, AIR_DECEL)
        if not self._try_buffered_jump() and self.state == "jump_up" and self.vel.y >= 0:
            self.change_state("fall")

    def _update_dash(self, dt):
        self.dash_timer -= dt
        if self.dash_timer <= 0:
            self.vel.x *= 0.25
            self.change_state("fall" if not self.on_ground else "idle")

    def _update_attack(self, dt):
        self.vel.x = self._approach(self.vel.x, 0, 1200 * dt)
        self._update_attack_hitbox()

        duration = self._attack_duration(self.current_attack)
        if self.state_timer >= duration:
            self.attack_hitbox = None
            if self.current_attack == "attack_1" and self.queued_attack:
                self.queued_attack = False
                self.current_attack = "attack_2"
                self.change_state("attack_2")
            else:
                self.queued_attack = False
                self.current_attack = None
                self.change_state("fall" if not self.on_ground else "idle")

    def _update_attack_hitbox(self):
        anim = self.anims._anims[self.current_attack]
        first, last = ATTACK_ACTIVE_FRAMES[self.current_attack]
        if not (first <= anim.frame_index <= last):
            self.attack_hitbox = None
            return

        w, h = ATTACK_HITBOX_SIZE
        hb = self.hitbox
        x = hb.centerx if self.facing > 0 else hb.centerx - w
        self.attack_hitbox = pygame.Rect(x, hb.centery - h // 2, w, h)

        if self.on_hit is None:
            return
        for enemy in list(self._enemies_ref):
            if enemy in self._hit_enemies or enemy.hp <= 0:
                continue
            if self.attack_hitbox.colliderect(enemy.hurtbox):
                self._hit_enemies.add(enemy)
                heavy = (self.current_attack == "attack_2")
                self.on_hit(enemy, ATTACK_DAMAGE[self.current_attack], heavy)

    def _update_death(self, dt):
        self.vel.x = 0

    # ------------------------------------------------------ damage
    def take_damage(self, amount: int, knockback_dir=None,
                    knockback=(140, -200)):
        if self.is_invincible or self.state == "death":
            return False
        self.hp -= amount
        print(f"[Player] took {amount}, hp {self.hp}/{self.max_hp}")
        if self.on_damaged:
            self.on_damaged(amount)

        if self.hp <= 0:
            self.hp = 0
            self.vel.update(0, 0)
            self.change_state("death")
            print("[Player] has fallen.")
            return True

        kb = pygame.Vector2(knockback)
        if knockback_dir is not None:
            kb.x = abs(kb.x) * knockback_dir
        else:
            kb.x *= -self.facing
        self.vel = kb
        self.invuln_timer = 0.8
        return True

    @property
    def is_invincible(self) -> bool:
        return self.invuln_timer > 0

    def reset(self, x, y):
        self.pos.update(x, y)
        self.vel.update(0, 0)
        self.hitbox.midbottom = (round(x), round(y))
        self.hp = self.max_hp
        self.invuln_timer = 0.0
        self.dash_timer = 0.0
        self.dash_cooldown_timer = 0.0
        self.queued_attack = False
        self.current_attack = None
        self.attack_hitbox = None
        self._hit_enemies.clear()
        self.change_state("idle")

    # ------------------------------------------------------ draw
    def draw(self, surface, camera=None):
        # Flicker while invincible (wall-clock, so it persists through
        # hit-stop) -- never flicker during death, the anim must be seen.
        if self.is_invincible and self.state != "death":
            if (pygame.time.get_ticks() // 90) % 2 == 0:
                return
        super().draw(surface, camera)

    # ------------------------------------------------------ debug
    def draw_debug(self, surface, camera=None):
        hb = camera.apply(self.hitbox) if camera else self.hitbox
        pygame.draw.rect(surface, (60, 130, 255, 160), hb, 1)

    def draw_attack_debug(self, surface, camera=None):
        if self.attack_hitbox:
            ab = camera.apply(self.attack_hitbox) if camera else self.attack_hitbox
            pygame.draw.rect(surface, (255, 60, 60), ab, 1)
