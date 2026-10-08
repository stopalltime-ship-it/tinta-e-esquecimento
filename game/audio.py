"""Efeitos sintetizados e sons enviados, com créditos em CREDITOS.md."""
from array import array
import math
import pygame
from .settings import ASSETS


class Audio:
    def __init__(self):
        self.muted = False
        self.sounds = {}
        self.current_ambience = None
        self.ambience_volume = .14
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1)
            for name, freq, length in [("ink", 240, .12), ("page", 620, .3),
                                       ("hurt", 100, .18), ("spell", 420, .22)]:
                samples = array("h")
                for i in range(int(22050 * length)):
                    t = i / 22050
                    envelope = (1 - t / length) ** 2 * min(1, t / .01)
                    samples.append(int(5000 * envelope * math.sin(2 * math.pi * freq * t)))
                self.sounds[name] = pygame.mixer.Sound(buffer=samples)
            self.sounds['confirm']=pygame.mixer.Sound(str(ASSETS/'audio/menu_confirm.wav'))
            self.sounds['confirm'].set_volume(.45)
        except pygame.error:
            pass  # O jogo continua funcionando em computadores sem dispositivo de áudio.

    def play(self, name):
        if not self.muted and name in self.sounds:
            self.sounds[name].play()

    def toggle(self):
        self.muted=not self.muted
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(0 if self.muted else self.ambience_volume)
            if self.muted: pygame.mixer.stop()

    def ambience(self,chapter,paused=False):
        if not pygame.mixer.get_init(): return
        filename=('ambiente_contos.ogg','ambiente_mapas.ogg','sinos_revisor.ogg')[chapter]
        if filename != self.current_ambience:
            pygame.mixer.music.load(str(ASSETS/'audio'/filename))
            pygame.mixer.music.play(-1,fade_ms=600)
            self.current_ambience=filename
        self.ambience_volume=.055 if paused else .14
        pygame.mixer.music.set_volume(0 if self.muted else self.ambience_volume)
