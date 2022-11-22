#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import pygame as pg

from settings import *


class Player(pg.sprite.Sprite):

    def __init__(self, *groups: pg.sprite.AbstractGroup):
        super().__init__(*groups)

        self.image = self.get_surface()
        self.rect = self.image.get_rect()

        self.dir = pg.math.Vector2()
        self.speed = 0.4

    def get_surface(self) -> pg.Surface:
        """
        Restituisce una surface
        """
        surf = pg.Surface((50, 50))
        surf.fill(YELLOW)
        eye = pg.Surface((10, 20))
        eye.fill("black")
        surf.blits([(eye, (12, 10)), (eye, (28, 10))])
        return surf

    def move(self, keys, dt):
        """
        Gestisce l'input utente legato al movimento del giocatore.
        """
        self.dir.x = keys[pg.K_RIGHT] - keys[pg.K_LEFT]

        # Nota: asse delle y invertito in Pygame.
        self.dir.y = keys[pg.K_DOWN] - keys[pg.K_UP]

        if self.dir.magnitude() != 0:
            self.dir.normalize()

        self.rect.move_ip(self.dir * self.speed * dt)

    def update(self, dt):
        """
        Applica le logiche per aggiornare lo stato del player.
        """
        # Mapping dei tasti. { key : 0 | 1 }.
        keys = pg.key.get_pressed()
        self.move(keys, dt)


class Game:
    """
    Classe principale di gioco.
    """

    def __init__(self):
        pg.init()  # Inizializza i moduli di pygame.
        self.screen = self.init_screen()
        self.mouse_pos = (0, 0)
        self.init_entities()
        self.clock = pg.time.Clock()
        self.run_game_loop()

    def init_entities(self):
        self.entities = pg.sprite.Group()
        self.player = Player(self.entities)

    def init_screen(self) -> pg.Surface:
        """
        Setta il titolo e le dimensioni della finestra
        principale di gioco e la restituisce.
        """
        # Setta il nome della finestra di gioco.
        pg.display.set_caption(TITOLO)

        # Inizializza la finestra di gioco settandone la risoluzione e la restituisce.
        return pg.display.set_mode(RISOLUZIONE)

    def run_game_loop(self):
        """
        Chiamare questo metodo per avviare il game loop.

        Il Game loop consiste in una sequenza di processi che viene
        eseguita continuamente fintanto che il gioco è in esecuzione.

        I tre processi principali sono:
          * Input;
          * Update;
          * Render.

        """
        while True:                            # Game loop.
            delta_time = self.clock.tick(60)   # Limita il framerate e restituisce il tempo trascorso dall'ultimo frame.
            self.process_events(delta_time)    # Input.
            self.update(delta_time)            # Update.
            self.draw()                        # Render.

    def process_events(self, dt: int):
        """
        Questo metodo si occupa di catturare gli eventi
        e aggiornare lo stato di gioco di conseguenza.
        In pygame, gli eventi sono uno dei modi in cui
        viene gestito l'input utente.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                # L'evento `QUIT` rappresenta il click, da parte dell'utente,
                # sulla `x` della finestra di gioco, solitamente utilizzata per
                # chiudere una finestra. Se l'utente la clicca, allora terminiamo
                # l'applicazione (eventualmente si possono eseguire prima delle
                # logiche, ad esempio mostrare un pop-up per chiedere conferma,
                # oppure eseguire un salvataggio automatico.
                sys.exit()
            elif event.type == pg.MOUSEMOTION:
                # Usiamo l'attributo `pos` dell'evento `MOUSEMOTION`
                # per aggiornare la posizione del mouse.
                self.mouse_pos = event.pos

    def update(self, dt: int):
        """
        Applica le logiche per aggiornare lo stato di gioco.
        """
        self.entities.update(dt)

    def draw(self):
        """
        Disegna a schermo (renderizza) l'attuale stato di gioco.
        """
        self.screen.fill(BLUE)
        self.entities.draw(self.screen)

        # Aggiorna la vista, rendendo effettivamente visibile ciò che
        # abbiamo disegnato su `self.screen` (che è la nostra finestra).
        pg.display.update()


if __name__ == '__main__':
    Game()  # Crea un'istanza di `Game`, avviando il gioco.

