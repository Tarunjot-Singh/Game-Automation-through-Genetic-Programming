# Main Game module

# Importing Necessary Libraries
import random as rn
from enum import Enum
import os.path
import os
from sprites import *
import cgp

class GameMode(Enum):
    PLAYER = 0
    GP = 1
    VS = 2


class Game:
    def __init__(self):
        os.environ['SDL_VIDEO_WINDOW_POS'] = '300,400'
        pg.mixer.pre_init()
        pg.mixer.init()
        pg.init()
        self._scr = pg.display.set_mode((WID_SCR, HGT_SCR))
        pg.display.set_caption(CAPTION)
        self._time = pg.time.Clock()
        self._frames = FPS
        self.music_on = False

        # Setting up image variables
        self._flappy_image = None
        self._pipe_images = None
        self._background_image = None

        # Setting up sprite variables
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.birds = pg.sprite.Group()
        self.pipes = pg.sprite.Group()
        self._load_images()
        self._human_bird = None

        # Setting up pipe(sprite) variables
        self.running = True
        self.playing = False
        self._front_pipe = None
        self._pipe_space_min = PIPE_SPACE_MIN
        self._pipe_gap_min = PIPE_GAP_MIN

        # Settings for Genetic Program
        self.n_birds = MUTATION + LAMBDA
        self._max_score_till_now = 0
        self._max_score = 0
        self.present_generation = 0

        self.pop_evo = cgp.create_population(self.n_birds)

    def reset(self):
        if Verb:
            print(f'--------Generation: {self.present_generation}. Max score till now: {self._max_score_till_now}-------')
        self._max_score = 0
        self.present_generation += 1
        self._pipe_space_min = PIPE_SPACE_MIN
        self._pipe_gap_min = PIPE_GAP_MIN
        # Remove existing sprites
        for s in self.all_sprites:
            s.kill()
        # Instantiating Flappy birds
        for i in range(self.n_birds):
            x = rn.randint(20, 200)
            y = rn.randint(HGT_SCR // 4, HGT_SCR // 4 * 3)
            AIFlappy_Bird(self, self._flappy_image, x, y, self.pop_evo[i])
        # Spawning pipes for repeated motions
        self._spawn_pipe(80)
        while self._front_pipe.rect.x < WID_SCR:
            self._spawn_pipe()
        Background(self, self._background_image)

    def _load_images(self):
        # Loading required images for game display in window
        def _load_one_image(file_name):
            return pg.image.load(os.path.join(PIC_DIR, file_name)).convert_alpha()
        # Prime PNG files for game
        self._flappy_image = _load_one_image('flappy.png')
        self._pipe_images = [_load_one_image(name) for name in ['pipetop.png', 'pipebottom.png']]
        self._background_image = _load_one_image('background.png')
        self._blue_bird_image = _load_one_image('bluebird.png')

    def _spawn_pipe(self, front_x=None):
        # Spawning pipes in the display window
        if front_x is None:
            front_x = self._front_pipe.rect.x
        pipe_space = rn.randint(self._pipe_space_min, PIPE_SPACE_MAX)
        centerx = front_x + pipe_space
        d_gap = PIPE_GAP_MAX - self._pipe_gap_min
        d_space = PIPE_SPACE_MAX - self._pipe_space_min
        if pipe_space > (self._pipe_space_min + PIPE_SPACE_MAX) / 2:
            gap = rn.randint(self._pipe_gap_min, PIPE_GAP_MAX)
        else:
            gap = rn.randint(int(PIPE_GAP_MAX - d_gap * (pipe_space - self._pipe_space_min) / d_space),
                                 PIPE_GAP_MAX) + 8
        if pipe_space - self._pipe_gap_min < d_space // 3:
            top_length = self._front_pipe.length + rn.randint(-50, 50)
        else:
            top_length = rn.randint(PIPE_LENGTH_MIN, HGT_SCR - gap - PIPE_LENGTH_MIN)
        if self._front_pipe is not None:
            gap += abs(top_length - self._front_pipe.length) // 10
        bottom_length = HGT_SCR - gap - top_length
        top_pipe = Pipe(self, self._pipe_images[0], centerx, top_length, PipeType.TOP)
        bottom_pipe = Pipe(self, self._pipe_images[1], centerx, bottom_length, PipeType.BOTTOM)
        self._front_pipe = top_pipe
        top_pipe.gap = gap
        bottom_pipe.gap = gap

    def run(self):
        self.playing = True
        while self.playing:
            self._handle_events()
            self._update()
            self._draw()
            self._time.tick(self._frames)
        if not self.running:
            return
    # End of generation and spinning up new one
    # If score is low, mutation rates are increased
        pb = MUTATE_PROB
        if self._max_score < 500:
            pb = MUTATE_PROB * 3
        elif self._max_score < 1000:
            pb = MUTATE_PROB * 2
        elif self._max_score < 2000:
            pb = MUTATE_PROB * 1.5
        elif self._max_score < 5000:
            pb = MUTATE_PROB * 1.2
        self.pop_evo = cgp.evolve(self.pop_evo, pb,
                                  MUTATION, LAMBDA)

    def _create_human_player(self):
        # Creating a human player for parallel play
        xs = [p.rect.right for p in self.pipes if p.rect.right < WID_SCR // 2]
        if len(xs) > 0:
            x = max(xs) + 20
        else:
            x = WID_SCR // 2 - 100
        y = HGT_SCR // 2
        self._human_bird = Flappy_Bird(self, self._blue_bird_image, x, y)

    def _handle_events(self):
        # Handling Human Interference Events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.playing = False
                self.running = False
            elif event.type == pg.KEYDOWN:
                pressed = pg.key.get_pressed()
                ctrl_held = pressed[pg.K_LCTRL] or pressed[pg.K_RCTRL]
                if ctrl_held:
                    # Press control + 1/2/3 for adjusting frame rate and increase game speed
                    if event.key == pg.K_1:
                        self._frames = FPS
                    elif event.key == pg.K_2:
                        self._frames = 2 * FPS
                    elif event.key == pg.K_3:
                        self._frames = 3 * FPS
                    # Control + h for human player bird
                    elif event.key == pg.K_h:
                        if not self._human_bird or not self._human_bird.alive():
                            self._create_human_player()
                elif event.key == pg.K_SPACE or event.key == pg.K_UP:   # space: flap the human player's bird
                    if self._human_bird is not None and self._human_bird.alive():
                        self._human_bird.flap()

        for bird in self.birds:
            if bird is not self._human_bird:
                self.try_flap(bird)

    def _get_front_bottom_pipe(self, bird):

        front_bottom_pipe = min((p for p in self.pipes if p.type == PipeType.BOTTOM and p.rect.right >= bird.rect.left),
                                key=lambda p: p.rect.x)
        return front_bottom_pipe

    def try_flap(self, bird):
        # Flapping the bird
        front_bottom_pipe = self._get_front_bottom_pipe(bird)
        h = front_bottom_pipe.rect.x - bird.rect.x
        v = front_bottom_pipe.rect.y - bird.rect.y
        g = front_bottom_pipe.gap
        if bird.eval(v, h, g) > 0:
            bird.flap()

    def _update(self):
        # Update the state/position of bird
        self.all_sprites.update()
        if not self.birds:
            self.playing = False
            return
        # Moving the pipes back while the game moves forward
        leading_bird = max(self.birds, key=lambda b: b.rect.x)
        if leading_bird.rect.x < WID_SCR / 3:
            for bird in self.birds:
                bird.move_by(dx=BIRD_SPEED_X)
        else:
            for pipe in self.pipes:
                pipe.move_by(dx=-BIRD_SPEED_X)
                if pipe.rect.x < -50:
                    pipe.kill()
        # Counting score per frame
        for bird in self.birds:
            bird.score += 1

        self._max_score += 1
        self._max_score_till_now = max(self._max_score_till_now, self._max_score)
        # spawn newly required pipes
        while self._front_pipe.rect.x < WID_SCR:
            self._spawn_pipe()

    def _draw(self):
        self.all_sprites.draw(self._scr)
        # Display Live Score
        self._draw_text('Score: {}'.format(self._max_score), 10, 10)
        self._draw_text('Max score till now: {}'.format(self._max_score_till_now), 10, 10 + FT_SIZE + 2)
        self._draw_text('Bird Gen: {}'.format(self.present_generation), 10, 10 + 2 * (FT_SIZE + 2))
        n_alive = len(self.birds)
        if self._human_bird is not None and self._human_bird.alive():
            n_alive -= 1
        self._draw_text('Alive birds: {} / {}'.format(n_alive, self.n_birds), 10, 10 + 3 * (FT_SIZE + 2))
        pg.display.update()

    def _draw_text(self, text, x, y, color=BLACK, font=FT_NAME, size=FT_SIZE):
        font = pg.font.SysFont(font, size)
        text_surface = font.render(text, True, color)
        self._scr.blit(text_surface, (x, y))
