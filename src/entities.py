#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import random

from enum import Enum
from typing import TYPE_CHECKING, Type

import pygame as pg

from settings import *

from assets import Tileset

if TYPE_CHECKING:
    from states import World


class Direction(Enum):
    DOWN = (0, 1)
    UP = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class AnimationMachine:

    class Animation(Enum):
        MOVE = 0
        ATK = 1

    animation_duration: int = 100
    default_animation = (Animation.MOVE, Direction.DOWN)

    def __init__(self, sprite: pg.Sprite):
        self._sprite = sprite
        self._animation_locked = False
        self._animations: dict[AnimationMachine.Animation, dict[Direction, list[pg.Surface]]] = self._init_animations()
        self._set_default_animation()

    def get_curr_image(self):
        return self._curr_animation[int(self._curr_animation_loop)]

    @classmethod
    def _init_animations(cls) -> dict[Animation, dict[Direction, list[pg.Surface]]]:
        """
        Restituisce il dizionario delle animazioni dell'`Actor`.
        """
        raise NotImplementedError

    def _set_default_animation(self):
        animation, direction = self.default_animation
        self._set_animation(animation, direction)

    def _set_animation(self, animation: Animation, direction: Direction):
        self._curr_animation = self._animations[animation][direction]
        self._curr_animation_frames = len(self._curr_animation)
        self._curr_animation_loop = 0.

    def update(self, dt):
        if self._animation_locked:
            return

        if not self._sprite.dir.magnitude():
            self._curr_animation_loop = 0.
            return

        animation = self.Animation.MOVE
        xy = self._sprite.facing.xy

        direction = Direction(xy)

        if self._curr_animation is not self._animations[animation][direction]:
            self._set_animation(animation, direction)
            return

        self._curr_animation_loop += dt / self.animation_duration
        if self._curr_animation_loop >= self._curr_animation_frames:
            self._curr_animation_loop -= self._curr_animation_frames


class EnemyAnimation(AnimationMachine):

    @classmethod
    def _init_animations(cls):
        spritesheet = Tileset(IMAGES / "enemy_spritesheet.png", TILESIZE)
        return {
            cls.Animation.MOVE: {
                Direction.DOWN: spritesheet.images_at_col(0),
                Direction.UP: spritesheet.images_at_col(1),
                Direction.LEFT: spritesheet.images_at_col(2),
                Direction.RIGHT: spritesheet.images_at_col(3),
            }
        }


class PlayerAnimation(AnimationMachine):

    def attack_animation(self):
        self._animation_locked = True
        animation = self.Animation.ATK
        xy = self._sprite.facing.xy
        direction = Direction(xy)
        self._set_animation(animation, direction)

    def end_attack_animation(self):
        self._animation_locked = False
        self._set_default_animation()

    @classmethod
    def _init_animations(cls):
        spritesheet = Tileset(IMAGES / "player_spritesheet.png", TILESIZE)
        return {
            cls.Animation.MOVE: {
                Direction.DOWN: spritesheet.images_at_col(0)[:-1],
                Direction.UP: spritesheet.images_at_col(1)[:-1],
                Direction.LEFT: spritesheet.images_at_col(2)[:-1],
                Direction.RIGHT: spritesheet.images_at_col(3)[:-1],
            },
            cls.Animation.ATK: {
                Direction.DOWN: spritesheet.images_at_col(0)[-1:],
                Direction.UP: spritesheet.images_at_col(1)[-1:],
                Direction.LEFT: spritesheet.images_at_col(2)[-1:],
                Direction.RIGHT: spritesheet.images_at_col(3)[-1:],
            },
        }


class Entity(pg.sprite.Sprite):

    @property
    def pos(self):
        return self.rect.midbottom

    def draw(self, surface: pg.Surface):
        surface.blit(self.image, self.rect)


class Attack(Entity):

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
        sword_down = pg.image.load(IMAGES / "sword_y.png").convert_alpha()
        sword_right = pg.image.load(IMAGES / "sword_x.png").convert_alpha()
        surfaces = {
            Direction.DOWN: sword_down,
            Direction.UP: pg.transform.rotate(sword_down, 180),
            Direction.LEFT: pg.transform.rotate(sword_right, 180),
            Direction.RIGHT: sword_right,
        }
        return surfaces[Direction(self.dir.xy)]

    def update(self):
        self._move()
        if pg.time.get_ticks() > self._attack_animation_start + self.animation_time:
            self.player.end_attack()
            self.kill()

    def _move(self):
        p_rect = self.player.hitbox
        a_rect = self.rect
        xy = self.dir.xy

        if xy == (1, 0):
            a_rect.midleft = p_rect.midright
        elif xy == (0, 1):
            a_rect.midtop = p_rect.midbottom
        elif xy == (-1, 0):
            a_rect.midright = p_rect.midleft
        elif xy == (0, -1):
            a_rect.midbottom = self.player.rect.midtop

    def hit(self, entity: Actor):
        entity.suffer_damage(self.damage)


class Sword(Attack):

    damage = 1
    animation_time = 200


class Wall(Entity):

    def __init__(self, x: int, y: int, *args):
        super().__init__(*args)
        tiles: list[pg.Surface] = Tileset(IMAGES / "rock_tileset.png", TILESIZE).images_at_row(0)
        self.image = random.choice(tiles)
        self.rect = self.image.get_rect()
        self.rect.topleft = x, y


class Actor(Entity):

    animation_type: Type[AnimationMachine] = None
    speed: int = None
    max_hp: int = None
    damage: int = None
    immunity_time: int = 1000

    def __init__(self, x: int, y: int, colliding: list[pg.sprite.AbstractGroup], world: World, *args):
        super().__init__(*args)
        self._world = world
        self._animation = self.animation_type(self)

        self.facing = pg.Vector2(0, 1)

        self.rect = self.image.get_rect()
        self.hitbox = self.rect.inflate(-8, -8)
        self.dir = pg.math.Vector2()
        self._colliding_entities = colliding

        self.hitbox.midbottom = self.rect.midbottom = x, y
        self.hp = self.max_hp
        self.last_damage = 0.

    @property
    def image(self) -> pg.Surface:
        return self._animation.get_curr_image()

    @property
    def center(self):
        return self.rect.center

    def update(self, dt):
        """
        Applica le logiche per aggiornare lo stato del player.
        """
        self._move_and_collide(dt)
        self._update_rect()
        self._set_facing()
        self._animation.update(dt)

    def _update_rect(self):
        self.rect.midbottom = self.hitbox.midbottom

    def _set_facing(self):
        if self.dir.x != 0:
            self.facing.xy = -1 if self.dir.x < 0 else 1, 0
        elif self.dir.y != 0:
            self.facing.xy = 0, -1 if self.dir.y < 0 else 1

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

        self.hitbox.x += value
        for group in self._colliding_entities:
            for entity in group:
                if self.collide(entity):

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

        self.hitbox.y += value
        for group in self._colliding_entities:
            for entity in group:
                if self.collide(entity):

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
        r = self.hitbox

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
        self.hitbox.right = x

    def _collide_left(self, x: int):
        """
        Logica da applicare quando il `left` dell'entità
        collide con un'altra entità solida.
        `x` è la `x` del punto di collisione.
        """
        self.hitbox.left = x

    def _collide_bottom(self, y: int):
        """
        Logica da applicare quando il `bottom` dell'entità
        collide con un'altra entità solida.
        `y` è la `y` del punto di collisione.
        """
        self.hitbox.bottom = y

    def _collide_top(self, y: int):
        """
        Logica da applicare quando il `top` dell'entità
        collide con un'altra entità solida.
        `y` è la `y` del punto di collisione.
        """
        self.hitbox.top = y

    def collide(self, entity: pg.sprite.Sprite) -> bool:
        """
        `True` se le due entità collidono.
        """
        return self.hitbox.colliderect(entity.rect)

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

    animation_type = EnemyAnimation
    speed = .08
    view_range = 64
    max_hp = 1
    damage = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._player: Player = self._world.player

    def _update_dir(self):
        """
        Aggiorna il vettore direzione.
        """
        px, py = self._player.pos
        ex, ey = self.pos
        self.dir.xy = px - ex, py - ey

        if self.dir.magnitude() > self.view_range:
            self.dir.xy = 0, 0

    def damage_player(self):
        self._player.suffer_damage(self.damage)


class Player(Actor):

    animation_type = PlayerAnimation
    speed = .2
    max_hp = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._attack_type: Type[Attack] = Sword
        self._attack: Attack | None = None

    def attack(self) -> Attack:
        if not self.is_attacking():
            self._attack = self._attack_type(self)
            self._animation.attack_animation()
        return self._attack

    def end_attack(self):
        self._attack = None
        self._animation.end_attack_animation()

    def is_attacking(self):
        return bool(self._attack)

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
