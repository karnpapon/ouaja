import pygame
import sys
import math
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
screen = pygame.display.set_mode((600, 500))
quit_app = False
commands = queue.Queue()

# Display
WIDTH = 1280
HEIGHT = 720
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PTK By @Karnpapon")
bg = pygame.image.load(os.path.join("Images", "ouija-board.jpeg"))
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

openai.api_key = os.getenv("OPENAI_API")
user = "Person:"
ai = "Geist:"
prompt_text = "GHOST"


# accel
MAX_SPEED = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (142, 68, 173)
INIT_POINT_X = 105
INIT_POINT_Y = 105
FPS = 30
DECELERATION = 5

CHARACTERS = {'A': (142, 386),
              'Ä': (142, 386),
              ' ': (1280/2, (720/2) + 120),
              'B': (230, 339),
              'C': (313, 310),
              'D': (394, 285),
              'E': (475, 269),
              'F': (558, 260),
              'G': (630, 257),
              'H': (721, 258),
              'I': (795, 269),
              'J': (855, 277),
              'K': (941, 304),
              'L': (1031, 334),
              'M': (1112, 371),
              'N': (163, 545),
              'O': (231, 495),
              'Ö': (231, 495),
              'P': (303, 452),
              'Q': (376, 423),
              'R': (460, 401),
              'S': (543, 382),
              'T': (621, 377),
              'U': (706, 379),
              'Ü': (706, 379),
              'V': (792, 384),
              'W': (884, 416),
              'X': (977, 453),
              'Y': (1050, 491),
              'Z': (1120, 539),
              '1': (291, 611),
              '2': (350, 614),
              '3': (428, 614),
              '4': (506, 614),
              '5': (588, 616),
              '6': (668, 614),
              '7': (747, 615),
              '8': (824, 616),
              '9': (905, 615),
              '0': (985, 610)}


class Ball(object):
    def __init__(self, x, y, color):
        self.color = color
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(2, 2)
        self.acceleration = pygame.Vector2(0.5, 0.5)
        self.friction = 0.95

    def Draw(self, surface):
        pygame.draw.circle(surface, self.color,
                           (self.position.x, self.position.y), 15, 0)

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
ball = Ball(INIT_POINT_X, INIT_POINT_Y, RED)


def ask(question):
    text = f"{prompt_text}\n{user} {question}"
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
            print("answer", answer, answer_index)
            to = pygame.Vector2(
                CHARACTERS[answer[answer_index]][0], CHARACTERS[answer[answer_index]][1])

        screen.blit(bg, (0, 0))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        if answer_index <= len(answer) and answer:
            if ball.position.distance_to(to) < 15 + 15:
                timeout -= 1
                # print("timeout:", timeout)

        if timeout == 0:
            if to == pygame.math.Vector2(INIT_POINT_X, INIT_POINT_Y):
                timeout = FPS * 4
                current_answer = ""
                go_to_init_pos = False
            else:
                current_answer += answer[answer_index].upper()
                answer_index += 1
                if answer_index < len(answer):
                    char = answer[answer_index].upper()
                    timeout = FPS * 4
                    if CHARACTERS.get(char):
                        # client.send_message("/ghost_coord", char)
                        to = pygame.Vector2(
                            CHARACTERS[char][0], CHARACTERS[char][1])
                else:
                    go_to_init_pos = True

        if go_to_init_pos and to != pygame.math.Vector2(INIT_POINT_X, INIT_POINT_Y):
            answer_index = 0
            to = pygame.Vector2(INIT_POINT_X, INIT_POINT_Y)
            # current_answer = ""
            timeout = FPS * 4

        ghost_msg = pygame.font.SysFont("Arial", 50, italic=True)
        ghost_msg = ghost_msg.render(str(current_answer), True, WHITE)
        WINDOW.blit(ghost_msg, (150, 0))

        if (answer):
            ball.Move(to)

        ball.Draw(WINDOW)

        pygame.display.update()
        clock.tick(FPS)


class Input(threading.Thread):
    def run(self):
        while not quit_app:
            question = input()
            question = user + question.lower() + '\n'
            # answer = ask(question)
            mockup_ans = random.choice(["ab", "bc", "cd"])
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
