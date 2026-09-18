# GRIMSLASH

<div align="center">

![GRIMSLASH: A Two-Chapter Boss Hunt](docs/screenshots/banner.svg)

**A moody medieval-fantasy 2D hack-and-slash BOSS RUSH built on Python and Pygame.**

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/pygame-v2.5.0+-C2185B?style=for-the-badge&logo=python&logoColor=white)](https://www.pygame.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-4B5563?style=for-the-badge)](https://github.com/)
[![Resolution](https://img.shields.io/badge/target-960%C3%97540%20%40%2060%20FPS-10B981?style=for-the-badge)](https://github.com/)
[![License](https://img.shields.io/badge/license-MIT-EAB308?style=for-the-badge)](LICENSE)

[Quickstart](#-quickstart--installation) • [The Boss Hunt](#-the-boss-hunt) • [Controls](#-controls--combat-mechanics) • [Architecture](#-project-architecture) • [Troubleshooting](#-troubleshooting--faq)

</div>

---

## 📖 Overview

**GRIMSLASH** is a high-intensity 2D action boss rush. Step into the boots of either **Aldric the Vanguard** or **Seren the Veilblade** and confront two ancient horrors back-to-back: **The Iron Vanguard** deep within the moonlit Thornwood, and **The Plague Alchemist** perched atop the frozen peaks of the Cold Ascent.

Engineered from the ground up for crisp combat feel, Grimslash features:
- ⚔️ **Impact-Driven Combat**: Hit-stop freeze frames, trauma-based screen shake, and pixel spark bursts on confirmed strikes.
- 💨 **Invulnerability Dash**: Fluid evasion with dedicated i-frames and balanced cooldown timers.
- 🦘 **Variable-Height Jump Physics**: Tap for a surgical short-hop or hold to gain maximum vertical clearance.
- 🖥️ **Aspect Ratio Preservation**: Native 960 × 540 pixel canvas that scales cleanly to any display resolution with clean black letterboxing and pixel-accurate mouse coordinate re-mapping.
- 🛡️ **Crash-Safe Progression**: Confirmed kill detection unlocks chapter transitions safely without relying on fragile animation timers.

---

## 📸 Screenshots & Gameplay

### Character Selection
Choose your hunter before embarking on the gauntlet. Each hero offers distinct animations, attack arcs, and visual effects.

<div align="center">
  <img src="docs/screenshots/character_select.svg" alt="Grimslash Character Selection" width="900" />
  <p><em>Aldric (The Vanguard) and Seren (The Veilblade) ready for the hunt.</em></p>
</div>

---

### Chapter I: The Thornwood
*Duel against the lightning-charged Iron Vanguard beneath a stormy canopy.*

<div align="center">
  <img src="docs/screenshots/boss_iron_vanguard.svg" alt="Chapter 1: The Iron Vanguard" width="900" />
  <p><em>Execute precise dashes through devastating greatsword cleaves and ground shockwaves.</em></p>
</div>

---

### Chapter II: The Cold Ascent
*Survive volatile chemical flask barrages and sudden teleportation rifts on the icy peaks.*

<div align="center">
  <img src="docs/screenshots/boss_plague_alchemist.svg" alt="Chapter 2: The Plague Alchemist" width="900" />
  <p><em>Close the distance with aerial combo finishers while evading lingering poison clouds.</em></p>
</div>

---

## 🗡️ Playable Heroes

| Hero | Title | Signature Weapon | Playstyle & Trait |
| :--- | :--- | :--- | :--- |
| **Aldric** | *The Vanguard* | Storm-forged Greatsword & Crested Shield | High-poise melee brawler; electric blue sparks and heavy downward cleave strikes. |
| **Seren** | *The Veilblade* | Dual Arc Daggers | Lightning-fast agility; low hitboxes, teal magical crescent cuts, and rapid recovery. |

---

## ⚔️ The Boss Hunt

1. **Chapter I — The Thornwood**
   - **Boss**: *The Iron Vanguard*
   - **Threats**: Slow wind-up cleaves with deceptive reach, jumping overhead ground slams, and lightning shockwave trails.
   - **Strategy**: Bait his heavy thrusts, dash through his blade during active i-frames, and unleash a two-hit combo before rolling away.

2. **Chapter II — The Cold Ascent**
   - **Boss**: *The Plague Alchemist*
   - **Threats**: Area-denial poison mist, lobbed explosive vials, and defensive teleportation when pressured.
   - **Strategy**: Track the purple teleport runes, bait flask arcs, and utilize short-hop jump strikes to catch him during spell recoveries.

---

## 🎮 Controls & Combat Mechanics

### Default Keybindings

| Action | Primary Key | Secondary Key | Notes |
| :--- | :---: | :---: | :--- |
| **Move Left / Right** | `A` / `D` | `←` / `→` | Smooth analog acceleration and friction deceleration |
| **Jump** | `Space` | `W` / `↑` | **Variable height**: Release early for short hop, hold for full jump |
| **Dash (Evade)** | `Shift` | `K` | Grants **invulnerability frames (i-frames)**; cooldown indicator on HUD |
| **Attack / Combo** | `Z` | `J` | Press once for slash; press again mid-swing for **Combo Finisher** |
| **Debug Hitboxes** | `F1` | — | Toggles visual collision, hurtbox, and attack hitboxes |
| **Retry / Select** | `R` | — | Instant retry upon death or return to character select after victory |
| **Quit Game** | `Esc` | — | Saves settings and cleanly releases SDL display/audio handles |

---

## 🚀 Quickstart & Installation

Follow the steps below to set up your local environment and run the game.

### Prerequisites
- **Python 3.10+** (Python 3.10, 3.11, or 3.12 recommended)
- **Git** (for cloning the repository)
- **pip** (Python package installer)

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/grimslash.git
cd grimslash
```

---

### Step 2: Create a Virtual Environment

Isolating your Python environment prevents dependency conflicts with system packages.

#### 🪟 Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
*(If you encounter execution policy restrictions in PowerShell, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first, or use Command Prompt: `.\.venv\Scripts\activate.bat`)*

#### 🍎 macOS (Terminal)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 🐧 Linux (Debian / Ubuntu / Mint / Fedora / Arch)
```bash
# Ubuntu / Debian systems require python3-venv package:
sudo apt-get update && sudo apt-get install -y python3-venv python3-pip

python3 -m venv .venv
source .venv/bin/activate
```

#### 🐍 Conda (Alternative)
```bash
conda create -n grimslash python=3.11 -y
conda activate grimslash
```

---

### Step 3: Install Dependencies

Install the required packages using `pip`:

```bash
pip install -r requirements.txt
```

*Or install Pygame directly:*
```bash
pip install pygame>=2.5.0
```

> **Tip:** You can also use **pygame-ce** (Community Edition) for bleeding-edge optimizations and improved audio latency:
> ```bash
> pip install pygame-ce
> ```

---

### Step 4: Launch the Game

Run the entry point from your terminal:

```bash
python main.py
```

*Or if launching from the parent folder:*
```bash
python grimslash/main.py
```

The game automatically resolves all bundled assets relative to its installation root, allowing you to launch from any working directory!

---

## 📂 Project Architecture

```
grimslash/
├── main.py                  # Main game loop, chapter state machine, hit-stop orchestrator
├── settings.py              # Global tuning constants (960x540 base, gravity, i-frames, volumes)
├── ui.py                    # HUD rendering, boss health bars, damage flashes, death/victory screens
├── engine/
│   ├── camera.py            # Trauma-based camera shake & horizontal tracking
│   ├── sprite_sheet.py      # Sprite sheet slicer & frame cache
│   ├── particles.py         # Pixel spark emitters, dust puffs, and slash trails
│   └── audio.py             # Crash-safe audio manager with fallback sound synthesis
├── entities/
│   ├── entity.py            # Base physics object (velocity, delta-time, collision bounding box)
│   ├── player.py            # Player state machine (run, jump, dash, attack, combo finisher)
│   ├── projectile.py        # Alchemist toxic flasks & lingering hazard pools
│   └── dummy.py             # Practice dummy entity for hitbox verification
├── bosses/
│   ├── boss.py              # Base boss controller with phase transitions and health bars
│   ├── iron_vanguard.py     # Chapter 1 Boss: Greatsword cleave, jump slam, lightning trails
│   └── plague_alchemist.py  # Chapter 2 Boss: Teleport rifts, toxic flasks, potion barrage
├── assets/
│   ├── hero_aldric/         # Movement and attack animation frames for Aldric
│   ├── hero_seren/          # Movement and attack animation frames for Seren
│   ├── bosses/
│   │   ├── iron_vanguard/   # Sprite sheets & baked animation assets
│   │   └── alchemist/       # Sprite sheets & baked animation assets
│   ├── backgrounds/         # Multi-layer parallax backgrounds (forest, mountain crags)
│   └── audio/               # Background music ('the-tournament.mp3') and SFX
├── docs/
│   └── screenshots/         # High-resolution screenshots and visual assets
├── requirements.txt         # Package dependencies
└── README.md                # Project documentation
```

---

## 🎨 Art & Audio Pipeline

### Sprite Sheet Generation
- Boss animations originate as animated GIFs and are baked into transparent sprite sheets at `assets/bosses/*/*_sheet.png`.
- The original source GIFs are preserved adjacent to the sheets for rapid tweaking.
- Hero animation strips are partitioned into standard 64×64 and 96×96 pixel frame matrices in `assets/hero_*/`.

### Parallax Backgrounds
- The Thornwood and Cold Ascent use multiple independent background surfaces rendered at progressive scroll multipliers (`0.15x`, `0.35x`, and `0.70x`) relative to player movement.

### Crash-Safe Audio System
The audio manager wraps Pygame's mixer in try/except boundaries. If no audio output device is detected or if an audio asset is missing, the game falls back to visual audio ripples and continues running smoothly without raising an unhandled exception.

**Included Audio Cues:**
- **Hunt Theme**: `the-tournament.mp3`
- **Strike Confirmed**: `sword-slice.mp3`
- **Iron Vanguard Hit / Defeat**: `sword-slice-2.mp3` / `boss-defeat.mp3`
- **Alchemist Hit / Defeat**: `sword-attack-combo.mp3` / `defeated-sigh.mp3`

---

## 🔧 Troubleshooting & FAQ

### 1. `pygame.error: No available audio device` on Linux
On minimal Linux installations or WSL2, the ALSA or PulseAudio driver might be missing:
```bash
sudo apt-get install -y libasound2 libasound2-plugins pulseaudio
# Or set dummy driver to run silently:
export SDL_AUDIODRIVER=dummy
```

### 2. High-DPI Scaling Blurriness on Windows 10/11
If the pixel art appears blurry on 4K or high-DPI laptop screens, Grimslash includes automatic Windows DPI awareness in `settings.py`. You can also verify your display scaling settings:
```python
# Incorporated in main.py:
import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass
```

### 3. Apple Silicon (M1/M2/M3) Missing SDL2 Libraries
If you encounter `Library not loaded: @rpath/SDL2.framework` on macOS:
```bash
brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf
pip install --upgrade --force-reinstall pygame
```

### 4. Running Headless / Continuous Integration (CI)
To test imports and initialization in a CI environment (e.g., GitHub Actions) without a display server:
```bash
export SDL_VIDEODRIVER=dummy
export SDL_AUDIODRIVER=dummy
python -c "import pygame; pygame.init(); print('Pygame initialized successfully!')"
```

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details. Free for educational and personal use.

---

<div align="center">
  <sub>Forged with passion for pixel art and classic 2D action games. Created with Python & Pygame.</sub>
</div>
