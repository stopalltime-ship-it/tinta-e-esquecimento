"""Efeitos originais sintetizados em memória; nenhum download de áudio."""
from array import array
import math
import pygame


class Audio:
    def __init__(self):
        self.muted = False
        self.sounds = {}
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
        except pygame.error:
            pass  # O jogo continua funcionando em computadores sem dispositivo de áudio.

    def play(self, name):
        if not self.muted and name in self.sounds:
            self.sounds[name].play()
