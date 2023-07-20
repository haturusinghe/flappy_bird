import pygame
import neat
import time
import os
import random

MIN_WIDTH = 500
MIN_HEIGHT = 800

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
        self.img_count = 0  # Which image we are currently showing
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


def draw_window(win, bird):
    win.blit(BG_IMG, (0, 0))  # This draws the background image
    bird.draw(win)
    pygame.display.update()  # This updates the display


def main():
    bird = Bird(200, 200)  # Create a new bird object with starting position (200, 200)
    win = pygame.display.set_mode(
        (MIN_WIDTH, MIN_HEIGHT)
    )  # Create a new window with width 500 and height 800
    clock = (
        pygame.time.Clock()
    )  # this is a clock object that we will use to set the fps of the game

    while True:
        clock.tick(30)  # this sets the fps of the game to 30
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        # bird.move()  # we call the move function of the bird object every frame
        draw_window(win, bird)  # this draws the window every frame


main()
