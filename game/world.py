"""Entidades e regras: movimento, colisões, tinta, pontes e combate."""
from dataclasses import dataclass, field
import math
import pygame

V = pygame.Vector2
ROOM = pygame.Rect(54, 182, 1044, 446)


@dataclass
class Actor:
    pos: V
    hp: float = 100
    radius: int = 15
    invulnerable: float = 0
    facing: V = field(default_factory=lambda: V(1, 0))
    moving: bool = False

    @property
    def rect(self):
        return pygame.Rect(round(self.pos.x - self.radius), round(self.pos.y - self.radius),
                           self.radius * 2, self.radius * 2)


@dataclass
class Enemy(Actor):
    speed: float = 70
    boss: bool = False
    shot_timer: float = 2


@dataclass
class Projectile:
    pos: V
    velocity: V
    friendly: bool
    ttl: float = 1.2
    damage: int = 28


class World:
    def __init__(self, chapter=0):
        self.chapter = chapter
        self.player = Actor(V(130, 407))
        self.ink = 100.0
        self.shield = 0.0
        self.cooldown = 0.0
        self.attack_flash = 0.0
        self.time = 0.0
        self.pages = []
        self.collected = 0
        self.projectiles = []
        self.effects = []
        self.story_written = False
        self.erase_timer = 7.0
        self.message = "Procure os fragmentos dourados. F: ler nos livros verdes."
        self.message_time = 5.0
        self.last_safe = self.player.pos.copy()
        self.portal = V(1040, 408)
        self.pedestal = V(575, 406)
        self.sources = [V(130, 545), V(590, 545), V(1010, 260)]
        self.source_cooldowns = [0., 0., 0.]
        self.obstacles = []
        self.gaps = []
        self.bridges = []  # Cada entrada: retângulo da ponte e segundos restantes.
        if chapter == 0:
            self.obstacles = [pygame.Rect(x, y, 155, 46) for x in (240, 510, 780) for y in (278, 475)]
            self.pages = [V(340, 235), V(665, 405), V(880, 568)]
            positions = [(390, 400), (690, 235), (910, 400)]
        elif chapter == 1:
            self.obstacles = [pygame.Rect(235, 270, 130, 45), pygame.Rect(560, 280, 110, 45),
                              pygame.Rect(890, 490, 120, 45)]
            self.gaps = [pygame.Rect(426, ROOM.top, 88, ROOM.height),
                         pygame.Rect(754, ROOM.top, 88, ROOM.height)]
            self.bridges = [[pygame.Rect(g.x - 18, 370, g.w + 36, 76), 0.] for g in self.gaps]
            self.pages = [V(290, 555), V(620, 230), V(940, 565)]
            positions = [(330, 415), (660, 430), (960, 330)]
        else:
            self.obstacles = [pygame.Rect(255, 290, 110, 44), pygame.Rect(770, 290, 110, 44)]
            self.pages = [V(220, 235), V(920, 565), V(610, 230)]
            positions = [(380, 530), (960, 400)]
        self.enemies = [Enemy(V(x, y), hp=48, speed=64 + chapter * 7) for x, y in positions]
        if chapter == 2:
            self.enemies.append(Enemy(V(870, 400), hp=210, radius=26, speed=43, boss=True))

    def tell(self, text, duration=3):
        self.message, self.message_time = text, duration

    def blocked(self, rect):
        if not ROOM.contains(rect) or any(rect.colliderect(o) for o in self.obstacles):
            return True
        for i, gap in enumerate(self.gaps):
            if rect.colliderect(gap):
                bridge, life = self.bridges[i]
                if life <= 0 or rect.top < bridge.top or rect.bottom > bridge.bottom:
                    return True
        return False

    def move(self, actor, delta):
        # Resolver cada eixo separadamente permite deslizar junto às estantes.
        for axis in (0, 1):
            previous = actor.pos[axis]
            actor.pos[axis] += delta[axis]
            if self.blocked(actor.rect):
                actor.pos[axis] = previous

    def hurt_player(self, damage):
        p = self.player
        if p.invulnerable > 0 or self.shield > 0:
            return False
        p.hp = max(0, p.hp - damage)
        p.invulnerable = 1.0
        return True

    def damage_enemy(self, enemy, amount):
        if enemy.boss and not self.story_written:
            self.tell("O Revisor está protegido. Reúna os fragmentos e escreva no círculo com F.")
            return
        enemy.hp -= amount
        enemy.invulnerable = .16

    def cast(self, spell):
        costs = {"slash": 6, "spear": 18, "shield": 24}
        if self.cooldown > 0:
            return False
        if self.ink < costs[spell]:
            self.tell("Falta tinta. Procure um livro verde e pressione F.")
            return False
        self.ink -= costs[spell]
        self.cooldown = .3 if spell == "slash" else .55
        if spell == "slash":
            self.attack_flash = .18
            for enemy in self.enemies:
                offset = enemy.pos - self.player.pos
                if offset.length() < 78 and (offset.length() < 22 or offset.normalize().dot(self.player.facing) > .15):
                    self.damage_enemy(enemy, 20)
        elif spell == "spear":
            self.projectiles.append(Projectile(self.player.pos.copy(), self.player.facing * 500, True))
        else:
            self.shield = 3.0
        return True

    def bridge(self):
        for rect, _ in self.bridges:
            if abs(self.player.pos.y - rect.centery) < 70 and abs(self.player.pos.x - rect.centerx) < 125:
                if self.ink < 20:
                    self.tell("A ponte precisa de 20 de tinta. Leia em um livro verde.")
                    return False
                index = next(i for i, b in enumerate(self.bridges) if b[0] == rect)
                self.bridges[index][1] = 8.
                self.ink -= 20
                self.tell("Ponte desenhada! Você tem 8 segundos para atravessar.")
                return True
        self.tell("Desenhe pontes nas bordas marcadas do Arquivo, usando B.")
        return False

    def interact(self):
        """Retorna um índice de leitura ou um evento de progressão."""
        p = self.player.pos
        if self.chapter == 2 and not self.story_written and p.distance_to(self.pedestal) < 66:
            if self.collected == 3:
                self.story_written = True
                self.ink = 100
                self.tell("A história permanece! A proteção do Revisor foi quebrada.", 6)
                return "story"
            self.tell("O círculo precisa dos três fragmentos da história.")
            return None
        for i, source in enumerate(self.sources):
            if p.distance_to(source) < 62:
                if self.source_cooldowns[i] > 0:
                    self.tell(f"Este livro recupera suas palavras em {math.ceil(self.source_cooldowns[i])} s.")
                    return None
                self.ink = min(100, self.ink + 65)
                self.player.hp = min(100, self.player.hp + 20)
                self.source_cooldowns[i] = 4.
                return i
        if self.chapter < 2 and p.distance_to(self.portal) < 65:
            if self.collected == 3:
                return "next"
            self.tell("Faltam fragmentos. Reúna os três antes de seguir.")
        else:
            self.tell("Aproxime-se de um livro verde, do portal ou do círculo para interagir.")
        return None

    def update(self, dt, movement):
        # Limitar dt evita atravessar paredes quando a janela perde desempenho.
        dt = min(dt, .04)
        self.time += dt
        self.cooldown = max(0, self.cooldown - dt)
        self.shield = max(0, self.shield - dt)
        self.attack_flash = max(0, self.attack_flash - dt)
        self.message_time = max(0, self.message_time - dt)
        self.player.invulnerable = max(0, self.player.invulnerable - dt)
        self.source_cooldowns = [max(0, c - dt) for c in self.source_cooldowns]
        movement = V(movement)
        self.player.moving = bool(movement.length_squared())
        if movement.length_squared():
            self.player.facing = movement.normalize()
            self.move(self.player, self.player.facing * 215 * dt)
        if not any(self.player.rect.colliderect(g) for g in self.gaps):
            self.last_safe = self.player.pos.copy()
        for bridge in self.bridges:
            bridge[1] = max(0, bridge[1] - dt)
        if self.blocked(self.player.rect):
            self.player.pos = self.last_safe.copy()
            self.hurt_player(15)
            self.tell("A ponte se apagou. Você voltou à margem; desenhe outra com B.")
        for page in self.pages[:]:
            if self.player.pos.distance_to(page) < 31:
                self.pages.remove(page)
                self.collected += 1
                self.ink = min(100, self.ink + 12)
                self.tell(f"Fragmento {self.collected}/3 recuperado.")
        for enemy in self.enemies[:]:
            if enemy.hp <= 0:
                self.enemies.remove(enemy)
                self.ink = min(100, self.ink + 8)
                continue
            enemy.invulnerable = max(0, enemy.invulnerable - dt)
            offset = self.player.pos - enemy.pos
            if offset.length() > 2:
                self.move(enemy, offset.normalize() * enemy.speed * dt)
            if offset.length() < enemy.radius + self.player.radius + 3:
                self.hurt_player(17 if enemy.boss else 12)
            if enemy.boss:
                enemy.shot_timer -= dt
                if enemy.shot_timer <= 0:
                    enemy.shot_timer = 1.7 if self.story_written else 2.5
                    direction = offset.normalize() if offset.length() else V(1, 0)
                    for angle in (-18, 0, 18):
                        self.projectiles.append(Projectile(enemy.pos.copy(), direction.rotate(angle) * 170, False, 4., 14))
        if self.chapter == 2:
            self.erase_timer -= dt
            if self.erase_timer <= 0:
                self.erase_timer = 7
                self.projectiles = [p for p in self.projectiles if not p.friendly]
                self.shield = 0
                self.tell("O Revisor apagou a lança e o escudo!" if not self.story_written else "O Revisor apaga os ataques, mas a história resiste.")
        for shot in self.projectiles[:]:
            shot.ttl -= dt
            shot.pos += shot.velocity * dt
            hit = shot.ttl <= 0 or not ROOM.collidepoint(shot.pos) or any(o.collidepoint(shot.pos) for o in self.obstacles)
            if shot.friendly:
                for enemy in self.enemies:
                    if shot.pos.distance_to(enemy.pos) < enemy.radius + 8:
                        self.damage_enemy(enemy, shot.damage)
                        hit = True
                        break
            elif shot.pos.distance_to(self.player.pos) < self.player.radius + 8:
                self.hurt_player(shot.damage)
                hit = True
            if hit:
                self.projectiles.remove(shot)
        if self.player.hp <= 0:
            return "defeat"
        if self.chapter == 2 and not any(e.boss and e.hp > 0 for e in self.enemies):
            return "name"
        return None
