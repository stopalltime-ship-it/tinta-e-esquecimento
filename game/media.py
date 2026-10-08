"""Carrega os assets enviados e prepara os quadros sem alterar os originais."""
import pygame
from .settings import ASSETS, WIDTH, HEIGHT, PAPER, TEAL, GOLD, RED


class Media:
    def __init__(self):
        image_dir=ASSETS/"images"
        self.scenes=[pygame.image.load(str(image_dir/name)).convert() for name in
                     ("conto_floresta.png","mapa_montanhas.png","ultima_pagina_ceu.png")]
        self.scaled={}
        sheet=pygame.image.load(str(image_dir/"classic_hero.png")).convert()
        # A spritesheet recebida tem fundo opaco. Só a cor de fundo vira transparente.
        background=tuple(sheet.get_at((0,0)))[:3]
        palette={(25,14,14):(14,30,45), (255,212,168):TEAL,
                 (239,150,98):(56,130,135), (62,154,218):(44,77,97),
                 (70,101,200):(28,48,72), (72,62,62):(32,55,70),
                 (255,255,235):PAPER, (255,206,21):GOLD,
                 (248,150,66):GOLD, (204,190,180):(158,189,174)}
        self.hero=[]
        for column in (1,2,3,4):
            frame=pygame.Surface((16,16),pygame.SRCALPHA)
            for y in range(16):
                for x in range(16):
                    color=tuple(sheet.get_at((column*16+x,16+y)))[:3]
                    if color != background:
                        frame.set_at((x,y),palette.get(color,color))
            self.hero.append(frame)
        self.hero_scaled={}

    def scene(self,index,size):
        key=(index,tuple(size))
        if key not in self.scaled:
            # Escala sem distorcer; o excedente fica recortado no centro.
            src=self.scenes[index]
            factor=max(size[0]/src.get_width(),size[1]/src.get_height())
            big=pygame.transform.scale(src,(round(src.get_width()*factor),round(src.get_height()*factor)))
            result=pygame.Surface(size)
            result.blit(big,((size[0]-big.get_width())//2,(size[1]-big.get_height())//2))
            self.scaled[key]=result
        return self.scaled[key]

    def hero_frame(self,index,size,flipped=False,hurt=False):
        key=(index,size,flipped,hurt)
        if key not in self.hero_scaled:
            image=pygame.transform.scale(self.hero[index],(size,size))
            if flipped: image=pygame.transform.flip(image,True,False)
            if hurt:
                silhouette=pygame.mask.from_surface(image).to_surface(setcolor=RED,unsetcolor=(0,0,0,0))
                image=silhouette.convert_alpha()
            self.hero_scaled[key]=image
        return self.hero_scaled[key]
