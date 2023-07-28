import os
import random

import neat
import pygame

pygame.font.init()  # init font

MIN_WIDTH = 500
MIN_HEIGHT = 800
FLOOR = 730
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = False

BIRD_IMGS = [
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png"))),
]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

gen = 0


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25  # How much the bird will tilt
    ROT_VEL = 20  # How much we will rotate on each frame
    ANIMATION_TIME = 5  # How long each bird animation will last

    # This is the constructor, it is called when we create a new bird
    def __init__(self, x, y):
        self.x = x  # Starting x position
        self.y = y  # Starting y position
        self.tilt = 0  # Starting tilt
        self.tick_count = 0  # How many ticks since last jump
        self.vel = 0  # Starting velocity
        self.height = self.y  # Starting height
        self.img_count = (
            0  # Which image we are currently showing, keeps track of the animation
        )
        self.img = self.IMGS[0]  # Starting image

    def jump(self):
        self.vel = -10.5  # Negative velocity means up
        self.tick_count = 0  # Reset tick count
        self.height = self.y  # Reset height

    def move(self):
        self.tick_count += 1

        # for downward acceleration
        displacement = self.vel * self.tick_count + 0.5 * (3) * self.tick_count ** 2  # calculate displacement

        # terminal velocity
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:  # tilt down
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1  # Increment image count

        # For animation of bird, loop through three images
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # so when bird is nose diving it isn't flapping
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        # tilt the bird
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)  # This is for pixel perfect collision


class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x  # x position of the pipe
        self.height = 0  # y position of the pipe

        self.top = 0  # position of the top pipe
        self.bottom = 0  # position of the bottom pipe
        self.PIPE_TOP = pygame.transform.flip(
            PIPE_IMG, False, True
        )  # flips the pipe image to make it face down
        self.PIPE_BOTTOM = PIPE_IMG  # pipe image

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(
            50, 450
        )  # generates a random height for the pipe between 50 and 450
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        """
        returns if a point is colliding with the pipe
        :param bird: Bird object
        :return: Bool
        """
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if b_point or t_point:
            return True

        return False


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # This makes the base move infinitely
        if self.x1 + self.WIDTH < 0:  # if the first base image is off the screen
            self.x1 = (
                    self.x2 + self.WIDTH
            )  # move the first base image to the right of the second base image
        if self.x2 + self.WIDTH < 0:  # if the second base image is off the screen
            self.x2 = (
                    self.x1 + self.WIDTH
            )  # move the second base image to the right of the first base image

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=topleft).center)

    surf.blit(rotated_image, new_rect.topleft)


def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
    if gen == 0:
        gen = 1
    win.blit(BG_IMG, (0, 0))  # This draws the background image

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)

    # score
    score_label = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(score_label, (MIN_WIDTH - score_label.get_width() - 15, 10))

    # generations
    score_label = STAT_FONT.render("Gens: " + str(gen - 1), 1, (255, 255, 255))
    win.blit(score_label, (10, 10))

    # alive
    score_label = STAT_FONT.render("Alive: " + str(len(birds)), 1, (255, 255, 255))
    win.blit(score_label, (10, 50))

    for bird in birds:
        # draw lines from bird to pipe
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255, 0, 0),
                                 (bird.x + bird.img.get_width() / 2, bird.y + bird.img.get_height() / 2),
                                 (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width() / 2, pipes[pipe_ind].height),
                                 5)
                pygame.draw.line(win, (255, 0, 0),
                                 (bird.x + bird.img.get_width() / 2, bird.y + bird.img.get_height() / 2), (
                                     pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width() / 2,
                                     pipes[pipe_ind].bottom), 5)
            except:
                pass
        # draw bird
        bird.draw(win)

    pygame.display.update()  # This updates the display


def eval_genomes(genomes, config):
    nets = []
    ge = []
    birds = []

    global gen
    gen += 1

    for gid, g in genomes:  # g is the genome
        g.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        ge.append(g)

    base = Base(FLOOR)  # Create a new base object with starting position (730, 0)
    pipes = [Pipe(700)]  # Create a new pipe object with starting position (700, 0)
    win = pygame.display.set_mode(
        (MIN_WIDTH, MIN_HEIGHT)
    )  # Create a new window with width 500 and height 800
    clock = (
        pygame.time.Clock()
    )  # this is a clock object that we will use to set the fps of the game

    score = 0

    run = True
    while run and len(birds) > 0:
        clock.tick(30)  # this sets the fps of the game to 30

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  # determine whether to
                # use the first or second
                pipe_ind = 1  # pipe on the screen for neural network input

        for bird in birds:  # This moves each bird in the list
            ge[birds.index(bird)].fitness += 0.1  # every frame the bird stays alive, it gets a fitness of 0.1
            bird.move()

            output = nets[birds.index(bird)].activate( #output determines whether the bird should jump or not
                (
                    bird.y, # y position of bird
                    abs(bird.y - pipes[pipe_ind].height), # location of top pipe
                    abs(bird.y - pipes[pipe_ind].bottom), # location of bottom pipe
                )
            )

            if output[0] > 0.5: #since we use the activation function tanh, we get a value between -1 and 1
                bird.jump()

        base.move()  # we call the move function of the base object every frame

        rem = []  # this is a list of pipes that we will remove
        add_pipe = False # this determines whether we should add a pipe or not
        for pipe in pipes:
            pipe.move() # we call the move function of the pipe object every frame
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)  # removes the bird from the list at index x
                    nets.pop(x)
                    ge.pop(x)

                # this checks if the bird has passed the pipe and sets add_pipe to True if it has
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True
                # ge[x].fitness += 5
                # pipes.append(Pipe(600))

            # this checks if the pipe is off the screen and adds it to the rem list if it is
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        # this removes the pipes in the rem list from the pipes list
        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        draw_window(win, birds, pipes, base, score, gen, pipe_ind)  # this draws the window every frame




def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    run(config_path)
