import pygame


FLASH_DURATION = 0.12
FADE_DURATION = 1.15
HUD_W, HUD_H = 104, 11
HUD_POS = (10, 13)
BOSS_BAR_W, BOSS_BAR_H = 190, 9


class UI:
    def __init__(self):
        self.font_title = pygame.font.Font(None, 40)
        self.font_big = pygame.font.Font(None, 27)
        self.font_medium = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 12)
        self.flash_alpha = 0.0

    @staticmethod
    def _label(surface, font, text, color, center, shadow=(8, 9, 14)):
        shade = font.render(text, False, shadow)
        image = font.render(text, False, color)
        rect = image.get_rect(center=center)
        surface.blit(shade, rect.move(1, 1))
        surface.blit(image, rect)
        return rect

    def trigger_flash(self):
        self.flash_alpha = 150.0

    def update(self, raw_dt: float):
        if self.flash_alpha > 0:
            self.flash_alpha = max(0.0, self.flash_alpha - 150.0 / FLASH_DURATION * raw_dt)

    # ------------------------------------------------------ title selection
    def draw_title(self, surf, portraits, selected, pulse):
        w, h = surf.get_size()
        shade = pygame.Surface((w, h), pygame.SRCALPHA)
        shade.fill((4, 8, 14, 96))
        surf.blit(shade, (0, 0))
        self._label(surf, self.font_title, "GRIMSLASH", (232, 217, 171), (w // 2, 25))
        self._label(surf, self.font_small, "A TWO-CHAPTER BOSS HUNT", (155, 183, 181),
                    (w // 2, 42))

        names = ("ALDRIC", "SEREN")
        roles = ("THE VANGUARD", "THE VEILBLADE")
        colors = ((213, 169, 86), (70, 205, 196))
        for index, (name, role, portrait) in enumerate(zip(names, roles, portraits)):
            card = pygame.Rect(26 + index * 150, 55, 118, 84)
            chosen = index == selected
            if chosen:
                glow = int(90 + 55 * pulse)
                pygame.draw.rect(surf, (*colors[index], glow), card.inflate(4, 4), border_radius=3)
            pygame.draw.rect(surf, (13, 19, 27, 225), card, border_radius=2)
            pygame.draw.rect(surf, colors[index] if chosen else (62, 73, 83), card, 1, border_radius=2)
            image = portrait.frame
            fit = min(88 / image.get_width(), 54 / image.get_height())
            preview = pygame.transform.scale_by(image, fit)
            surf.blit(preview, preview.get_rect(center=(card.centerx, card.y + 35)))
            self._label(surf, self.font_medium, name, colors[index],
                        (card.centerx, card.bottom - 20))
            self._label(surf, self.font_small, role, (185, 193, 192),
                        (card.centerx, card.bottom - 9))

        self._label(surf, self.font_small, "ARROWS / A D  SELECT     ENTER  BEGIN",
                    (222, 221, 205), (w // 2, h - 14))

    def draw_encounter(self, surf, chapter, boss_name, t):
        if t <= 0:
            return
        alpha = min(1.0, t * 2.5, (2.5 - t) * 2.5)
        if alpha <= 0:
            return
        w, h = surf.get_size()
        panel = pygame.Surface((w, 44), pygame.SRCALPHA)
        panel.fill((5, 7, 12, int(150 * alpha)))
        surf.blit(panel, (0, h // 2 - 25))
        self._label(surf, self.font_small, chapter, (178, 165, 123), (w // 2, h // 2 - 13))
        self._label(surf, self.font_big, boss_name, (235, 221, 182), (w // 2, h // 2 + 5))

    # ------------------------------------------------------ health bar
    def draw_health_bar(self, surf: pygame.Surface, player):
        x, y = HUD_POS
        ratio = max(0.0, player.hp / player.max_hp)
        pygame.draw.rect(surf, (9, 10, 15), (x - 2, y - 2, HUD_W + 4, HUD_H + 4))
        pygame.draw.rect(surf, (68, 18, 26), (x, y, HUD_W, HUD_H))
        fill_w = int(HUD_W * ratio)
        if fill_w:
            pygame.draw.rect(surf, (196, 45, 54), (x, y, fill_w, HUD_H))
            pygame.draw.line(surf, (255, 117, 111), (x, y), (x + fill_w - 1, y))
        for i in range(1, 10):
            sx = x + int(HUD_W * i / 10)
            pygame.draw.line(surf, (18, 16, 19), (sx, y), (sx, y + HUD_H - 1))
        self._label(surf, self.font_small, "VITALITY", (229, 219, 198),
                    (x + 24, y - 7))
        self._label(surf, self.font_small, f"{player.hp:03d} / {player.max_hp:03d}",
                    (255, 238, 217), (x + HUD_W - 24, y - 7))

    # ------------------------------------------------------ boss bar
    def draw_boss_bar(self, surf: pygame.Surface, boss):
        if boss.hp <= 0:
            return
        w, h = surf.get_size()
        x, y = (w - BOSS_BAR_W) // 2, h - 20
        self._label(surf, self.font_small,
                    f"{boss.name}  {boss.hp:02d} / {boss.max_hp:02d}",
                    (230, 211, 181), (w // 2, y - 7))
        ratio = max(0.0, boss.hp / boss.max_hp)
        pygame.draw.rect(surf, (9, 10, 15), (x - 2, y - 2, BOSS_BAR_W + 4, BOSS_BAR_H + 4))
        pygame.draw.rect(surf, (57, 15, 19), (x, y, BOSS_BAR_W, BOSS_BAR_H))
        fill = int(BOSS_BAR_W * ratio)
        if fill:
            pygame.draw.rect(surf, (177, 39, 48), (x, y, fill, BOSS_BAR_H))
            pygame.draw.line(surf, (247, 101, 92), (x, y), (x + fill - 1, y))

    # ------------------------------------------------------ flash + end screens
    def draw_flash(self, surf: pygame.Surface):
        if self.flash_alpha <= 0:
            return
        overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        overlay.fill((196, 24, 33, int(self.flash_alpha)))
        surf.blit(overlay, (0, 0))

    def _end_overlay(self, surf, fade_t, title, color, prompt):
        overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(215 * min(1.0, fade_t))))
        surf.blit(overlay, (0, 0))
        if fade_t < 1:
            return
        w, h = surf.get_size()
        self._label(surf, self.font_big, title, color, (w // 2, h // 2 - 10))
        self._label(surf, self.font_small, prompt, (224, 220, 207), (w // 2, h // 2 + 15))

    def draw_death_screen(self, surf, fade_t):
        self._end_overlay(surf, fade_t, "YOU DIED", (188, 47, 54), "R  TRY AGAIN")

    def draw_boss_defeated(self, surf, t):
        scale = min(1.0, 0.55 + t * 3.0)
        font = pygame.font.Font(None, max(1, int(26 * scale)))
        self._label(surf, font, "BOSS DEFEATED", (232, 200, 106),
                    (surf.get_width() // 2, surf.get_height() // 2 - 8))

    def draw_victory_screen(self, surf, fade_t):
        self._end_overlay(surf, fade_t, "HUNT COMPLETE", (235, 204, 109),
                          "R  RETURN TO THE HUNT")
