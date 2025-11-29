# from psychopy import event
import random

### Experiment's imports ###
import pygame
from .constants import *

N_BLOCKS = 10


class Record:
    """
    Takes in an EEG and uses it to run an experiment to record MI data

    Used to draw instructions on a screen according to a pre-defined MI
    experiment and save files with information of the EEG data points,
    the timings of each trial, and other information such as accelerometry.
    """

    def __init__(self, explore):
        self.explore = explore

        # Pygame setup
        pygame.init()
        self.win = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Experiment: Wheelchair movement by MI activation")

        self.run_()

    ########   "Unimportant functions"   ###########
    def draw_images(self, color):
        # Display message on screen
        self.win.fill(color)
        if color == GREEN:
            msg = "GO"
            side = int(0.75 * WIN_W)
            # Indicator box
            pygame.draw.rect(self.win, WHITE, pygame.Rect(side, WIN_H / 2, 60, 60))

        elif color == RED:
            msg = "STOP"
            side = int(0.25 * WIN_W)
            # Indicator box
            pygame.draw.rect(self.win, WHITE, pygame.Rect(side, WIN_H / 2, 60, 60))

        elif color == PEACEFUL_BLUE:
            msg = "Rest"

        else:
            msg = ""

        letter_font = pygame.font.Font("freesansbold.ttf", 250)
        text = letter_font.render(msg, True, WHITE)
        textRect = text.get_rect()
        textRect.center = (WIN_W // 2, WIN_H // 2)
        self.win.blit(text, textRect)

        pygame.display.update()

    def countdown(self, surface, sec):
        """Displays a countdown at start of experiment"""
        x = 520
        y = 110
        surface.fill((0, 0, 0))
        myfont = pygame.font.SysFont("Comic Sans MS", 300)

        for i in range(sec, 0, -1):
            surface.fill((0, 0, 0))
            text = myfont.render(str(i), False, (160, 160, 160))
            surface.blit(text, (x, y))
            pygame.display.update()
            pygame.time.delay(1000)

    def quit_game(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

    ########   "Important" functions"   ############
    def move_WC_Display_screen(self):
        ### Total duration of one trial: 23s regardless of randomization
        # Different trial cases: Normal, Error_start
        ###

        self.quit_game()

        delta_t = random.randint(0, 2000)
        self.explore.set_marker(BLOCK_START)

        ###########      Rest (12-14s)      ##################
        self.draw_images(PEACEFUL_BLUE)
        # event.clearEvents()
        self.explore.set_marker(REST_trial)
        pygame.time.delay(12000 + delta_t)

        ###########      MI (6s)      #################
        self.draw_images(GREEN)
        # event.clearEvents()
        self.explore.set_marker(MI_trial)
        pygame.time.delay(6000)

        # Mark the end of one block
        self.explore.set_marker(BLOCK_END)

        print("One block done!")

    # mainloop
    # Assumes an Explore is currently running and is recording data
    # Should probably move the explore recorder into here
    def run_(self):
        # TODO we should clean up the code in here so that we can set the parameters
        # of a basic EEG experiment at a high level without having to dig around in here

        # Create and save trial order
        n_blocks = N_BLOCKS

        # Experiment start instruction
        letter_font = pygame.font.Font("freesansbold.ttf", 250)
        text = letter_font.render("Click to start", True, WHITE)
        textRect = text.get_rect()
        textRect.center = (WIN_W // 2, WIN_H // 2)
        self.win.blit(text, textRect)
        pygame.display.update()

        # Click to start
        start = False
        while not start:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    start = True
                    break

        self.countdown(self.win, 3)

        # Start experiment (screen display, time stamp labelling)
        self.explore.set_marker(EXPERIMENT_START)
        for block in range(n_blocks):
            self.move_WC_Display_screen()

        pygame.quit()
        pygame.time.delay(3000)

        # Experiment end
        self.explore.set_marker(EXPERIMENT_END)
        self.explore.stop_recording()
        self.explore.disconnect()
