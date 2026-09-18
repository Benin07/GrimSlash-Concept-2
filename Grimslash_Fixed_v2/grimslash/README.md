# GRIMSLASH

A moody medieval-fantasy 2D hack-and-slash BOSS RUSH built on Python + Pygame.
Two bosses back-to-back: THE IRON VANGUARD, then THE PLAGUE ALCHEMIST.

## Run

    pip install -r grimslash/requirements.txt
    python main.py

You can also run `python grimslash/main.py`. The launcher now resolves bundled
assets relative to the project, so the game no longer depends on the current
working directory.

The game opens at 960 × 540 and can be resized freely. It maintains the
correct 16:9 play area with black letterboxing instead of stretching the
pixel art; mouse selection remains accurate at every window size.

## Start a Hunt

Launch the game to reach the character selection screen, then choose either:

- **Aldric** — the male Vanguard, wielding a storm-forged blade.
- **Seren** — the female Veilblade, quick and precise with teal arc magic.

Use **A / D** or **Left / Right** to choose, then press **Enter**. You can
also click a character card.

## Controls

    A/D or Arrow Keys ....... move
    Space / W / Up .......... jump (release early = short hop)
    Shift or K .............. dash (i-frames + cooldown)
    Z or J .................. attack (press again mid-swing -> combo finisher)
    F1 ...................... debug hitboxes
    R ....................... retry after death / return to selection after victory
    Esc ..................... quit

## Structure

    main.py             game loop, boss-rush flow, hit-stop, phase state machine
    settings.py         global tuning constants
    engine/             sprite_sheet, camera (trauma shake), particles, audio
    entities/           entity (physics base), player, dummy, projectile
    bosses/             boss (base class), iron_vanguard, plague_alchemist
    ui.py               HUD, boss bar, damage flash, death/victory screens
    assets/             hero strips (included) + drop-in boss sprites/audio

## The Boss Hunt

1. **The Thornwood** — a moonlit parallax forest duel against the lightning-charged
   **Iron Vanguard**. His slow cleaves and ground slam reward well-timed dashes.
2. **The Cold Ascent** — a layered mountain pass where the **Plague Alchemist**
   teleports, throws volatile flasks, and pressures you at range.

Defeating the Iron Vanguard now unlocks the second encounter directly from the
confirmed kill, so a missing or unusually long death animation cannot block
progression.

## Audio

`the-tournament.mp3` plays during a hunt. Combat effects are bundled and fire
only when their associated hit confirms:

- Your strike lands: `sword-slice.mp3`
- Iron Vanguard hits you / is defeated: `sword-slice-2.mp3` / `boss-defeat.mp3`
- Plague Alchemist hits you / is defeated: `sword-attack-combo.mp3` / `defeated-sigh.mp3`

## Art Pipeline

- Both selectable heroes use their supplied animated portraits. Their full movement
  strips live in `assets/hero_*/`.
- Boss GIFs are baked into transparent sprite sheets at
  `assets/bosses/*/*_sheet.png`; the original GIF files are retained beside them.
- Forest and mountain parallax layers live in `assets/backgrounds/` and are drawn
  at different scroll speeds during their respective chapters.
- Audio hooks are crash-safe and support `.wav`, `.ogg`, and `.mp3` files.
