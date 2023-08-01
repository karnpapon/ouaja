import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
import queue
from pygame.locals import *
from easing_functions import *
from . import const
from .button import Button
from . import arg
from . import states

pygame.init()

os.environ['SDL_VIDEO_WINDOW_POS'] = '0, 0'
WINDOW = pygame.display.set_mode((const.WIDTH, const.HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("live-ghosting")
bg = pygame.image.load(os.path.join("img", "ghost-board7.png")).convert()
bg = pygame.transform.scale(bg, (const.WIDTH, const.HEIGHT))
logo = pygame.image.load(os.path.join("img", "logo.png")).convert()
logo = pygame.transform.scale(logo, (logo.get_width() / 1.5, logo.get_height() / 1.5))
coin = pygame.image.load(os.path.join("img", "coin-sm-shadow2.png")).convert_alpha()

clock = pygame.time.Clock()

class Pointer(object):
    def __init__(self, x, y, color):
        self.color = color
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(const.VELOCITY, const.VELOCITY)
        self.acceleration = pygame.Vector2(0.5, 0.5)
        self.friction = 0.95

    def Draw(self, surface):
        surface.blit(coin, (self.position.x - coin.get_width() /
                     2, self.position.y - coin.get_height() / 2))

    def Move(self, to: pygame.Vector2):
        target = to
        dir = target - self.position

        self.velocity.x = self.velocity.x * self.friction + \
            self.acceleration.x * dir.normalize().x
        self.velocity.y = self.velocity.y * self.friction + \
            self.acceleration.y * dir.normalize().y
        self.velocity.x = max(-const.MAX_SPEED, min(const.MAX_SPEED, self.velocity.x))
        self.velocity.y = max(-const.MAX_SPEED, min(const.MAX_SPEED, self.velocity.y))

        self.position.x += self.velocity.x
        self.position.y += self.velocity.y

def get_font(size):
    return pygame.font.SysFont("Argent Pixel CF", size)

# draw some text into an area of a surface
# automatically wraps words
# returns any text that didn't get blitted
# https://www.pygame.org/wiki/TextWrap
def draw_text(surface, text, color, rect, font, aa=False, bkg=None):
    rect = pygame.Rect(rect)
    y = rect.top
    lineSpacing = -2

    # get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # if we've wrapped the text, then adjust the wrap to the last word      
        if i < len(text): 
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]

    return text

pointer = Pointer(const.INIT_POINT_X, const.INIT_POINT_Y, const.RED)

def start():
    answer_index = 0
    timeout = const.FPS * const.TIMEOUT_FACTOR
    go_to_init_pos = False
    answer = ""
    current_answer = ""

    while not states.quit_app:
        try:
            reply = states.reply_answer.get(False)
        except queue.Empty:
            reply = None

        if not reply == None:
            answer = reply
            answer = answer.upper()
            to = pygame.Vector2(
                const.CHARACTERS[answer[answer_index]][0], const.CHARACTERS[answer[answer_index]][1])

        WINDOW.blit(bg, (0, 0))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        if answer_index <= len(answer) and answer:
            if pointer.position.distance_to(to) < 15 + 15:
                timeout -= 1

        if timeout == 0:
            if to == pygame.math.Vector2(const.INIT_POINT_X, const.INIT_POINT_Y):
                timeout = const.FPS * const.TIMEOUT_FACTOR
                current_answer = ""
                go_to_init_pos = False
            else:
                current_answer += answer[answer_index].upper()
                answer_index += 1
                if answer_index < len(answer):
                    char = answer[answer_index].upper()
                    timeout = const.FPS * const.TIMEOUT_FACTOR
                    if const.CHARACTERS.get(char):
                        to = pygame.Vector2(
                            const.CHARACTERS[char][0], const.CHARACTERS[char][1])
                else:
                    go_to_init_pos = True

        if go_to_init_pos and to != pygame.math.Vector2(const.INIT_POINT_X, const.INIT_POINT_Y):
            answer_index = 0
            to = pygame.Vector2(const.INIT_POINT_X, const.INIT_POINT_Y)
            # current_answer = ""
            timeout = const.FPS * const.TIMEOUT_FACTOR

        ghost_msg = pygame.font.SysFont(
            "Argent Pixel CF", 50)
        ghost_msg = ghost_msg.render(str(current_answer), True, const.WHITE)
        draw_text(WINDOW, current_answer, const.WHITE, [70, 105, 805, 78*4],pygame.font.SysFont("Argent Pixel CF", 50))

        if (answer):
            pointer.Move(to)

        pointer.Draw(WINDOW)
        arg.client.send_message(
            "/synth_coord", [pointer.position.x / const.WIDTH, 1.0 - pointer.position.y / const.HEIGHT])

        pygame.display.update()
        clock.tick(const.FPS)



def main():
    while not states.quit_app:

        # WINDOW.blit(logo, ((WIDTH/2) - logo.get_width() / 2, (HEIGHT/4) - logo.get_height() / 2))
        MENU_MOUSE_POS = pygame.mouse.get_pos()

        # MENU_TEXT = get_font(100).render("MAIN MENU", True, "#b68f40")
        # MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

        PLAY_BUTTON = Button(image=logo, pos=( (const.WIDTH/2) - 20, (const.HEIGHT/2) - 20 ), 
                            text_input="", font=get_font(70), base_color="#d7fcd4", hovering_color="White")
        # OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(640, 400), 
        #                     text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        # QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(640, 550), 
        #                     text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

        # WINDOW.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(WINDOW)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    start()
                # if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                #     options()
                # if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                #     pygame.quit()
                #     sys.exit()

        pygame.display.update()