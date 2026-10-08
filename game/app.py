"""Loop principal e máquina de estados das telas do jogo."""
import json
import pygame
from .settings import WIDTH, HEIGHT, FPS, TITLE, ASSETS, TEAL
from .world import World
from .render import Renderer
from .audio import Audio


class Game:
    def __init__(self):
        pygame.mixer.pre_init(22050,-16,1,512)
        pygame.init()
        self.screen=pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption(TITLE)
        icon=pygame.Surface((32,32),pygame.SRCALPHA)
        pygame.draw.circle(icon,TEAL,(16,17),13)
        pygame.display.set_icon(icon)
        self.renderer=Renderer(self.screen)
        self.audio=Audio()
        with (ASSETS / "story.json").open(encoding="utf-8") as f:
            self.chapters=json.load(f)["chapters"]
        self.world=World()
        self.state="menu"
        self.running=True
        self.selection=0
        self.clock=pygame.time.Clock()
        self.time=0
        self.reading=""
        self.signature=""

    def start_chapter(self, chapter):
        self.world=World(chapter)
        self.state="chapter"

    def event(self, event):
        if event.type == pygame.QUIT:
            self.running=False
            return
        if self.state == "name" and event.type == pygame.TEXTINPUT:
            self.signature += "".join(c for c in event.text if c.isprintable())
            self.signature=self.signature[:18]
            return
        if event.type == pygame.MOUSEBUTTONDOWN and self.state == "menu" and event.button == 1:
            for i in range(3):
                if pygame.Rect(80,431+i*49,345,40).collidepoint(event.pos):
                    self.selection=i
                    self.menu_action()
            return
        if event.type != pygame.KEYDOWN:
            return
        key=event.key
        if key == pygame.K_m and self.state != "name":
            self.audio.muted=not self.audio.muted
            self.world.tell("Som desligado." if self.audio.muted else "Som ligado.")
            return
        if self.state == "menu":
            if key in (pygame.K_DOWN,pygame.K_s): self.selection=(self.selection+1)%3
            if key in (pygame.K_UP,pygame.K_w): self.selection=(self.selection-1)%3
            if key in (pygame.K_RETURN,pygame.K_SPACE): self.menu_action()
            if key == pygame.K_ESCAPE: self.running=False
        elif self.state == "play":
            if key == pygame.K_ESCAPE: self.state="pause"
            elif key in (pygame.K_SPACE,pygame.K_q,pygame.K_e):
                spell={pygame.K_SPACE:"slash",pygame.K_q:"spear",pygame.K_e:"shield"}[key]
                if self.world.cast(spell): self.audio.play("ink" if spell == "slash" else "spell")
            elif key == pygame.K_b:
                if self.world.bridge(): self.audio.play("spell")
            elif key == pygame.K_f:
                result=self.world.interact()
                if isinstance(result,int):
                    self.reading=self.chapters[self.world.chapter]["verses"][result]
                    self.state="reading"
                    self.audio.play("page")
                elif result == "next": self.start_chapter(self.world.chapter+1)
                elif result == "story": self.audio.play("page")
        elif self.state == "pause":
            if key in (pygame.K_ESCAPE,pygame.K_RETURN): self.state="play"
            elif key == pygame.K_r: self.start_chapter(self.world.chapter)
            elif key == pygame.K_BACKSPACE: self.state="menu"
        elif self.state in ("chapter","reading"):
            if key in (pygame.K_RETURN,pygame.K_SPACE,pygame.K_ESCAPE): self.state="play"
        elif self.state == "defeat":
            if key in (pygame.K_RETURN,pygame.K_r): self.start_chapter(self.world.chapter)
            elif key == pygame.K_ESCAPE: self.state="menu"
        elif self.state == "name":
            if key == pygame.K_BACKSPACE: self.signature=self.signature[:-1]
            elif key == pygame.K_RETURN:
                pygame.key.stop_text_input()
                self.signature=self.signature.strip() or "Ilo"
                self.state="ending"
        elif self.state in ("credits","ending"):
            if key in (pygame.K_RETURN,pygame.K_ESCAPE): self.state="menu"

    def menu_action(self):
        if self.selection == 0: self.start_chapter(0)
        elif self.selection == 1: self.state="credits"
        else: self.running=False

    def update(self, dt, movement=None):
        self.time+=dt
        if self.state != "play": return
        if movement is None:
            keys=pygame.key.get_pressed()
            movement=(int(keys[pygame.K_d] or keys[pygame.K_RIGHT])-int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
                      int(keys[pygame.K_s] or keys[pygame.K_DOWN])-int(keys[pygame.K_w] or keys[pygame.K_UP]))
        before_hp,before_pages=self.world.player.hp,self.world.collected
        result=self.world.update(dt,movement)
        if self.world.player.hp < before_hp: self.audio.play("hurt")
        if self.world.collected > before_pages: self.audio.play("page")
        if result:
            self.state=result
            if result == "name":
                self.signature=""
                pygame.key.start_text_input()

    def draw(self):
        r=self.renderer
        if self.state in ("menu","credits"):
            r.menu(self.time,self.selection)
            if self.state == "credits":
                r.overlay("Feito de palavras e tinta", "Conceito e história: Emerson. Demo desenvolvida com assistência de IA. Arte geométrica e efeitos sonoros criados em código para este projeto. Python + Pygame. Consulte CREDITOS.md para detalhes.","ENTER  Voltar ao menu", "CRÉDITOS")
        elif self.state == "ending": r.ending(self.signature,self.time)
        else:
            chapter=self.chapters[self.world.chapter]
            r.game(self.world,chapter)
            if self.state == "chapter":
                r.overlay(chapter["title"],chapter["intro"],"ENTER  Começar",f"CAPÍTULO {self.world.chapter+1:02d} · {chapter['subtitle']}")
            elif self.state == "pause":
                r.overlay("A história espera por você.","O tempo está parado. Volte quando estiver pronto para continuar escrevendo.","ENTER  Continuar    R  Reiniciar fase    BACKSPACE  Menu","PAUSA")
            elif self.state == "reading":
                r.overlay("As palavras voltam a respirar.",self.reading,"ENTER  Continuar   ·   +65 tinta / +20 vida (até o limite)","LEITURA · O TEMPO ESTÁ PAUSADO")
            elif self.state == "defeat":
                r.overlay("Ainda não é o fim.","O Vazio alcançou Ilo, mas a história pode ser reescrita. Leia para recuperar vida e tinta. Use o escudo para atravessar o perigo.","ENTER  Tentar esta fase novamente    ESC  Menu","PÁGINA APAGADA")
            elif self.state == "name":
                r.overlay("Assine a última página.","A história completa resistiu ao Revisor. Escreva seu nome para que a biblioteca se lembre de quem a salvou.", "ENTER  Concluir   ·   Até 18 caracteres; vazio usa Ilo", "O VAZIO RECUOU")
                r.panel(pygame.Rect(260,428,630,48))
                r.text((self.signature or "_")+" |",280,439,34,TEAL)
        pygame.display.flip()

    def run(self, frames=None, screenshot=None):
        count=0
        while self.running:
            dt=self.clock.tick(FPS)/1000
            for event in pygame.event.get(): self.event(event)
            self.update(dt)
            self.draw()
            count+=1
            if frames and count >= frames: break
        if screenshot:
            pygame.image.save(self.screen,str(screenshot))
        pygame.quit()
