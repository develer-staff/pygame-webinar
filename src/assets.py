#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import pygame as pg

from settings import *


class Tileset:
    """
    Classe che rappresenta un tileset/spritesheet e che
    espone i metodi per accedere ai singoli tile.
    """

    def __init__(self, filename: str, tilesize: int):
        self.sheet = pg.image.load(filename).convert_alpha()
        self.tilesize = tilesize

        size_x, size_y = self.sheet.get_size()
        self.rows = size_y // self.tilesize
        self.cols = size_x // self.tilesize

    def image_at(self, x: int, y: int) -> pg.Surface:
        """
        Date delle coordinate `x` e `y`, restituisce
        l'immagine presente a quelle coordinate.
        """
        size = (self.tilesize, self.tilesize)
        image = pg.Surface(size, pg.SRCALPHA)
        pos = (x * self.tilesize, y * self.tilesize)
        image.blit(self.sheet, (0, 0), pg.Rect(pos, size))
        image.convert_alpha()
        return image

    def images_at_row(self, y: int) -> list[pg.Surface]:
        """
        Restituisce la lista di immagini a una data riga.
        """
        return [self.image_at(x, y) for x in range(self.cols)]

    def images_at_col(self, x: int) -> list[pg.Surface]:
        """
        Restituisce la lista di immagini a una data colonna.
        """
        return [self.image_at(x, y) for y in range(self.rows)]


if __name__ == "__main__":
    pg.init()
    pg.display.set_caption("Prova assets.py")
    screen = pg.display.set_mode(SCREEN_RES, flags=pg.RESIZABLE | pg.SCALED)
    view = pg.Surface(VIEW_RES)

    rock_tileset = Tileset(IMAGES / "rock_tileset.png", TILESIZE)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()

        rocks = rock_tileset.images_at_row(0)
        for i, rock in enumerate(rocks):
            view.blit(rock, (i * TILESIZE, 0))

        pg.transform.scale(view, SCREEN_RES, screen)
        pg.display.update()
