import pygame
import neat
import time
import os
import random

pygame.font.init()  # init font

MIN_WIDTH = 500
MIN_HEIGHT = 800
FLOOR = 730
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)

BIRD_IMGS = [
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png"))),
]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))


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
        self.tick_count += 1  # Increment tick count

        d = self.vel * self.tick_count + 1.5 * self.tick_count**2
        # How much we are moving up or down this frame

        if d >= 16:  # if we are moving down more than 16 pixels
            d = 16  # this changes the value to 16 so that we don't move down too fast

        if d < 0:  # if we are moving up
            d -= 2  # move up a little more so that we don't move up too fast

        self.y = (
            self.y + d
        )  # what this does is it moves the bird up or down depending on the value of d

        if d < 50 or self.y < self.height + 50:
            # if we are moving up or if we are above the height we started at
            # and if we are not tilted too far down
            if self.tilt < -self.MAX_ROTATION:  # if we are tilted too far down
                self.tilt = (
                    -self.MAX_ROTATION
                )  # set tilt to max rotation so that we don't tilt too far down
            else:
                if self.tilt > -90:
                    self.tilt -= self.ROT_VEL  # it tilts the bird down

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

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(
            center=self.img.get_rect(topleft=(self.x, self.y)).center
        )
        win.blit(rotated_image, new_rect.topleft)

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
        bird_mask = bird.get_mask()  # gets the mask of the bird
        top_mask = pygame.mask.from_surface(
            self.PIPE_TOP
        )  # gets the mask of the top pipe
        bottom_mask = pygame.mask.from_surface(
            self.PIPE_BOTTOM
        )  # gets the mask of the bottom pipe

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        # This is the distance between the bird and the top pipe
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))
        # This is the distance between the bird and the bottom pipe

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        # This is the point of collision between the bird and the bottom pipe
        t_point = bird_mask.overlap(top_mask, top_offset)
        # This is the point of collision between the bird and the top pipe

        if t_point or b_point:
            # if either of the points are not None
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


def draw_window(win, bird, pipes, base, score):
    win.blit(BG_IMG, (0, 0))  # This draws the background image
    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)

    score_label = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(score_label, (MIN_WIDTH - score_label.get_width() - 15, 10))

    bird.draw(win)

    pygame.display.update()  # This updates the display


def main():
    bird = Bird(230, 350)  # Create a new bird object with starting position (200, 200)
    base = Base(730)  # Create a new base object with starting position (730, 0)
    pipes = [Pipe(700)]  # Create a new pipe object with starting position (700, 0)
    win = pygame.display.set_mode(
        (MIN_WIDTH, MIN_HEIGHT)
    )  # Create a new window with width 500 and height 800
    clock = (
        pygame.time.Clock()
    )  # this is a clock object that we will use to set the fps of the game

    score = 0

    while True:
        clock.tick(30)  # this sets the fps of the game to 30
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # bird.move()  # we call the move function of the bird object every frame
        base.move()  # we call the move function of the base object every frame
        for pipe in pipes:
            if pipe.collide(bird):
                pass
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                pipes.remove(pipe)
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                score += 1
                pipes.append(Pipe(600))
            pipe.move()  # we call the move function of the pipe object every frame
        draw_window(win, bird, pipes, base, score)  # this draws the window every frame


main()
