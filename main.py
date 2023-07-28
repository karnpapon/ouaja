import pygame
import sys
import os
from pygame.locals import *
from easing_functions import *
import openai
import threading
import queue
import argparse
import random
from pythonosc import udp_client
from dotenv import load_dotenv
load_dotenv()
# import speech_recognition as sr
# import pyttsx3

pygame.init()
quit_app = False
commands = queue.Queue()

# Display
WIDTH = 960
HEIGHT = 540
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PTK By @Karnpapon")
bg = pygame.image.load(os.path.join("Images", "ghost-board.png"))
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
coin = pygame.image.load(os.path.join("Images", "coin-sm-shadow2.png"))
# coin = pygame.transform.scale(coin, (60, 60))

openai.api_key = os.getenv("OPENAI_API")
USER = "Person:"
PROMPT_TEXT = "GHOST"

# accel
MAX_SPEED = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (142, 68, 173)
INIT_POINT_X = 400
INIT_POINT_Y = 80
FPS = 60
DECELERATION = 5

CHARACTERS = {'A': (100, 212),
              ' ': (626, 354),
              'B': (150, 208),
              'C': (206, 208),
              'D': (251, 208),
              'E': (302, 208),
              'F': (342, 208),
              'G': (398, 208),
              'H': (441, 208),
              'I': (485, 208),
              'J': (524, 208),
              'K': (568, 208),
              'L': (611, 208),
              'M': (662, 218),
              'N': (104, 283),
              'O': (161, 283),
              'P': (216, 283),
              'Q': (271, 283),
              'R': (324, 283),
              'S': (378, 283),
              'T': (419, 283),
              'U': (455, 283),
              'V': (503, 283),
              'W': (554, 283),
              'X': (655, 283),
              'Y': (705, 283),
              'Z': (755, 283),
              '0': (99, 344),
              '1': (145, 344),
              '2': (200, 344),
              '3': (245, 344),
              '4': (297, 344),
              '5': (342, 344),
              '6': (396, 344),
              '7': (442, 344),
              '8': (491, 344),
              '9': (544, 344)}


class Pointer(object):
    def __init__(self, x, y, color):
        self.color = color
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(2, 2)
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
    answer_index = 0
    timeout = FPS * 4
    go_to_init_pos = False
    # is_italic = False
    answer = ""
    current_answer = ""

    while not quit_app:
        try:
            command = commands.get(False)
        except queue.Empty:
            command = None

        if not command == None:
            answer = command
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
                timeout = FPS * 4
                current_answer = ""
                go_to_init_pos = False
                # is_italic = bool(random.getrandbits(1))
            else:
                current_answer += answer[answer_index].upper()
                # is_italic = bool(random.getrandbits(1))
                answer_index += 1
                if answer_index < len(answer):
                    char = answer[answer_index].upper()
                    timeout = FPS * 4
                    if CHARACTERS.get(char):
                        to = pygame.Vector2(
                            CHARACTERS[char][0], CHARACTERS[char][1])
                else:
                    go_to_init_pos = True

        if go_to_init_pos and to != pygame.math.Vector2(INIT_POINT_X, INIT_POINT_Y):
            answer_index = 0
            to = pygame.Vector2(INIT_POINT_X, INIT_POINT_Y)
            # current_answer = ""
            timeout = FPS * 4

        ghost_msg = pygame.font.SysFont(
            "Argent Pixel CF", 85)
        ghost_msg = ghost_msg.render(str(current_answer), True, RED)
        WINDOW.blit(ghost_msg, (50, 125))

        if (answer):
            pointer.Move(to)

        pointer.Draw(WINDOW)
        client.send_message(
            "/synth_coord", [pointer.position.x / WIDTH, 1.0 - pointer.position.y / HEIGHT])

        pygame.display.update()
        clock.tick(FPS)


class Input(threading.Thread):
    def run(self):
        while not quit_app:
            question = input()
            question = USER + question.lower() + '\n'
            # answer = ask(question)
            mockup_ans = random.choice(["I'm a ghost", "oxygen", "zebra"])
            commands.put(mockup_ans)
            # print("commands: ", commands.get())


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
