import threading
import random
import re
from . import const
from . import utils
from . import model
from . import states 

class Input(threading.Thread):

    def run(self):
        while not states.quit_app:
            question = input("> ")
            if question != "":
                # match commands with prefix (::).
                if val := re.match("^((::).[A-z]+) *\d*", question):
                    cmd = val.group().split(' ')
                    if cmd[0] == "::SET_FPS":
                        try:
                            const.FPS = utils.clamp(10, int(cmd[1]), 60)
                        except IndexError:
                            print(
                                "your SET_FPS index is not correct or maybe out of range.")
                    elif cmd[0] == "::SET_TIMEOUT_FACTOR":
                        try:
                            const.TIMEOUT_FACTOR = utils.clamp(1, int(cmd[1]), 8)
                        except IndexError:
                            print(
                                "your TIMEOUT_FACTOR index is not correct or maybe out of range.")
                    elif cmd[0] == "::SET_MAX_SPEED":
                        try:
                            const.MAX_SPEED = utils.clamp(1, int(cmd[1]), 200)
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
                        states.quit_app = True
                    # elif cmd[0] == "::BREAK":
                        # try:
                        #     reply_answer.get(False)
                        # except queue.Empty:
                        #     continue
                        # reply_answer.task_done()

                else:
                    # question = const.USER + question.lower() + '\n'
                    question = question.lower() + '\n'
                    answer = model.ask(question)
                    # mockup_ans = random.choice(
                    #     ["I am a ghost, so I don't have a gender."])
                    states.reply_answer.put(answer)
                    try:
                        outFile = open('conversation.txt', 'a')
                        outFile.write('Q:{}A:{}\n\n'.format(
                            question, answer))
                        outFile.close()
                    except IOError as e:
                        print("I/O error({0.filename}):".format(e))