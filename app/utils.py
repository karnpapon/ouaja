from . import const
import openai

def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))


def ask(question):
    text = f"{const.PROMPT_TEXT}\n{const.USER} {question}"
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
    