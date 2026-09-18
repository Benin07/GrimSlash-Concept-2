from entities.entity import Entity


class Boss(Entity):
    """
    Shared skeleton for all Grimslash bosses.

    Subclass contract:
      - set ATTACK_STATES (states that must not be staggered out of)
      - build self.anims in __init__
      - fill self.handlers = {"idle": fn, ...}
      - override on_state_enter(state) for attack entries (lunges, hops)
      - override think(distance) for idle-state decision making
    Base update loop, damage intake, cooldown discipline, and death
    handling are inherited and never duplicated.
    """

    ATTACK_STATES = set()
    HURT_STAGGER = 0.40
    POST_ATTACK_COOLDOWN = 1.5

    def __init__(self, x, y, player, hitbox_size, max_hp, name):
        super().__init__(x, y, hitbox_size=hitbox_size)
        self.player = player
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp

        self.state = "idle"
        self.state_timer = 0.0
        self.cooldown_timer = 1.0
        self.activated = False

        self.attack_hitbox = None
        self._struck_player = False
        self.on_damaged = None
        self.on_player_hit = None
        self.handlers = {}
        self.anims = None

    # ------------------------------------------------ combat interface
    @property
    def hurtbox(self):
        return self.hitbox

    @property
    def is_invincible(self):
        return False

    @property
    def dead(self):
        return self.state == "death" and self.anims.finished

    def take_damage(self, amount: int, knockback_dir=1):
        if self.state == "death":
            return False
        self.hp -= amount
        self.activated = True
        print(f"[{self.name}] took {amount}, hp {self.hp}/{self.max_hp}")
        if self.on_damaged:
            self.on_damaged(amount)
        if self.hp <= 0:
            self.hp = 0
            self.change_state("death")
            print(f"[{self.name}] has been slain!")
            return True
        # Armor rule: hits during attacks deal damage but never stagger
        if self.state not in self.ATTACK_STATES and "hurt" in self.handlers:
            self.vel.x = knockback_dir * 40
            self.change_state("hurt")
        return True

    def damage_player(self, amount: int, knockback_dir=None) -> bool:
        """Deal damage and notify the game only when the hit actually lands."""
        if self.player is None:
            return False
        landed = self.player.take_damage(amount, knockback_dir=knockback_dir)
        if landed and self.on_player_hit:
            self.on_player_hit(self, amount)
        return landed

    # ------------------------------------------------ state machine core
    def change_state(self, new_state: str):
        self.state = new_state
        self.state_timer = 0.0
        self.anims.play(new_state, force=True)
        self.attack_hitbox = None
        self._struck_player = False
        if new_state == "death":
            self.vel.x = 0.0
        self.on_state_enter(new_state)

    def on_state_enter(self, state: str):
        """Subclass hook: lunges, hop velocity, spawns."""
        pass

    def think(self, distance: float):
        """Subclass AI hook, called from the subclass's idle handler."""
        raise NotImplementedError

    # ------------------------------------------------ main loop
    def update(self, dt, colliders):
        self.state_timer += dt
        self.cooldown_timer -= dt

        handler = self.handlers.get(self.state)
        if handler:
            handler(dt)

        if self.state != "death":
            self.apply_gravity(dt)
            self.move_and_collide(dt, colliders)

        self.anims.update(dt)
        self.sync_rect_to_hitbox(self.anims.current_frame)

    def end_attack(self, cooldown=None):
        self.attack_hitbox = None
        self.cooldown_timer = cooldown if cooldown is not None \
            else self.POST_ATTACK_COOLDOWN
        self.change_state("idle")

    # ------------------------------------------------ shared helpers
    def anim_duration(self, state=None) -> float:
        anim = self.anims._anims[state or self.state]
        return anim.frame_duration * len(anim.frames)

    def distance_to_player(self) -> float:
        return abs(self.player.hitbox.centerx - self.hitbox.centerx)

    def _face_player(self):
        dx = self.player.hitbox.centerx - self.hitbox.centerx
        self.facing = 1 if dx >= 0 else -1

    @staticmethod
    def _approach(value, target, step):
        if value < target:
            return min(value + step, target)
        return max(value - step, target)

    def reset(self, x, y):
        self.pos.update(x, y)
        self.vel.update(0, 0)
        self.hitbox.midbottom = (round(x), round(y))
        self.hp = self.max_hp
        self.cooldown_timer = 1.0
        self.activated = False
        self.change_state("idle")

    # ------------------------------------------------ debug
    def draw_debug(self, surface, camera=None):
        hb = camera.apply(self.hitbox) if camera else self.hitbox
        pygame.draw.rect(surface, (255, 60, 60, 160), hb, 1)
        if self.attack_hitbox:
            ab = camera.apply(self.attack_hitbox) if camera else self.attack_hitbox
            pygame.draw.rect(surface, (255, 160, 40), ab, 1)
