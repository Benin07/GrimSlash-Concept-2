import os
import pygame

from settings import resolve_path


class AudioManager:
    """
    Crash-safe sound/music manager. Sound hooks can use .wav, .ogg, or .mp3
    files in assets/audio/sfx/ (or assets/audio/music/ for music). Missing
    files are silently swallowed so the game never dies on an audio typo.
    """

    EXTENSIONS = (".wav", ".ogg", ".mp3")

    def __init__(self, sfx_dir="assets/audio/sfx",
                 music_dir="assets/audio/music"):
        self.sfx_dir = sfx_dir
        self.music_dir = music_dir
        self._cache = {}
        self.enabled = True
        try:
            pygame.mixer.init()
        except pygame.error:
            self.enabled = False
            print("[Audio] mixer unavailable -- running silent.")

    @staticmethod
    def _asset_path(directory, name):
        """Return the first supported asset matching a hook name."""
        for extension in AudioManager.EXTENSIONS:
            path = resolve_path(os.path.join(directory, f"{name}{extension}"))
            if os.path.isfile(path):
                return path
        return None

    def _load(self, name):
        if name in self._cache:
            return self._cache[name]
        try:
            path = self._asset_path(self.sfx_dir, name)
            if path is None:
                raise FileNotFoundError(name)
            snd = pygame.mixer.Sound(path)
            self._cache[name] = snd
            return snd
        except (pygame.error, FileNotFoundError):
            self._cache[name] = None
            return None

    def play_sound(self, name, volume=1.0):
        if not self.enabled:
            return
        try:
            snd = self._load(name)
            if snd is not None:
                snd.set_volume(volume)
                snd.play()
        except pygame.error:
            pass

    def play_music(self, name, loops=-1, volume=0.6):
        if not self.enabled:
            return
        try:
            path = self._asset_path(self.music_dir, name)
            if path is None:
                raise FileNotFoundError(name)
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
        except (pygame.error, FileNotFoundError):
            pass

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass
