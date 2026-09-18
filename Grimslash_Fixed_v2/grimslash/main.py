import math
import os
import sys
from pathlib import Path

# Let both `python main.py` and `python grimslash/main.py` find bundled art.
PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))
os.chdir(PROJECT_DIR)

import pygame

from settings import (LOGICAL_WIDTH, LOGICAL_HEIGHT, SCREEN_WIDTH,
                      SCREEN_HEIGHT, WINDOW_TITLE, FPS_CAP, load_image)
from engine.art import FrameLoop, load_cropped_frames
from engine.camera import Camera
from engine.parallax import ParallaxBackdrop
from engine.particles import ParticleManager
from engine.audio import AudioManager
from entities.player import Player
from bosses.iron_vanguard import IronVanguard
from bosses.plague_alchemist import PlagueAlchemist
from ui import UI, FADE_DURATION


BOSS_RUSH = (IronVanguard, PlagueAlchemist)
BOSS_THEMES = ("forest", "mountain")
BOSS_CHAPTERS = ("CHAPTER I — THE THORNWOOD", "CHAPTER II — THE COLD ASCENT")
BOSS_DEFEATED_DURATION = 2.3
VICTORY_FADE = 1.8
ENCOUNTER_CARD_DURATION = 2.5
BOSS_AUDIO = (
    ("sword-slice-2", "boss-defeat"),
    ("sword-attack-combo", "defeated-sigh"),
)
HEROES = (
    ("Aldric", "assets/hero_male"),
    ("Seren", "assets/hero_female"),
)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)
        self.native_w = LOGICAL_WIDTH
        self.native_h = LOGICAL_HEIGHT
        self.native = pygame.Surface((self.native_w, self.native_h))
        self.window = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.viewport = pygame.Rect(0, 0, self.native_w, self.native_h)
        self._refresh_viewport()
        self.clock = pygame.time.Clock()
        self.running = True

        self.level_rects = [
            pygame.Rect(-500, 400, 3000, 200),
            pygame.Rect(470, 310, 132, 14),
            pygame.Rect(815, 255, 132, 14),
        ]
        self.camera = Camera(2048, 640, (self.native_w, self.native_h))
        self.backdrop = ParallaxBackdrop()
        self.ui = UI()
        self.particles = ParticleManager()
        self.audio = AudioManager()
        self.swoosh = self._load_swoosh()
        self.portraits = self._load_portraits()

        self.player_spawn = (200, 380)
        self.boss_spawn = (900, 380)
        self.player = None
        self.boss = None
        self.projectiles = []
        self.current_boss_index = 0
        self.selected_hero = 0
        self.phase = "title"
        self.fade_t = 0.0
        self.boss_defeated_timer = 0.0
        self.encounter_timer = 0.0
        self.hitstop_timer = 0.0
        self.debug = False
        self.title_time = 0.0

    # ------------------------------------------------------ presentation
    def _refresh_viewport(self):
        """Fit the logical game surface into the current window."""
        window_w, window_h = self.window.get_size()
        scale = min(window_w / self.native_w, window_h / self.native_h)
        width = max(1, round(self.native_w * scale))
        height = max(1, round(self.native_h * scale))
        self.viewport = pygame.Rect((window_w - width) // 2,
                                    (window_h - height) // 2,
                                    width, height)

    def _window_to_native(self, position):
        """Map pointer input through the letterboxed presentation."""
        if not self.viewport.collidepoint(position):
            return None
        x = (position[0] - self.viewport.x) * self.native_w / self.viewport.width
        y = (position[1] - self.viewport.y) * self.native_h / self.viewport.height
        return int(x), int(y)

    def _load_swoosh(self):
        try:
            return pygame.transform.scale_by(load_image("assets/swoosh.png"), 1 / 3)
        except (pygame.error, FileNotFoundError):
            return None

    def _load_portraits(self):
        configs = (
            ("assets/characters/aldric_sheet.png", (155, 112), (0, 0, 155, 112), 1.0, 3),
            ("assets/characters/seren_sheet.png", (122, 115), (0, 0, 122, 115), 1.0, 3),
        )
        portraits = []
        for path, frame_size, crop, scale, step in configs:
            try:
                frames = load_cropped_frames(path, frame_size, crop, scale, step)
            except (FileNotFoundError, pygame.error, ValueError):
                fallback = pygame.Surface((88, 74), pygame.SRCALPHA)
                pygame.draw.polygon(fallback, (180, 190, 200),
                                    ((44, 5), (64, 31), (55, 67), (30, 67), (22, 31)))
                frames = [fallback]
            portraits.append(FrameLoop(frames, 0.065))
        return portraits

    @property
    def active_theme(self):
        if self.phase == "title":
            return "forest"
        return BOSS_THEMES[min(self.current_boss_index, len(BOSS_THEMES) - 1)]

    # ------------------------------------------------------ flow
    def _begin_hunt(self):
        _, assets_dir = HEROES[self.selected_hero]
        self.player = Player(*self.player_spawn, assets_dir=assets_dir)
        self.player.audio = self.audio
        self.player.on_hit = self._on_player_hit
        self.player.on_dash = self._on_player_dash
        self.player.on_damaged = lambda amount: self.ui.trigger_flash()
        self.current_boss_index = 0
        self.projectiles.clear()
        self._spawn_boss(self.current_boss_index)
        self.audio.play_music("the-tournament", volume=0.34)
        self.camera.offset.update(0, 0)
        self.camera._initialized = False
        self.phase = "playing"
        self.encounter_timer = ENCOUNTER_CARD_DURATION

    def _spawn_boss(self, index):
        self.boss = BOSS_RUSH[index](*self.boss_spawn, player=self.player)
        if hasattr(self.boss, "projectiles"):
            self.boss.projectiles = self.projectiles
        if hasattr(self.boss, "arena"):
            self.boss.arena = (80, 1980)
        self.boss.on_damaged = self._on_boss_damaged
        self.boss.on_player_hit = self._on_boss_hit_player
        self.boss.player_hit_sound, self.boss.defeat_sound = BOSS_AUDIO[index]

    def _advance_boss_rush(self):
        self.current_boss_index += 1
        if self.current_boss_index >= len(BOSS_RUSH):
            self.phase = "victory_fading"
            self.fade_t = 0.0
            self.audio.stop_music()
            return
        self.projectiles.clear()
        self.player.reset(*self.player_spawn)
        self.player.invuln_timer = 1.0
        self.camera.offset.update(0, 0)
        self.camera._initialized = False
        self._spawn_boss(self.current_boss_index)
        # Leaving this as "boss_defeated" would consume the next transition
        # timer immediately and skip straight from Chapter I to victory.
        self.phase = "playing"
        self.encounter_timer = ENCOUNTER_CARD_DURATION

    def _return_to_title(self):
        self.player = None
        self.boss = None
        self.projectiles.clear()
        self.current_boss_index = 0
        self.phase = "title"
        self.fade_t = 0.0
        self.audio.stop_music()
        self.camera.offset.update(0, 0)
        self.camera._initialized = False

    # ------------------------------------------------------ combat hooks
    def _on_player_dash(self):
        feet = (self.player.hitbox.centerx, self.player.hitbox.bottom)
        self.particles.dash_dust(*feet, self.player.facing)
        self.audio.play_sound("dash", volume=0.5)

    def _on_player_hit(self, enemy, damage, heavy):
        direction = 1 if enemy.hitbox.centerx >= self.player.hitbox.centerx else -1
        enemy.take_damage(damage, knockback_dir=direction)
        self.trigger_hitstop(0.12 if heavy else 0.08)
        self.camera.add_trauma(0.65 if heavy else 0.35)
        cx = enemy.hitbox.centerx - direction * enemy.hitbox.width // 2
        self.particles.hit_sparks(cx, enemy.hitbox.centery)
        self.audio.play_sound("sword-slice", volume=0.72)

    def _on_boss_damaged(self, amount):
        self.camera.add_trauma(0.15)

    def _on_boss_hit_player(self, boss, amount):
        self.audio.play_sound(boss.player_hit_sound, volume=0.72)

    def trigger_hitstop(self, duration: float):
        self.hitstop_timer = max(self.hitstop_timer, duration)

    # ------------------------------------------------------ loop + input
    def run(self):
        while self.running:
            raw_dt = self.clock.tick(FPS_CAP) / 1000.0
            dt = min(raw_dt, 1.0 / 30.0)
            self.handle_events()
            self.title_time += raw_dt
            for portrait in self.portraits:
                portrait.update(raw_dt)
            self.ui.update(raw_dt)
            self.particles.update(raw_dt)

            if self.hitstop_timer > 0:
                self.hitstop_timer -= raw_dt
                sim_dt = 0.0
            else:
                sim_dt = dt
            self.camera.decay_shake(raw_dt)

            if self.phase == "playing":
                self.update(sim_dt)
            elif self.phase == "boss_defeated":
                # Continue the death animation while the transition card is up.
                if self.boss:
                    self.boss.update(sim_dt, self.level_rects)
                self.boss_defeated_timer -= raw_dt
                if self.boss_defeated_timer <= 0:
                    self._advance_boss_rush()
            self.update_death_flow(raw_dt)
            self.encounter_timer = max(0.0, self.encounter_timer - raw_dt)
            self.render()
        pygame.quit()

    def _handle_title_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected_hero = 0
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected_hero = 1
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z, pygame.K_j):
                self._begin_hunt()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            position = self._window_to_native(event.pos)
            if position is None:
                return
            x, y = position
            if pygame.Rect(26, 55, 118, 84).collidepoint(x, y):
                self.selected_hero = 0
            elif pygame.Rect(176, 55, 118, 84).collidepoint(x, y):
                self.selected_hero = 1

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue
            if event.type in (pygame.VIDEORESIZE, pygame.WINDOWRESIZED):
                self._refresh_viewport()
                continue
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
                continue
            if self.phase == "title":
                self._handle_title_event(event)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.phase in ("gameover", "victory"):
                    self.soft_reset()
                elif event.key == pygame.K_F1:
                    self.debug = not self.debug
                elif self.phase == "playing":
                    self.player.handle_keydown(event.key)
            elif event.type == pygame.KEYUP and self.player:
                self.player.handle_keyup(event.key)

    # ------------------------------------------------------ game simulation
    def update(self, dt):
        self.player.keys = pygame.key.get_pressed()
        targets = [self.boss] if self.boss and self.boss.hp > 0 else []
        self.player.update(dt, self.level_rects, enemies=targets)
        if self.boss:
            self.boss.update(dt, self.level_rects)
        for projectile in self.projectiles:
            projectile.update(dt, self.level_rects, self.player)
        self.projectiles[:] = [projectile for projectile in self.projectiles if projectile.alive]

        if (self.boss and not self.boss.activated
                and abs(self.player.pos.x - self.boss.pos.x) < 380):
            self.boss.activated = True
            self.camera.add_trauma(0.3)
        self.camera.note_facing(self.player.facing)
        self.camera.update(dt, self.player.hitbox)

    def update_death_flow(self, raw_dt):
        if self.phase == "playing":
            if self.player.state == "death" and self.player.anims.finished:
                self.phase = "fading"
                self.fade_t = 0.0
            # Advance from the confirmed kill, rather than waiting on an
            # optional art animation to report completion.  This guarantees
            # the Plague Alchemist encounter always unlocks.
            elif self.boss and self.boss.hp <= 0:
                self.phase = "boss_defeated"
                self.boss_defeated_timer = BOSS_DEFEATED_DURATION
                self.player.hp = self.player.max_hp
                self.player.invuln_timer = 1.0
                self.audio.play_sound(self.boss.defeat_sound, volume=0.85)
                self.camera.add_trauma(0.8)
        elif self.phase == "fading":
            self.fade_t = min(1.0, self.fade_t + raw_dt / FADE_DURATION)
            if self.fade_t >= 1.0:
                self.phase = "gameover"
        elif self.phase == "victory_fading":
            self.fade_t = min(1.0, self.fade_t + raw_dt / VICTORY_FADE)
            if self.fade_t >= 1.0:
                self.phase = "victory"

    def soft_reset(self):
        if self.phase == "victory":
            self._return_to_title()
            return
        self.player.reset(*self.player_spawn)
        self.projectiles.clear()
        self.hitstop_timer = 0.0
        self.phase = "playing"
        self.fade_t = 0.0
        self.camera.offset.update(0, 0)
        self.camera._initialized = False
        self._spawn_boss(self.current_boss_index)
        self.encounter_timer = ENCOUNTER_CARD_DURATION

    # ------------------------------------------------------ render
    def _draw_platforms(self):
        for platform in self.level_rects[1:]:
            rect = self.camera.apply(platform)
            pygame.draw.rect(self.native, (38, 48, 47), rect)
            pygame.draw.line(self.native, (135, 152, 112), rect.topleft, rect.topright, 1)

    def _draw_swoosh(self):
        if not self.swoosh or not self.player or not self.player.current_attack:
            return
        image = self.swoosh
        if self.player.facing < 0:
            image = pygame.transform.flip(image, True, False)
        origin = self.camera.apply(self.player.hitbox)
        x = origin.centerx if self.player.facing > 0 else origin.centerx - image.get_width()
        self.native.blit(image, (x, origin.centery - image.get_height() // 2))

    def render(self):
        self.backdrop.draw(self.native, self.active_theme, self.camera.offset.x)
        ground_y = self.camera.apply(self.level_rects[0]).top
        self.backdrop.draw_ground(self.native, ground_y, self.active_theme)

        if self.phase == "title":
            self.ui.draw_title(self.native, self.portraits, self.selected_hero,
                               (math.sin(self.title_time * 3.2) + 1) * 0.5)
        else:
            self._draw_platforms()
            if self.debug:
                for collider in self.level_rects:
                    pygame.draw.rect(self.native, (90, 200, 90), self.camera.apply(collider), 1)
            if self.boss and (self.boss.hp > 0 or self.boss.state == "death"):
                self.boss.draw(self.native, camera=self.camera)
            for projectile in self.projectiles:
                projectile.draw(self.native, camera=self.camera)
            self._draw_swoosh()
            if self.player:
                self.player.draw(self.native, camera=self.camera)
            self.particles.draw(self.native, camera=self.camera)

            if self.debug and self.player:
                self.player.draw_debug(self.native, camera=self.camera)
                self.player.draw_attack_debug(self.native, camera=self.camera)
                if self.boss:
                    self.boss.draw_debug(self.native, camera=self.camera)

            self.ui.draw_health_bar(self.native, self.player)
            self.ui.draw_flash(self.native)
            if self.boss and self.boss.activated:
                self.ui.draw_boss_bar(self.native, self.boss)
            if self.boss:
                chapter = BOSS_CHAPTERS[min(self.current_boss_index, len(BOSS_CHAPTERS) - 1)]
                self.ui.draw_encounter(self.native, chapter,
                                       self.boss.name, self.encounter_timer)

            if self.phase in ("fading", "gameover"):
                self.ui.draw_death_screen(self.native, self.fade_t)
            elif self.phase == "boss_defeated":
                self.ui.draw_boss_defeated(
                    self.native, BOSS_DEFEATED_DURATION - self.boss_defeated_timer)
            elif self.phase in ("victory_fading", "victory"):
                self.ui.draw_victory_screen(self.native, self.fade_t)

        # Nearest-neighbour scaling retains the pixel-art look at all sizes.
        self.window.fill((0, 0, 0))
        scaled = pygame.transform.scale(self.native, self.viewport.size)
        self.window.blit(scaled, self.viewport.topleft)
        pygame.display.flip()


if __name__ == "__main__":
    Game().run()
