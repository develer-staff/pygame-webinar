#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random

import pygame as pg

from settings import *

from assets import Tileset
from entities import Entity, Player, Enemy, Wall, Attack


class State:

    def __init__(self, game):
        self.game = game
        self.screen = pg.Surface(VIEW_RES)

    def process_event(self, event, dt):
        """
        Processa un evento.
        """
        pass

    def update(self, dt):
        """
        Applica le logiche per aggiornare lo stato.
        """
        pass

    def draw(self):
        """
        Disegna su self.screen.
        """
        pass


class World(State):

    world_map = ["WWWWWWWWWWWWWWWW",
                 "WWWWWWW WWWWWWWW",
                 "WW       WW   WW",
                 "W  W W P    W EW",
                 "   E            ",
                 "   W W     EW   ",
                 "                ",
                 "W  W W      W  W",
                 "WW    E  WW   WW",
                 "WWWWWWW  WWWWWWW",
                 "WWWWWWW  WWWWWWW"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_sounds()
        self.new_game()

    def _init_sounds(self):
        self._attack_sound = pg.mixer.Sound(SOUNDS / "Attack.wav")
        self._enemy_hit_sound = pg.mixer.Sound(SOUNDS / "EnemyHit.wav")
        self._player_hit_sound = pg.mixer.Sound(SOUNDS / "PlayerHit.wav")
        self._game_over_sound = pg.mixer.Sound(SOUNDS / "GameOver.wav")

    def new_game(self):
        self._init_groups()
        self._init_world()
        self._start_bg_music()

    def _start_bg_music(self):
        pg.mixer.music.load(SOUNDS / "theme.ogg")
        pg.mixer.music.set_volume(.4)
        pg.mixer.music.play(loops=-1)

    def _init_groups(self):
        self.visible_entities = pg.sprite.Group()
        self.environment = pg.sprite.Group()
        self.actors = pg.sprite.Group()
        self.player_group = pg.sprite.GroupSingle()
        self.enemies = pg.sprite.Group()
        self.attacks = pg.sprite.Group()

    def _init_world(self):
        """
        Crea la mappa del mondo.
        """
        # Creiamo le surface per lo sfondo.
        grass_tiles = Tileset(IMAGES / "grass_tileset.png", TILESIZE).images_at_row(0)

        world_x = SCREEN_TILES[0] * TILESIZE
        world_y = SCREEN_TILES[1] * TILESIZE
        self.world = pg.Surface((world_x, world_y))
        self.background = pg.Surface((world_x, world_y))

        players = 0
        for row_index, row in enumerate(self.world_map):
            for col_index, col in enumerate(row):
                x = col_index * TILESIZE
                y = row_index * TILESIZE

                self.background.blit(random.choice(grass_tiles), (x, y))
                if col == "W":
                    Wall(x, y, self.environment, self.visible_entities)
                    continue

                x += HALF_TILESIZE
                y += HALF_TILESIZE

                if col == "P":
                    players += 1
                    self.player = Player(x, y, [self.environment], self,
                                         self.player_group, self.actors, self.visible_entities)
                elif col == "E":
                    Enemy(x, y, [self.environment], self, self.enemies, self.actors, self.visible_entities)

        if players != 1:
            raise Exception(f"Invalid number of players: {players}")

    def process_event(self, event: pg.event.Event, dt: int):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.pause()
            elif event.key == pg.K_SPACE:
                self.player_start_attack()

    def player_start_attack(self):
        self._attack_sound.play()
        attack = self.player.attack()
        self.attacks.add(attack)
        self.visible_entities.add(attack)

    def pause(self):
        pg.mixer.music.stop()
        self.game.pause()

    def play(self):
        pg.mixer.music.play(-1)

    def update(self, dt):
        """
        Applica le logiche per aggiornare lo stato.
        """
        # Chiamo la `update()` di tutti gli `Actor` nel gruppo `self.actors`
        self.actors.update(dt)

        for enemy in self.enemies:
            if self.player.collide(enemy):
                assert isinstance(enemy, Enemy)
                if enemy.damage_player():
                    self._player_hit_sound.play()

        if self.player.is_attacking():
            self.attacks.update()
            attacked_enemies = pg.sprite.groupcollide(self.attacks, self.enemies, False, False)

            for attack, enemies in attacked_enemies.items():
                assert isinstance(attack, Attack) and isinstance(enemies, list)
                for enemy in enemies:
                    attack.hit(enemy)

            if attacked_enemies:
                self._enemy_hit_sound.play()

    def draw(self):
        """
        Disegna a schermo (renderizza) l'attuale stato di gioco.
        """
        self.screen.blit(self.background, (0, 0))
        for ent in sorted(self.visible_entities, key=lambda e: e.pos[1]):
            assert isinstance(ent, Entity)
            ent.draw(self.screen)

    def game_over(self):
        pg.mixer.music.stop()
        self._game_over_sound.play()
        self.game.game_over()


class Pause(State):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.screen.fill(BLUE)

        # Inizializza font.
        big_font = pg.font.Font(FONTS / "NormalFont.ttf", 50)
        small_font = pg.font.Font(FONTS / "NormalFont.ttf", 18)

        # Crea `Surface` con scritta.
        bf_surf = big_font.render("PAUSA", False, YELLOW)
        sf_surf = small_font.render("ESC: TORNA AL GIOCO", False, YELLOW)

        # Creo `Rect` per la posizione.
        x, y = VIEW_RES
        center_x, center_y = x / 2, y / 2
        bf_rect = bf_surf.get_rect(midbottom=(center_x, center_y))
        sf_rect = sf_surf.get_rect(midbottom=(center_x, y - 20))

        # Disegno le surface su `self.screen`
        self.screen.blit(bf_surf, bf_rect)
        self.screen.blit(sf_surf, sf_rect)

    def process_event(self, event: pg.event.Event, dt: int):
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.game.play()


class GameOver(State):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.screen.fill(RED)

        # Inizializza font.
        big_font = pg.font.Font(FONTS / "NormalFont.ttf", 30)
        small_font = pg.font.Font(FONTS / "NormalFont.ttf", 16)

        # Crea `Surface` con scritta.
        bf_surf = big_font.render("GAME OVER", False, "white")
        sf_surf = small_font.render("SPAZIO: NUOVA PARTITA", False, "white")

        # Creo `Rect` per la posizione.
        x, y = VIEW_RES
        center_x, center_y = x / 2, y / 2
        bf_rect = bf_surf.get_rect(midbottom=(center_x, center_y))
        sf_rect = sf_surf.get_rect(midbottom=(center_x, y - 20))

        # Disegno le surface su `self.screen`
        self.screen.blit(bf_surf, bf_rect)
        self.screen.blit(sf_surf, sf_rect)

    def process_event(self, event: pg.event.Event, dt: int):
        if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            self.game.new_game()
