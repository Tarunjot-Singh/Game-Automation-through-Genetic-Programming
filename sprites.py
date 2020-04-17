# Importing Required Libraries
# Sprites present in the game: Flappy_Bird and Pipe
import enum
import pygame as pg
from settings import *
from os import path

# Defining a movable class for sprite
class Sprite_Movable(pg.sprite.Sprite):
    # Initializer
    def __init__(self, *groups):
        super().__init__(*groups)
        self.rect = None

    def move_to(self, x=0, y=0):
        self.rect.x = x
        self.rect.y = y

    def move_by(self, dx=0, dy=0):
        self.rect.move_ip(dx, dy)


class Flappy_Bird(Sprite_Movable):
    def __init__(self, game, image: pg.Surface, x, y):
        self._layer = 2
        super().__init__(game.all_sprites, game.birds)
        self._game = game
        self.image = image
        self.origin_image = self.image
        self.rect = image.get_rect(x=x, y=y)
        self._vel_y = 0
        self.score = 0

    def update(self, *args):
        if self.rect.top > HGT_SCR or self.rect.bottom < 0:
            self.kill()
            return
        if pg.sprite.spritecollideany(self, self._game.pipes):
            self.kill()
            return
        self._vel_y = min(self._vel_y + GRAVITY_ACC, BIRD_MAX_Y_SPEED)
        self.rect.y += self._vel_y
        bird_angle = 40 - (self._vel_y + 4) / 8 * 80
        bird_angle = min(30, max(bird_angle, -30))
        self.image = pg.transform.rotate(self.origin_image, bird_angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def flap(self):
        self._vel_y = JUMP_SPEED

    @property
    def vel_y(self):
        return self._vel_y


class AIFlappy_Bird(Flappy_Bird):
    def __init__(self, game, image: pg.Surface, x, y, brain):
        super().__init__(game, image, x, y)
        self.brain = brain

    def kill(self):
        super().kill()
        self.brain.fitness = self.score

    def eval(self, v, h, g):
        return self.brain.eval(v, h, g)


class PipeType(enum.Enum):
    TOP = 0
    BOTTOM = 1


class Pipe(Sprite_Movable):
    def __init__(self, game, image, centerx, length, type_):
        self._layer = 1
        super().__init__(game.all_sprites, game.pipes)
        self._game = game
        self.type = type_
        self.image = pg.Surface((image.get_width(), length))
        if type_ == PipeType.TOP:
            self.image.blit(image, (0, 0), (0, image.get_height() - length, image.get_width(), length))
        else:
            self.image.blit(image, (0, 0), (0, 0, image.get_width(), length))
        self.rect = self.image.get_rect(centerx=centerx)
        if type_ == PipeType.TOP:
            self.rect.top = 0
        else:
            self.rect.bottom = HGT_SCR
        self.gap = 0
        self.length = length


class Background(pg.sprite.Sprite):
    def __init__(self, game, image):
        self._layer = 0
        super().__init__(game.all_sprites)
        if image.get_width() < WID_SCR:
            w = image.get_width()
            repeats = WID_SCR // w + 1
            self.image = pg.Surface((w * repeats, image.get_height()))
            for i in range(repeats):
                self.image.blit(image, (i * w, 0))
        else:
            self.image = image
        self.rect = self.image.get_rect()