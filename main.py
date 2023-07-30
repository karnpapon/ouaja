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
reply_answer = queue.Queue()

WIDTH = 960
HEIGHT = 540

USER = "Person:"
PROMPT_TEXT = "GHOST"

INIT_POINT_X = 485
INIT_POINT_Y = 80
MAX_SPEED = 20
TIMEOUT_FACTOR = 4
FPS = 30
DECELERATION = 5

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (142, 68, 173)

CHARACTERS = {
    ' ': (688, 467),
    'A': (75, 290),
    'B': (148, 290),
    'C': (222, 290),
    'D': (290, 290),
    'E': (360, 290),
    'F': (425, 290),
    'G': (500, 290),
    'H': (570, 290),
    'I': (630, 290),
    'J': (676, 290),
    'K': (726, 290),
    'L': (793, 290),
    'M': (877, 290),
    'N': (80, 370),
    'O': (145, 370),
    'P': (210, 370),
    'Q': (274, 370),
    'R': (333, 370),
    'S': (397, 370),
    'T': (458, 370),
    'U': (525, 370),
    'V': (594, 370),
    'W': (671, 370),
    'X': (753, 370),
    'Y': (817, 370),
    'Z': (884, 370),
    '0': (75, 467),
    '1': (134, 467),
    '2': (189, 467),
    '3': (247, 467),
    '4': (311, 467),
    '5': (364, 467),
    '6': (431, 467),
    '7': (491, 467),
    '8': (551, 467),
    '9': (616, 467)
}

os.environ['SDL_VIDEO_WINDOW_POS'] = '0, 0'
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("live-ghosting")
bg = pygame.image.load(os.path.join("Images", "ghost-board2.png")).convert()
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
coin = pygame.image.load(os.path.join("Images", "coin-sm-shadow2.png"))

openai.api_key = os.getenv("OPENAI_API")


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
            "Argent Pixel CF", 85)
        ghost_msg = ghost_msg.render(str(current_answer), True, WHITE)
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
            if question != "":
                question = USER + question.lower() + '\n'
                # answer = ask(question)
                mockup_ans = random.choice(["I'm a ghost", "oxygen", "zebra"])
                reply_answer.put(mockup_ans)
                try:
                    outFile = open('conversation.txt', 'a')
                    outFile.write('Q:{}A:{}\n\n'.format(question, mockup_ans))
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
