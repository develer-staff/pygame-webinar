#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING, Type

import pygame as pg

from settings import *

if TYPE_CHECKING:
    from states import World


class Wall(pg.sprite.Sprite):

    def __init__(self, x: int, y: int, image: pg.Surface, *args):
        super().__init__(*args)
        self.image = image
        self.rect = image.get_rect()
        self.rect.topleft = x, y


class Attack(pg.sprite.Sprite):

    damage: int = None
    animation_time: int = None

    def __init__(self, player: Player, *groups):
        super().__init__(*groups)
        self.player = player
        self.dir = pg.Vector2(self.player.facing)
        self.image = self._get_surface()
        self.rect = self.image.get_rect()
        self._attack_animation_start = pg.time.get_ticks()

    def _get_surface(self) -> pg.Surface:
        surf = pg.Surface((SPRITESIZE, SPRITESIZE))
        surf.fill("gray")
        return surf

    def update(self):
        self._move()
        if pg.time.get_ticks() > self._attack_animation_start + self.animation_time:
            self.player.end_attack()
            self.kill()

    def _move(self):
        p_rect = self.player.rect
        a_rect = self.rect
        xy = self.dir.xy

        if xy == (1, 0):
            a_rect.midleft = p_rect.midright
        elif xy == (0, 1):
            a_rect.midtop = p_rect.midbottom
        elif xy == (-1, 0):
            a_rect.midright = p_rect.midleft
        elif xy == (0, -1):
            a_rect.midbottom = p_rect.midtop

    def hit(self, entity: Actor):
        entity.suffer_damage(self.damage)


class Sword(Attack):

    damage = 1
    animation_time = 200


class Entity(pg.sprite.Sprite):

    def __init__(self, world: World, *groups):
        super().__init__(*groups)
        self._world = world

        self.image = self._get_surface()
        self.rect = self.image.get_rect()
        self.dir = pg.math.Vector2()

    @property
    def center(self):
        return self.rect.center

    def _get_surface(self) -> pg.Surface:
        """
        Restituisce l'immagine relativa allo sprite.
        """
        raise NotImplementedError


class Actor(Entity):

    speed: int = None
    max_hp: int = None
    damage: int = None
    immunity_time: int = 1000

    def __init__(self, x: int, y: int, colliding: list[pg.sprite.AbstractGroup], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._colliding_entities = colliding

        self.rect.center = x, y
        self.hp = self.max_hp
        self.last_damage = 0

    def update(self, dt):
        """
        Applica le logiche per aggiornare lo stato del player.
        """
        self._move_and_collide(dt)

    def _update_dir(self):
        """
        Aggiorna il vettore direzione.
        """
        pass

    def _move_and_collide(self, dt):
        """
        Gestisce l'input utente legato al movimento del giocatore.
        """
        self._update_dir()

        if self.dir.magnitude() == 0:
            return

        self.dir.normalize_ip()

        x, y = self.dir * self.speed * dt

        self._move_x(x)
        self._move_y(y)
        self._collide_window()

    def _move_x(self, value):
        """
        Muove l'entità sull'asse X.
        """
        if value == 0:
            return

        self.rect.x += value
        for group in self._colliding_entities:
            for entity in group:
                if self._collide(entity):

                    if value > 0:
                        self._collide_right(entity.rect.left - 1)
                        continue

                    self._collide_left(entity.rect.right + 1)

    def _move_y(self, value):
        """
        Muove l'entità sull'asse Y.
        """
        if value == 0:
            return

        self.rect.y += value
        for group in self._colliding_entities:
            for entity in group:
                if self._collide(entity):

                    if value > 0:
                        self._collide_bottom(entity.rect.top - 1)
                        continue

                    self._collide_top(entity.rect.bottom + 1)

    def _collide_window(self):
        """
        Se l'entità collide col bordo della finestra,
        riposiziona l'entità.
        """
        left = top = 0
        right, bottom = VIEW_RES
        r = self.rect

        if r.top < top:
            self._collide_top(top - 1)
        elif r.bottom > bottom:
            self._collide_bottom(bottom + 1)

        if r.left < left:
            self._collide_left(left - 1)
        elif r.right > right:
            self._collide_right(right + 1)

    def _collide_right(self, x: int):
        """
        Logica da applicare quando il `right` dell'entità
        collide con un'altra entità solida.
        `x` è la `x` del punto di collisione.
        """
        self.rect.right = x

    def _collide_left(self, x: int):
        """
        Logica da applicare quando il `left` dell'entità
        collide con un'altra entità solida.
        `x` è la `x` del punto di collisione.
        """
        self.rect.left = x

    def _collide_bottom(self, y: int):
        """
        Logica da applicare quando il `bottom` dell'entità
        collide con un'altra entità solida.
        `y` è la `y` del punto di collisione.
        """
        self.rect.bottom = y

    def _collide_top(self, y: int):
        """
        Logica da applicare quando il `top` dell'entità
        collide con un'altra entità solida.
        `y` è la `y` del punto di collisione.
        """
        self.rect.top = y

    def _collide(self, entity: pg.sprite.Sprite) -> bool:
        """
        `True` se le due entità collidono.
        """
        return self.rect.colliderect(entity.rect)

    def suffer_damage(self, dmg: int):
        """
        L'entità riceve danno.
        """
        t = pg.time.get_ticks()
        elapsed = t - self.last_damage

        if elapsed <= self.immunity_time:
            return

        self.last_damage = t
        self.hp -= dmg
        if self.hp <= 0:
            self._die()

    def _die(self):
        """
        Logica da eseguire quando l'entità muore (hp <= 0).
        """
        self.kill()


class Enemy(Actor):

    speed = .3
    view_range = 250
    max_hp = 1
    damage = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._player: Player = self._world.player

    def _get_surface(self):
        surf = pg.Surface((SPRITESIZE, SPRITESIZE))
        surf.fill(RED)
        return surf

    def _update_dir(self):
        """
        Aggiorna il vettore direzione.
        """
        px, py = self._player.center
        ex, ey = self.center
        self.dir.xy = px - ex, py - ey

        if self.dir.magnitude() > self.view_range:
            self.dir.xy = 0, 0

    def damage_player(self):
        self._player.suffer_damage(self.damage)


class Player(Actor):

    speed = 0.4
    max_hp = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._attack_type: Type[Attack] = Sword
        self._attack: Attack | None = None
        self.facing = pg.Vector2(0, 1)

    def update(self, dt):
        super().update(dt)
        self._set_facing()

    def _set_facing(self):
        if self.dir.x != 0:
            self.facing.xy = -1 if self.dir.x < 0 else 1, 0
        elif self.dir.y != 0:
            self.facing.xy = 0, -1 if self.dir.y < 0 else 1

    def attack(self) -> Attack:
        if not self.is_attacking():
            self._attack = self._attack_type(self)
        return self._attack

    def end_attack(self):
        self._attack = None

    def is_attacking(self):
        return bool(self._attack)

    def _get_surface(self):
        surf = pg.Surface((SPRITESIZE, SPRITESIZE))
        surf.fill(YELLOW)
        return surf

    def _update_dir(self):
        """
        Aggiorna il vettore direzione.
        """
        # Mapping dei tasti. { key : 0 | 1 }.
        keys = pg.key.get_pressed()
        self.dir.x = keys[pg.K_RIGHT] - keys[pg.K_LEFT]
        self.dir.y = keys[pg.K_DOWN] - keys[pg.K_UP]  # Nota: asse delle y invertito in Pygame.

    def _die(self):
        super()._die()
        self._world.game_over()
