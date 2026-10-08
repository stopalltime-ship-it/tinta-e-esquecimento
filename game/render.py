"""Arte procedural original: biblioteca, livros, criatura de tinta e interface."""
import math
import random
import pygame
from .settings import WIDTH, HEIGHT, BG, PAPER, MUTED, GOLD, TEAL, RED
from .world import ROOM


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.fonts = {size: pygame.font.Font(None, size) for size in (17, 19, 21, 24, 28, 34, 42, 64, 86)}
        self.rng = random.Random(12)
        self.dust = [(self.rng.randrange(WIDTH), self.rng.randrange(HEIGHT), self.rng.uniform(.3, 1)) for _ in range(60)]

    def text(self, text, x, y, size=24, color=PAPER, center=False):
        surface = self.fonts[size].render(text, True, color)
        self.screen.blit(surface, surface.get_rect(center=(x, y)) if center else (x, y))

    def wrap(self, text, rect, size=28, color=PAPER, line_height=34):
        words, line, y = text.split(), "", rect.y
        for word in words:
            trial = (line + " " + word).strip()
            if self.fonts[size].size(trial)[0] > rect.w and line:
                self.text(line, rect.x, y, size, color)
                y += line_height
                line = word
            else:
                line = trial
        if line:
            self.text(line, rect.x, y, size, color)
        return y + line_height

    def panel(self, rect, color=(25, 36, 47), border=(61, 74, 81), radius=12):
        pygame.draw.rect(self.screen, color, rect, border_radius=radius)
        pygame.draw.rect(self.screen, border, rect, 1, border_radius=radius)

    def background(self, t):
        self.screen.fill(BG)
        for x, y, speed in self.dust:
            pygame.draw.circle(self.screen, (49, 65, 72), (int((x + t * speed * 7) % WIDTH), int((y - t * speed * 5) % HEIGHT)), 1)
        pygame.draw.rect(self.screen, (42, 55, 64), (24, 24, WIDTH - 48, HEIGHT - 48), 1, border_radius=4)

    def book(self, x, y, scale=1, color=GOLD, opened=True):
        s = scale
        pts = [(x - 20*s, y - 11*s), (x - 3*s, y - 7*s), (x, y - 3*s),
               (x + 3*s, y - 7*s), (x + 20*s, y - 11*s), (x + 20*s, y + 12*s),
               (x + 3*s, y + 16*s), (x, y + 19*s), (x - 3*s, y + 16*s), (x - 20*s, y + 12*s)]
        pygame.draw.polygon(self.screen, (9, 19, 27), [(a, b + 4*s) for a, b in pts])
        pygame.draw.polygon(self.screen, color, pts)
        pygame.draw.line(self.screen, (73, 73, 66), (x, y - 2*s), (x, y + 15*s), max(1, int(s)))
        for i in range(3):
            yy = y + (i * 5 - 3) * s
            pygame.draw.line(self.screen, (121, 126, 112), (x - 16*s, yy), (x - 5*s, yy + 3*s), max(1, int(s)))
            pygame.draw.line(self.screen, (121, 126, 112), (x + 5*s, yy + 3*s), (x + 16*s, yy), max(1, int(s)))

    def ilo(self, x, y, t, scale=1, hurt=False):
        bob = math.sin(t * 5) * 2 * scale
        pygame.draw.ellipse(self.screen, (13, 21, 28), (x-20*scale, y+13*scale, 40*scale, 10*scale))
        c = RED if hurt else (30, 53, 66)
        pygame.draw.ellipse(self.screen, TEAL, (x-16*scale, y-20*scale+bob, 32*scale, 38*scale))
        pygame.draw.ellipse(self.screen, c, (x-14*scale, y-19*scale+bob, 28*scale, 35*scale))
        pygame.draw.polygon(self.screen, c, [(x-10*scale,y-10*scale+bob),(x+3*scale,y-35*scale+bob),(x+10*scale,y-9*scale+bob)])
        for dx in (-5, 5):
            pygame.draw.ellipse(self.screen, PAPER, (x+dx*scale-2*scale,y-5*scale+bob,4*scale,7*scale))
        pygame.draw.line(self.screen, GOLD, (x+13*scale, y+7*scale), (x+30*scale,y-18*scale), max(2,int(2*scale)))
        pygame.draw.polygon(self.screen, PAPER, [(x+28*scale,y-14*scale),(x+38*scale,y-28*scale),(x+29*scale,y-23*scale)])

    def shelf(self, rect, seed=0):
        x, y, w, h = rect
        pygame.draw.rect(self.screen, (15, 21, 28), (x+5, y+7, w, h), border_radius=3)
        pygame.draw.rect(self.screen, (89, 70, 61), rect, border_radius=3)
        pygame.draw.rect(self.screen, (37, 38, 40), (x+5, y+5, w-10, h-12))
        colors = [(146,105,83),(71,111,111),(167,139,92),(103,96,127),(109,124,106)]
        for i in range((w-14)//12):
            height = 22 + ((i*7 + seed) % 10)
            xx = x+8+i*12
            pygame.draw.rect(self.screen, colors[(i+seed)%len(colors)], (xx, y+h-8-height, 9, height), border_radius=1)
            pygame.draw.line(self.screen, (199,173,123), (xx+2, y+h-14), (xx+6,y+h-14))
        pygame.draw.line(self.screen, (171,137,95), (x+1,y+h-5), (x+w-2,y+h-5), 3)

    def menu(self, t, selection):
        self.background(t)
        self.text("UM RPG SOBRE O QUE PERMANECE", 80, 94, 19, TEAL)
        self.text("Tinta e", 76, 148, 86)
        self.text("Esquecimento", 76, 217, 86, GOLD)
        self.wrap("Quando o mundo vira uma página em branco, um pequeno risco pode mudar o final.", pygame.Rect(80,315,490,90), 28, MUTED)
        for i, label in enumerate(("Começar a história", "Créditos", "Sair")):
            rect = pygame.Rect(80, 431+i*49, 345, 40)
            self.panel(rect, (47,74,76) if selection == i else (24,34,44), TEAL if selection == i else (42,55,64), 5)
            self.text(label, 103, rect.y+9, 28)
            if selection == i:
                self.text("›", 396, rect.y+7, 28, TEAL)
        pygame.draw.circle(self.screen, (27,39,48), (846,300), 181)
        pygame.draw.circle(self.screen, (58,75,78), (846,300), 179, 1)
        self.book(847, 396, 6.1, PAPER)
        self.ilo(839, 305, t, 3.1)
        self.text("ILO", 846, 133, 19, TEAL, True)
        self.text("Três capítulos · Uma última página", 847, 555, 24, MUTED, True)
        self.text("WASD / setas: mover   •   Espaço: rabisco   •   Q: lança   •   E: escudo", 80, 618, 21, PAPER)
        self.text("F: ler / interagir   •   B: ponte   •   Esc: pausa   •   M: som   •   Enter: selecionar", 80, 648, 21, MUTED)

    def game(self, world, chapter):
        w = world
        self.background(w.time)
        self.text(f"CAPÍTULO {w.chapter+1:02d} / 03", 55, 46, 19, TEAL)
        self.text(chapter["title"], 54, 74, 42)
        self.text(f"FRAGMENTOS  {w.collected} / 3", 846, 53, 24, GOLD)
        self.text("MOVER  WASD / SETAS", 846, 85, 19, MUTED)
        self.bar(55,130,215,w.player.hp,RED,"VIDA")
        self.bar(300,130,215,w.ink,TEAL,"TINTA")
        objective = "Reúna os fragmentos e alcance o livro à direita."
        if w.chapter == 2:
            objective = "Enfrente O Revisor!" if w.story_written else "3 fragmentos + F no círculo central"
        self.text(objective, 552, 139, 21, GOLD)
        pygame.draw.rect(self.screen, (43,49,52), ROOM, border_radius=8)
        for y in range(ROOM.y, ROOM.bottom, 32):
            for x in range(ROOM.x, ROOM.right, 64):
                shade = 44 + ((x*13+y*7)//32 % 3)*3
                pygame.draw.rect(self.screen, (shade,shade+6,shade+7), (x+1,y+1,min(62,ROOM.right-x-1), min(30,ROOM.bottom-y-1)))
        pygame.draw.rect(self.screen, (110,99,79), ROOM, 3, border_radius=8)
        for i, gap in enumerate(w.gaps):
            pygame.draw.rect(self.screen, (211,216,204), gap)
            for j in range(17):
                yy = ROOM.y + j*28
                xx = gap.x+int(9*math.sin(w.time+j))
                pygame.draw.line(self.screen,(237,232,215),(xx,yy),(xx+gap.w,yy+8),3)
            bridge, remaining = w.bridges[i]
            if remaining > 0:
                pygame.draw.rect(self.screen,(43,88,92),bridge)
                for x in range(bridge.x+3,bridge.right,13):
                    pygame.draw.line(self.screen,TEAL,(x,bridge.y+4),(x+3,bridge.bottom-4),2)
                self.text(f"{remaining:.1f}s",bridge.centerx,bridge.y-17,21,TEAL,True)
            else:
                for xx in (gap.x-28,gap.right+28):
                    pygame.draw.circle(self.screen,GOLD,(xx,408),15,1)
                    self.text("B",xx,408,21,GOLD,True)
        if w.chapter == 2:
            color = TEAL if w.story_written else (111,106,91)
            pygame.draw.circle(self.screen,color,w.pedestal,52,2)
            pygame.draw.circle(self.screen,color,w.pedestal,44,1)
            self.book(*w.pedestal,1.2,color)
            self.text("HISTÓRIA" if w.story_written else "F · ESCREVER",575,467,19,color,True)
        for i, source in enumerate(w.sources):
            color = TEAL if w.source_cooldowns[i] <= 0 else MUTED
            pygame.draw.circle(self.screen,(40,68,67),source,29)
            self.book(*source,.85,color)
            self.text("F · LER",source.x,source.y+39,17,color,True)
        for i, obstacle in enumerate(w.obstacles):
            self.shelf(obstacle,i)
        if w.chapter < 2:
            pygame.draw.circle(self.screen,(67,70,58),w.portal,35)
            self.book(*w.portal,1.2,GOLD if w.collected == 3 else MUTED)
            self.text("F · SEGUIR",w.portal.x,w.portal.y+49,17,GOLD,True)
        for page in w.pages:
            yy = page.y + math.sin(w.time*3+page.x)*4
            pygame.draw.circle(self.screen,(84,78,55),(page.x,yy),19)
            pygame.draw.polygon(self.screen,GOLD,[(page.x-8,yy-12),(page.x+8,yy-12),(page.x+8,yy+12),(page.x-8,yy+12)])
            for off in (-5,0,5):
                pygame.draw.line(self.screen,(127,99,64),(page.x-4,yy+off),(page.x+4,yy+off),1)
        for enemy in sorted(w.enemies,key=lambda e:e.pos.y):
            x,y = enemy.pos
            size = 27 if enemy.boss else 16
            pygame.draw.ellipse(self.screen,(20,28,35),(x-size,y+size-5,size*2,12))
            color = PAPER if enemy.invulnerable else (188,196,184)
            pygame.draw.polygon(self.screen,color,[(x-size,y+size),(x-size*.7,y-size),(x,y-size-9),(x+size*.7,y-size),(x+size,y+size),(x+5,y+size-5),(x,y+size),(x-6,y+size-5)])
            pygame.draw.line(self.screen,(62,72,72),(x-8,y-6),(x-3,y-3),3)
            pygame.draw.line(self.screen,(62,72,72),(x+3,y-3),(x+8,y-6),3)
            if enemy.boss:
                if not w.story_written:
                    pygame.draw.circle(self.screen,GOLD,(x,y),38,2)
                self.text("O REVISOR",x,y-53,19,GOLD,True)
                pygame.draw.rect(self.screen,(37,40,42),(x-42,y+39,84,5))
                pygame.draw.rect(self.screen,RED,(x-42,y+39,84*max(0,enemy.hp)/210,5))
        p=w.player
        self.ilo(*p.pos,w.time,hurt=p.invulnerable > 0 and int(w.time*12)%2 == 0)
        if w.shield > 0:
            pygame.draw.circle(self.screen,TEAL,p.pos,34,2)
            self.text(f"{w.shield:.1f}",p.pos.x,p.pos.y-49,17,TEAL,True)
        if w.attack_flash > 0:
            angle = math.atan2(-p.facing.y,p.facing.x)
            pygame.draw.arc(self.screen,TEAL,(p.pos.x-65,p.pos.y-65,130,130),angle-.8,angle+.8,5)
        for shot in w.projectiles:
            color = TEAL if shot.friendly else PAPER
            tip = shot.pos + shot.velocity.normalize()*15
            pygame.draw.line(self.screen,color,shot.pos,tip,4)
            pygame.draw.circle(self.screen,color,tip,4)
        if w.message_time > 0:
            self.panel(pygame.Rect(90,593,970,30),(24,34,43),(61,74,81),5)
            self.text(w.message,575,608,19,PAPER,True)
        self.text("ESPAÇO  Rabisco · 6     Q  Lança · 18     E  Escudo · 24     B  Ponte · 20",55,651,21,TEAL)
        self.text("F  Interagir     ESC  Pausa     M  Som",55,679,19,MUTED)
        self.text("TINTA E ESQUECIMENTO",917,679,17,GOLD)

    def bar(self,x,y,width,value,color,label):
        self.text(label,x,y-15,17,MUTED)
        pygame.draw.rect(self.screen,(26,33,40),(x,y+6,width,10),border_radius=5)
        pygame.draw.rect(self.screen,color,(x,y+6,width*max(0,value)/100,10),border_radius=5)
        self.text(str(int(value)),x+width+8,y,19,color)

    def overlay(self, title, body, footer, eyebrow="UMA PAUSA ENTRE AS PÁGINAS"):
        shade=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        shade.fill((8,15,23,215))
        self.screen.blit(shade,(0,0))
        self.panel(pygame.Rect(220,187,712,360),(25,36,46),(119,108,85),10)
        self.text(eyebrow,260,222,19,TEAL)
        self.text(title,260,258,42,GOLD)
        self.wrap(body,pygame.Rect(260,321,630,160),28,PAPER,33)
        self.text(footer,260,505,21,TEAL)

    def ending(self, name, t):
        self.background(t)
        self.text("CAPÍTULO FINALIZADO",WIDTH//2,92,21,TEAL,True)
        self.text("Toda história merece ser lembrada.",WIDTH//2,158,42,PAPER,True)
        self.book(WIDTH//2,350,6,PAPER)
        self.text(name or "Ilo",WIDTH//2,488,42,GOLD,True)
        self.text("A biblioteca foi salva. Ilo tornou-se uma história.",WIDTH//2,553,28,PAPER,True)
        self.text("E, em algum lugar, alguém começou a ler.",WIDTH//2,590,24,MUTED,True)
        self.text("ENTER  Voltar ao menu",WIDTH//2,655,21,TEAL,True)
