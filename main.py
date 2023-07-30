import sys
import re
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
from pygame.locals import *
from easing_functions import *
import openai
import threading
import queue
import argparse
import random
from button import Button
from pythonosc import udp_client
from dotenv import load_dotenv
load_dotenv()
pygame.init()
quit_app = False
reply_answer = queue.Queue()

WIDTH = 960
HEIGHT = 540

USER = "Person:"
PROMPT_TEXT = "GHOST"

INIT_POINT_X = 482
INIT_POINT_Y = 50
MAX_SPEED = 20
TIMEOUT_FACTOR = 4
FPS = 30
VELOCITY = 2

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (142, 68, 173)

CHARACTERS = {
    ' ': (482, 482),

    'A': (95, 234 + 10),
    'B': (252, 234 + 10),
    'C': (405, 234 + 10),
    'D': (558, 234 + 10),
    'E': (707, 234 + 10),
    'F': (858, 234 + 10),

    'G': (97, 289 + 10),
    'H': (249, 289 + 10),
    'I': (404, 289 + 10),
    'J': (556, 289 + 10),
    'K': (707, 289 + 10),
    'L': (858, 289 + 10),

    'M': (97, 345 + 10),
    'N': (249, 345 + 10),
    'O': (404, 345 + 10),
    'P': (556, 345 + 10),
    'Q': (707, 345 + 10),
    'R': (858, 345 + 10),

    'S': (97, 401 + 10),
    'T': (249, 401 + 10),
    'U': (404, 401 + 10),
    'V': (556, 401 + 10),
    'W': (707, 401 + 10),
    'X': (858, 401 + 10),

    'Y': (404, 463 + 10),
    'Z': (556, 463 + 10),

    '0': (92, 464 + 10),
    '1': (150, 464 + 10),
    '2': (206, 464 + 10),
    '3': (268, 464 + 10),
    '4': (328, 464 + 10),

    '5': (638, 464),
    '6': (699, 464),
    '7': (758, 464),
    '8': (815, 464),
    '9': (875, 464)
}

os.environ['SDL_VIDEO_WINDOW_POS'] = '0, 0'
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("live-ghosting")
bg = pygame.image.load(os.path.join("images", "ghost-board5.png")).convert()
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
logo = pygame.image.load(os.path.join("images", "logo.png")).convert()
logo = pygame.transform.scale(logo, (logo.get_width() / 1.5, logo.get_height() / 1.5))
coin = pygame.image.load(os.path.join("images", "coin-sm-shadow2.png")).convert()

openai.api_key = os.getenv("OPENAI_API")


class Pointer(object):
    def __init__(self, x, y, color):
        self.color = color
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(VELOCITY, VELOCITY)
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
        self.velocity.x = max(-MAX_SPEED, min(MAX_SPEED, self.velocity.x))
        self.velocity.y = max(-MAX_SPEED, min(MAX_SPEED, self.velocity.y))

        self.position.x += self.velocity.x
        self.position.y += self.velocity.y


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

def get_font(size):
    return pygame.font.SysFont("Argent Pixel CF", size)

# Game Variables
clock = pygame.time.Clock()
pointer = Pointer(INIT_POINT_X, INIT_POINT_Y, RED)


def ask(question):
    text = f"{PROMPT_TEXT}\n{USER} {question}"
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=text,
        temperature=0.5,
        max_tokens=64,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    # print(response)
    response = response['choices'][0]['text'].replace("\n", "")
    return str(response)

def main():
    while not quit_app:

        # WINDOW.blit(logo, ((WIDTH/2) - logo.get_width() / 2, (HEIGHT/4) - logo.get_height() / 2))
        MENU_MOUSE_POS = pygame.mouse.get_pos()

        # MENU_TEXT = get_font(100).render("MAIN MENU", True, "#b68f40")
        # MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

        PLAY_BUTTON = Button(image=logo, pos=( (WIDTH/2) - 20, (HEIGHT/2) - 20 ), 
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

def start():
    answer_index = 0
    timeout = FPS * TIMEOUT_FACTOR
    go_to_init_pos = False
    answer = ""
    current_answer = ""

    while not quit_app:
        try:
            reply = reply_answer.get(False)
        except queue.Empty:
            reply = None

        if not reply == None:
            answer = reply
            answer = answer.upper()
            to = pygame.Vector2(
                CHARACTERS[answer[answer_index]][0], CHARACTERS[answer[answer_index]][1])

        WINDOW.blit(bg, (0, 0))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        if answer_index <= len(answer) and answer:
            if pointer.position.distance_to(to) < 15 + 15:
                timeout -= 1

        if timeout == 0:
            if to == pygame.math.Vector2(INIT_POINT_X, INIT_POINT_Y):
                timeout = FPS * TIMEOUT_FACTOR
                current_answer = ""
                go_to_init_pos = False
            else:
                current_answer += answer[answer_index].upper()
                answer_index += 1
                if answer_index < len(answer):
                    char = answer[answer_index].upper()
                    timeout = FPS * TIMEOUT_FACTOR
                    if CHARACTERS.get(char):
                        to = pygame.Vector2(
                            CHARACTERS[char][0], CHARACTERS[char][1])
                else:
                    go_to_init_pos = True

        if go_to_init_pos and to != pygame.math.Vector2(INIT_POINT_X, INIT_POINT_Y):
            answer_index = 0
            to = pygame.Vector2(INIT_POINT_X, INIT_POINT_Y)
            # current_answer = ""
            timeout = FPS * TIMEOUT_FACTOR

        ghost_msg = pygame.font.SysFont(
            "Argent Pixel CF", 50)
        ghost_msg = ghost_msg.render(str(current_answer), True, WHITE)
        draw_text(WINDOW, current_answer, WHITE, [70, 105, 805, 78*4],pygame.font.SysFont("Argent Pixel CF", 50))

        if (answer):
            pointer.Move(to)

        pointer.Draw(WINDOW)
        client.send_message(
            "/synth_coord", [pointer.position.x / WIDTH, 1.0 - pointer.position.y / HEIGHT])

        pygame.display.update()
        clock.tick(FPS)


def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))


class Input(threading.Thread):

    def run(self):
        global FPS
        global TIMEOUT_FACTOR
        global MAX_SPEED
        global pointer
        global quit_app
        global reply_answer

        while not quit_app:
            question = input("> ")
            if question != "":
                # match commands with prefix (::).
                if val := re.match("^((::).[A-z]+) *\d*", question):
                    cmd = val.group().split(' ')
                    if cmd[0] == "::SET_FPS":
                        try:
                            FPS = clamp(10, int(cmd[1]), 60)
                        except IndexError:
                            print(
                                "your SET_FPS index is not correct or maybe out of range.")
                    elif cmd[0] == "::SET_TIMEOUT_FACTOR":
                        try:
                            TIMEOUT_FACTOR = clamp(1, int(cmd[1]), 8)
                        except IndexError:
                            print(
                                "your TIMEOUT_FACTOR index is not correct or maybe out of range.")
                    elif cmd[0] == "::SET_MAX_SPEED":
                        try:
                            MAX_SPEED = clamp(1, int(cmd[1]), 200)
                        except IndexError:
                            print(
                                "your MAX_SPEED index is not correct or maybe out of range.")
                    # elif cmd[0] == "::SET_VELOCITY":
                    #     try:
                    #         pointer.velocity.x = clamp(1, int(cmd[1]), 10)
                    #         pointer.velocity.y = clamp(1, int(cmd[1]), 10)
                    #     except IndexError:
                    #         print(
                    #             "your VELOCITY index is not correct or maybe out of range.")
                    elif cmd[0] == "::BYE":
                        quit_app = True
                    # elif cmd[0] == "::BREAK":
                        # try:
                        #     reply_answer.get(False)
                        # except queue.Empty:
                        #     continue
                        # reply_answer.task_done()

                else:
                    question = USER + question.lower() + '\n'
                    # answer = ask(question)
                    mockup_ans = random.choice(
                        ["I am a ghost, so I don't have a gender."])
                    reply_answer.put(mockup_ans)
                    try:
                        outFile = open('conversation.txt', 'a')
                        outFile.write('Q:{}A:{}\n\n'.format(
                            question, mockup_ans))
                        outFile.close()
                    except IOError as e:
                        print("I/O error({0.filename}):".format(e))


if __name__ == "__main__":

    # setup/parsing OSC
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1",
                        help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=8080,
                        help="The port the OSC server is listening on")
    args = parser.parse_args()
    client = udp_client.SimpleUDPClient(args.ip, args.port)

    # app
    inp = Input()
    inp.start()
    main()
    inp.join()
