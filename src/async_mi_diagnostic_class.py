# Load in helper functions
from .helper_functions import *

# Online motor imagery experiment
import pygame
from .constants import *
from .async_mi_core import AsyncMICore


class AsyncMIDiagnostic:
    """
    Loads up AsyncMICore and begins running it on a thread.
    Repeatedly pulls the predictions from AsyncMICore and displays it using pygame.
    Runs until keyboard interrupt (ctrl+c).
    """

    def __init__(self, eeg_name, filename, mock_file):
        self.async_mi_core = AsyncMICore(eeg_name, filename, mock_file, False)

    def _init_vis(self):
        # create screen
        pygame.init()
        self.win = pygame.display.set_mode((WIN_W, WIN_H))

    def run(self):
        self.async_mi_core.start()

        self._init_vis()  # create screen
        myfont = pygame.font.SysFont(
            "Comic Sans MS", 300
        )  # set it as comics sans bc yolo

        # MI threshold
        THRESHOLD = 0.5
        started_boo = False

        while True:  # go until specified duration\
            pygame.display.update()  # updates display

            if started_boo == False:
                # Fill buffer
                pygame.time.delay(5000)
                started_boo = True

            predicted, _ = self.async_mi_core.getData()

            if predicted > THRESHOLD:
                # draw screen
                self.win.fill(GREEN)

                # write MI
                text = myfont.render("MI", True, WHITE)
                textRect = text.get_rect()
                textRect.center = (WIN_W // 2, WIN_H // 2)
                self.win.blit(text, textRect)

            else:
                self.win.fill(PEACEFUL_BLUE)

            # pause processing
            # pygame.time.delay(100)
