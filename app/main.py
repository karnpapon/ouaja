from . import transitions
from . import states
from . import arg
from .button import Button
from . import const
from . import pyganim
from easing_functions import *
from pygame.locals import *
import queue
import pygame
import sys
import os


os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'


pygame.init()
WINDOW = pygame.display.set_mode((const.WIDTH, const.HEIGHT))

frame_1 = pygame.image.load("assets/sprites/soul/soul_1.png").convert_alpha()
frame_2 = pygame.image.load("assets/sprites/soul/soul_2.png").convert_alpha()
frame_3 = pygame.image.load("assets/sprites/soul/soul_3.png").convert_alpha()
frame_4 = pygame.image.load("assets/sprites/soul/soul_4.png").convert_alpha()
frame_5 = pygame.image.load("assets/sprites/soul/soul_5.png").convert_alpha()
frame_6 = pygame.image.load("assets/sprites/soul/soul_6.png").convert_alpha()
frame_7 = pygame.image.load("assets/sprites/soul/soul_7.png").convert_alpha()
frame_8 = pygame.image.load("assets/sprites/soul/soul_8.png").convert_alpha()

swirl_fx_1 = pygame.image.load("assets/sprites/swirl/frame_00.png")
swirl_fx_2 = pygame.image.load("assets/sprites/swirl/frame_01.png")
swirl_fx_3 = pygame.image.load("assets/sprites/swirl/frame_02.png")
swirl_fx_4 = pygame.image.load("assets/sprites/swirl/frame_03.png")
swirl_fx_5 = pygame.image.load("assets/sprites/swirl/frame_04.png")
swirl_fx_6 = pygame.image.load("assets/sprites/swirl/frame_05.png")
swirl_fx_7 = pygame.image.load("assets/sprites/swirl/frame_06.png")
swirl_fx_8 = pygame.image.load("assets/sprites/swirl/frame_07.png")
swirl_fx_9 = pygame.image.load("assets/sprites/swirl/frame_08.png")
swirl_fx_10 = pygame.image.load("assets/sprites/swirl/frame_09.png")
swirl_fx_11 = pygame.image.load("assets/sprites/swirl/frame_10.png")
swirl_fx_12 = pygame.image.load("assets/sprites/swirl/frame_11.png")
swirl_fx_13 = pygame.image.load("assets/sprites/swirl/frame_12.png")
swirl_fx_14 = pygame.image.load("assets/sprites/swirl/frame_13.png")
swirl_fx_15 = pygame.image.load("assets/sprites/swirl/frame_14.png")
swirl_fx_16 = pygame.image.load("assets/sprites/swirl/frame_15.png")
swirl_fx_17 = pygame.image.load("assets/sprites/swirl/frame_16.png")

spriteAnim = pyganim.PygAnimation([(frame_1, 0.1),
                                 (frame_2, 0.1),
                                 (frame_3, 0.1),
                                 (frame_4, 0.1),
                                 (frame_5, 0.1),
                                 (frame_6, 0.1),
                                 (frame_7, 0.1),
                                 (frame_8, 0.1)])
spriteAnim.scale((frame_1.get_width() * 5, frame_1.get_height() * 5)) 
spriteAnim.play() 


fx_swirl = pyganim.PygAnimation([(swirl_fx_1, 0.1),
                                 (swirl_fx_2, 0.1),
                                 (swirl_fx_3, 0.1),
                                 (swirl_fx_4, 0.1),
                                 (swirl_fx_5, 0.1),
                                 (swirl_fx_6, 0.1),
                                 (swirl_fx_7, 0.1),
                                 (swirl_fx_8, 0.1),
                                 (swirl_fx_9, 0.1),
                                 (swirl_fx_10, 0.1),
                                 (swirl_fx_11, 0.1),
                                 (swirl_fx_12, 0.1),
                                 (swirl_fx_13, 0.1),
                                 (swirl_fx_14, 0.1),
                                 (swirl_fx_15, 0.1),
                                 (swirl_fx_16, 0.1),
                                 (swirl_fx_17, 0.1),
                                 ], loop=False)
fx_swirl.scale((swirl_fx_1.get_width() * 1, swirl_fx_1.get_height() * 1)) 

os.environ['SDL_VIDEO_WINDOW_POS'] = '0, 0'
pygame.display.set_caption("live-ghosting")
bg = pygame.image.load(os.path.join("img", "ghost-board7.png")).convert()
bg = pygame.transform.scale(bg, (const.WIDTH, const.HEIGHT))
logo = pygame.image.load(os.path.join("img", "logo.png")).convert()
logo = pygame.transform.scale(
    logo, (logo.get_width() / 1.5, logo.get_height() / 1.5))
coin = pygame.image.load(os.path.join(
    "img", "coin-sm-shadow2.png")).convert_alpha()

transitions.init(WINDOW, const.WIDTH, const.HEIGHT)
clock = pygame.time.Clock()

padding = 20

small_font = pygame.font.Font("assets/fonts/NicerNightie.ttf", 48)

# bg_color = (176, 174, 167) #B0AEA7
# text_color = (49, 47, 40) #312F28
# text_lightest_color = (125,120,102) #7D7866

bg_color = (0, 0, 0) #B0AEA7
text_color = (255, 0, 0) #312F28
text_lightest_color = (255,255,255) #7D7866

font = pygame.font.Font("assets/fonts/NicerNightie.ttf", 58)

# Board layout data
letters = "?ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890 "
# positions = []

# Layout constants
start_x = 50
start_y = 200
spacing = 28
row_spacing = 60

def draw_border(screen: pygame.Surface, tile, screen_width, screen_height, tile_size):
    # Top and Bottom
    for x in range(0, screen_width, tile_size):
        screen.blit(tile, (x, 0))  # Top
        screen.blit(tile, (x, screen_height - tile_size))  # Bottom

    # Left and Right
    for y in range(0, screen_height, tile_size):
        screen.blit(tile, (0, y))  # Left
        screen.blit(tile, (screen_width - tile_size, y))  # Right

class Pointer(object):
    def __init__(self, x, y, color):
        self.color = color
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(const.VELOCITY, const.VELOCITY)
        self.acceleration = pygame.Vector2(0.5, 0.5)
        self.friction = 0.95

    def Draw(self):
        spriteAnim.blit(WINDOW, (
            ( self.position.x - coin.get_width() / 2 ) + 10, 
            ( self.position.y - coin.get_height() / 2 )
        ))

    def Move(self, to: pygame.Vector2):
        target = to
        dir = target - self.position

        self.velocity.x = self.velocity.x * self.friction + \
            self.acceleration.x * dir.normalize().x
        self.velocity.y = self.velocity.y * self.friction + \
            self.acceleration.y * dir.normalize().y
        self.velocity.x = max(-const.MAX_SPEED,
                              min(const.MAX_SPEED, self.velocity.x))
        self.velocity.y = max(-const.MAX_SPEED,
                              min(const.MAX_SPEED, self.velocity.y))

        self.position.x += self.velocity.x
        self.position.y += self.velocity.y


def get_font(size):
    return pygame.font.Font("assets/fonts/NicerNightie.ttf", size)

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
    # transitions.run("fadeIn")

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

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # WINDOW.blit(bg, (0, 0))
        WINDOW.fill(bg_color)
        # if transitions.updateScreen() == False:
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
                # print(current_answer)
                fx_swirl.play() 
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

        ghost_msg = pygame.font.Font("assets/fonts/NicerNightie.ttf", 50)
        ghost_msg = ghost_msg.render(str(current_answer), True, const.WHITE)

        # Draw "YES" and "NO"
        yes_text = font.render("Yes", True, text_color)
        no_text = font.render("No", True, text_color)
        WINDOW.blit(yes_text, (70, 50))
        WINDOW.blit(no_text, (240, 50))

        # Draw "GOODBYE"
        goodbye_text = font.render("Goodbye", True, text_color)
        WINDOW.blit(goodbye_text, (700, 50))

        for _, letter in enumerate(letters):
            if letter == " ":
                display_letter = "(  )"
            else:
                display_letter = letter.lower() if letter.isalpha() else letter
            text = small_font.render(f"{display_letter}", True, text_color)
            pos = const.CHARACTERS[letter]
            WINDOW.blit(text, pos)

        draw_text(
            WINDOW,
            current_answer.title(),  # Capitalize each word
            const.RED,
            [70, 140, 805, 78*4],
            pygame.font.Font("assets/fonts/NicerNightie.ttf", 62)
        )

        if (answer):
            pointer.Move(to)
            if answer_index > 0:
                fx_swirl.blit(WINDOW, (
                    ( const.CHARACTERS[answer[answer_index - 1]][0] - swirl_fx_1.get_width() / 2 ) + 10,
                    (const.CHARACTERS[answer[answer_index - 1]][1] - swirl_fx_1.get_height() / 2) + 10
                ))

        pointer.Draw()
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

        # PLAY_BUTTON = Button(pos=((const.WIDTH/2) - 20, (const.HEIGHT/2) - 20),
        #                      text_input="Ouaja", font=get_font(70), base_color="#d7fcd4", hovering_color="White")
        # OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(640, 400),
        #                     text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        # QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(640, 550),
        #                     text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

        # WINDOW.blit(MENU_TEXT, MENU_RECT)
        WINDOW.fill(bg_color)

        # for button in [PLAY_BUTTON]:
        #     button.changeColor(MENU_MOUSE_POS)
        #     button.update(WINDOW)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                states.quit_app = True
                pygame.quit()
                sys.exit()
            # if event.type == pygame.MOUSEBUTTONDOWN:
            #     if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
            #         transitions.run("fadeOut")
            #         states.should_start = True
                # if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                #     options()
                # if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                #     pygame.quit()
                #     sys.exit()

        if transitions.updateScreen() == False:
            if states.should_start:
                start()

        pygame.display.update()
