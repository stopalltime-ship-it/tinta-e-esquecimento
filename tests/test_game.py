"""Testes de regras críticas; sem janela ou dispositivo de áudio reais."""
import os
os.environ["SDL_VIDEODRIVER"]="dummy"
os.environ["SDL_AUDIODRIVER"]="dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"]="1"
from collections import deque
import unittest
import pygame
from game.world import World, V, ROOM
from game.app import Game


class Rules(unittest.TestCase):
    def test_walls_and_obstacles_block_movement(self):
        w=World()
        w.player.pos=V(210,300)
        for _ in range(90): w.update(1/60,(1,0))
        self.assertLessEqual(w.player.rect.right,240)
        w.player.pos=V(80,220)
        for _ in range(60): w.update(1/60,(-1,0))
        self.assertTrue(ROOM.contains(w.player.rect))

    def test_diagonal_speed_is_normalized(self):
        a,b=World(),World()
        origin=a.player.pos.copy()
        a.update(.03,(1,0));b.update(.03,(1,1))
        self.assertAlmostEqual(a.player.pos.distance_to(origin),b.player.pos.distance_to(origin))

    def test_no_spell_without_ink_or_during_cooldown(self):
        w=World();w.ink=5
        self.assertFalse(w.cast("slash"));self.assertEqual(w.ink,5)
        w.ink=100
        self.assertTrue(w.cast("spear"));self.assertEqual(w.ink,82)
        self.assertFalse(w.cast("spear"));self.assertEqual(w.ink,82)

    def test_reading_recovers_resources_and_has_cooldown(self):
        w=World();w.player.pos=w.sources[0].copy();w.ink=0;w.player.hp=40
        self.assertEqual(w.interact(),0)
        self.assertEqual((w.ink,w.player.hp),(65,60))
        self.assertIsNone(w.interact())
        w.enemies=[]
        for _ in range(250): w.update(1/60,(0,0))
        self.assertEqual(w.interact(),0)
        self.assertEqual(w.ink,100)

    def test_shield_and_damage_grace_period(self):
        w=World();w.cast("shield")
        self.assertFalse(w.hurt_player(20))
        w.shield=0
        self.assertTrue(w.hurt_player(20));self.assertFalse(w.hurt_player(20))
        self.assertEqual(w.player.hp,80)

    def test_bridge_blocks_opens_and_returns_player_on_expiry(self):
        w=World(1);w.enemies=[];w.player.pos=V(390,407)
        for _ in range(30): w.update(1/60,(1,0))
        self.assertLessEqual(w.player.rect.right,426)
        self.assertTrue(w.bridge());self.assertEqual(w.ink,80)
        for _ in range(17): w.update(1/60,(1,0))
        self.assertTrue(w.player.rect.colliderect(w.gaps[0]))
        w.bridges[0][1]=.001;w.update(.02,(0,0))
        self.assertFalse(w.blocked(w.player.rect));self.assertEqual(w.player.hp,85)
        w.ink=19
        self.assertFalse(w.bridge())

    def test_portal_requires_all_fragments(self):
        w=World();w.enemies=[];w.player.pos=w.portal.copy()
        self.assertIsNone(w.interact())
        for pos in w.pages[:]:
            w.player.pos=pos.copy();w.update(.01,(0,0))
        self.assertEqual(w.collected,3)
        w.player.pos=w.portal.copy()
        self.assertEqual(w.interact(),"next")

    def test_boss_story_and_victory(self):
        w=World(2);boss=next(e for e in w.enemies if e.boss)
        w.damage_enemy(boss,50);self.assertEqual(boss.hp,210)
        w.player.pos=w.pedestal.copy()
        self.assertIsNone(w.interact())
        for p in w.pages[:]:
            w.player.pos=p.copy();w.update(.01,(0,0))
        w.player.pos=w.pedestal.copy()
        self.assertEqual(w.interact(),"story")
        w.damage_enemy(boss,210)
        self.assertEqual(w.update(.01,(0,0)),"name")

    def test_projectiles_and_eraser(self):
        w=World(2);w.cast("spear");w.shield=2;w.erase_timer=.001
        w.update(.02,(0,0))
        self.assertFalse(any(p.friendly for p in w.projectiles));self.assertEqual(w.shield,0)
        w=World();w.enemies=w.enemies[:1];enemy=w.enemies[0]
        enemy.pos=V(190,407);enemy.speed=0
        w.cast("spear")
        for _ in range(12): w.update(1/60,(0,0))
        self.assertEqual(enemy.hp,20)

    def test_defeat(self):
        w=World();w.player.hp=1;w.hurt_player(12)
        self.assertEqual(w.update(.01,(0,0)),"defeat")

    def test_all_pages_and_portals_reachable_with_open_bridges(self):
        # Flood fill do espaço caminhável, incluindo a largura do personagem.
        for chapter in range(3):
            w=World(chapter)
            for bridge in w.bridges: bridge[1]=8
            start=(130,407);queue=deque([start]);visited={start}
            while queue:
                x,y=queue.popleft()
                for dx,dy in ((10,0),(-10,0),(0,10),(0,-10)):
                    point=(x+dx,y+dy)
                    if point not in visited and not w.blocked(pygame.Rect(point[0]-15,point[1]-15,30,30)):
                        visited.add(point);queue.append(point)
            for target in w.pages+w.sources+([w.portal] if chapter < 2 else [w.pedestal]):
                self.assertTrue(any(V(p).distance_to(target)<25 for p in visited),(chapter,target))


class Screens(unittest.TestCase):
    def setUp(self): self.game=Game()
    def tearDown(self): pygame.quit()
    def press(self,key): self.game.event(pygame.event.Event(pygame.KEYDOWN,key=key))

    def test_menu_pause_reading_and_retry(self):
        g=self.game;self.press(pygame.K_RETURN);self.assertEqual(g.state,"chapter")
        self.press(pygame.K_RETURN);self.assertEqual(g.state,"play")
        self.press(pygame.K_ESCAPE);self.assertEqual(g.state,"pause")
        old=g.world.time;g.update(.5,(1,0));self.assertEqual(g.world.time,old)
        self.press(pygame.K_RETURN);g.world.player.pos=g.world.sources[0].copy()
        self.press(pygame.K_f);self.assertEqual(g.state,"reading")
        g.update(.5,(1,0));self.assertEqual(g.world.time,old)
        self.press(pygame.K_RETURN);g.world.player.hp=0;g.update(.01,(0,0))
        self.assertEqual(g.state,"defeat");self.press(pygame.K_RETURN)
        self.assertEqual(g.state,"chapter");self.assertEqual(g.world.player.hp,100)

    def test_progression_and_signature(self):
        g=self.game
        for chapter in (0,1):
            g.start_chapter(chapter);g.state="play";g.world.collected=3
            g.world.player.pos=g.world.portal.copy();self.press(pygame.K_f)
            self.assertEqual(g.world.chapter,chapter+1)
        g.state="play";g.world.story_written=True
        for e in g.world.enemies:
            if e.boss: e.hp=0
        g.update(.01,(0,0));self.assertEqual(g.state,"name")
        g.event(pygame.event.Event(pygame.TEXTINPUT,text="Emerson"))
        self.press(pygame.K_RETURN);self.assertEqual(g.state,"ending")
        self.assertEqual(g.signature,"Emerson")
        self.press(pygame.K_RETURN);self.assertEqual(g.state,"menu")

    def test_every_screen_renders(self):
        g=self.game
        for chapter in range(3):
            g.start_chapter(chapter)
            for state in ("chapter","play","pause","reading","defeat","name","ending","credits"):
                g.state=state;g.draw()

    def test_imported_sprite_transparency_and_animation(self):
        media=self.game.renderer.media
        for frame in media.hero:
            self.assertEqual(frame.get_at((0,0)).a,0)
            self.assertGreater(pygame.mask.from_surface(frame).count(),20)
        self.assertNotEqual(pygame.image.tobytes(media.hero[1],'RGBA'),
                            pygame.image.tobytes(media.hero[2],'RGBA'))
        self.assertEqual(media.hero_frame(0,48,True).get_size(),(48,48))

    def test_imported_audio_decodes_and_mutes(self):
        audio=self.game.audio
        self.assertGreater(audio.sounds['confirm'].get_length(),.1)
        for chapter in range(3):
            audio.ambience(chapter)
            self.assertTrue(pygame.mixer.music.get_busy())
        audio.toggle()
        self.assertEqual(pygame.mixer.music.get_volume(),0)
        audio.ambience(1,paused=True)
        self.assertEqual(pygame.mixer.music.get_volume(),0)
        audio.toggle()
        self.assertGreater(pygame.mixer.music.get_volume(),0)


if __name__ == "__main__": unittest.main()
