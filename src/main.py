#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

import pygame as pg

from settings import *


class Game:
    """
    Classe principale di gioco.
    """

    def __init__(self):
        pg.init()  # Inizializza i moduli di pygame.
        self.screen = self.init_screen()
        self.run_game_loop()

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
        while True:                # Game loop.
            self.process_events()  # Input.
            self.update()          # Update.
            self.render()          # Render.

    def process_events(self):
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

    def update(self):
        """
        Applica le logiche per aggiornare lo stato di gioco.
        """
        pass

    def render(self):
        """
        Disegna a schermo (renderizza) l'attuale stato di gioco.
        """
        pass


if __name__ == '__main__':
    Game()  # Crea un'istanza di `Game`, avviando il gioco.

