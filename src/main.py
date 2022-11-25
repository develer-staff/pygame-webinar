#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from enum import Enum

import pygame as pg

from settings import *
from states import State, World, Pause, GameOver


class GameStates(Enum):
    PLAY = 0
    PAUSE = 1
    GAME_OVER = 2


class Game:
    """
    Classe principale di gioco.
    """

    def __init__(self):
        pg.init()  # Inizializza i moduli di pygame.
        self.screen = self._init_screen()

        self.states: dict[GameStates, State] = {GameStates.PLAY: World(self),
                                                GameStates.PAUSE: Pause(self),
                                                GameStates.GAME_OVER: GameOver(self)}

        self.active_state = World(self)

        self.clock = pg.time.Clock()
        self.run_game_loop()

    def _init_screen(self) -> pg.Surface:
        """
        Setta il titolo e le dimensioni della finestra
        principale di gioco e la restituisce.
        """
        # Setta il nome della finestra di gioco.
        pg.display.set_caption(TITLE)

        # Inizializza la finestra di gioco settandone la risoluzione e la restituisce.
        return pg.display.set_mode(SCREEN_RES, flags=pg.RESIZABLE | pg.SCALED)

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

            self.active_state.process_event(event, dt)

    def update(self, dt: int):
        """
        Applica le logiche per aggiornare lo stato di gioco.
        """
        self.active_state.update(dt)

    def draw(self):
        """
        Disegna a schermo (renderizza) l'attuale stato di gioco.
        """
        self.active_state.draw()
        pg.transform.scale(self.active_state.screen, SCREEN_RES, self.screen)

        # Aggiorna la vista, rendendo effettivamente visibile ciò che
        # abbiamo disegnato su `self.screen` (che è la nostra finestra).
        pg.display.update()

    def pause(self):
        self.active_state = self.states[GameStates.PAUSE]

    def play(self):
        self.active_state = self.states[GameStates.PLAY]

    def game_over(self):
        self.active_state = self.states[GameStates.GAME_OVER]

    def new_game(self):
        play_state = self.states[GameStates.PLAY]
        assert isinstance(play_state, World)
        play_state.new_game()
        self.active_state = play_state


if __name__ == '__main__':
    Game()  # Crea un'istanza di `Game`, avviando il gioco.

