#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Questo file contiene le costanti globali che costituiscono le impostazioni di gioco.

NOTA: Alcune di queste informazioni, come la risoluzione, potrebbero essere tenute in un
      altro tipo di file, in modo da poter essere modificate tramite delle interazioni
      utente, ma, per questioni di semplificazione, le teniamo qui come costanti.
"""

# Schermo e finestra.
TITLE = "Game development con Pygame"
FPS = 60

SCREEN_RES = (800, 550)
SCREEN_TILES = (16, 11)

TILESIZE = 64
HALF_TILESIZE = TILESIZE / 2
SPRITESIZE = int(HALF_TILESIZE)

VIEW_RES = (SCREEN_TILES[0] * TILESIZE,
            SCREEN_TILES[1] * TILESIZE)

# Colori
BLUE = (0, 173, 233)
YELLOW = (252, 182, 71)
RED = (236, 101, 69)
