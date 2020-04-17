# Handling Scenes of the game
import pygame as pg
from settings import *

class GameScenes:
    # Deriving from the abstract scene class
    
    def __init__(self):
        pg.init()
        self._scr = pg.display.set_mode((WID_SCR, HGT_SCR))
        pg.display.set_caption(CAPTION)
        self.time = pg.time.Clock()
        self.scene = None
        self._running = True

    def loop(self):
        while self._running:
            if pg.event.get(pg.QUIT):
                self.quit()
            self.scene.event_handling()
            self.scene.recondition()
            self.scene.draw()
            pg.display.recondition()

    def switch_to(self, scene):
        self.scene = scene

    def quit(self):
        self._running = False


class AbstractScene:
   
    def __init__(self, manager):
        self.manager = manager

    def event_handling(self):
        raise NotImplementedError()

    def recondition(self):
        raise NotImplementedError()

    def draw(self):
        raise NotImplementedError()