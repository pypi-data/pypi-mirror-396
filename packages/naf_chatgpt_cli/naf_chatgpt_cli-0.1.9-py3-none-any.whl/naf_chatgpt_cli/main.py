#!/usr/bin/python3``
# -*- coding: utf-8 -*-
"""ChatGPT CLI with OpenAI API"""

import os
import readline
import save_load_history
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from time import time
import re

from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.document import Document

from openai import OpenAI

gpt_api_key = os.getenv("GPT_API_KEY")

client = OpenAI(
    api_key=gpt_api_key,
)


def format_rich(text):

    return Syntax(
        text, "markdown", theme="monokai", line_numbers=False, word_wrap=True, padding=0
    )

conversation_history = []

prefix = """
        You must return the output strictly in Markdown format.
        Rules:

        Return all output strictly in Markdown.
        Rules:

        1. Any code or examples must be wrapped in triple backticks ``` with the language if known.
        2. Text explanations or comments should be separated by a blank line from code blocks.
        3. Do not add extra spaces or characters at the start of lines.
        4. Do not combine multiple code blocks into one line; each block should be separate.
        5. Keep all code and text in one continuous Markdown response.
        6. Use line breaks for readability: description, blank line, code block, blank line, description, etc.
        7. If language is unknown, still wrap code in ``` without specifying language.
        """


def ask_chatgpt(question):
    """Answer the question using ChatGPT API.
    This function sends a question to the ChatGPT API and returns the answer.

    Args:
        question (str): The question to be asked.
        prefix (str): The prefix to be added to the question.
        conversation_history (list): The history of the conversation.

    Returns:
        str: answer from ChatGPT.
    """
    # add prefix to the question
    conversation_history.append({"role": "user", "content": f"{prefix}{question}"})

    # request to the API with conversation history and context
    response = client.chat.completions.create(
        model="gpt-5", messages=conversation_history
    )

    answer = response.choices[0].message.content

    # add answer to the conversation history
    conversation_history.append({"role": "assistant", "content": answer})

    return answer


def start_new_topic():
    """Start a new topic in the conversation.
    This function clears the conversation history and starts a new topic.
    """
    global conversation_history
    conversation_history = []
    print("A new topic has been started. You can ask your question.")


def start():
    """Start the ChatGPT CLI.
    This function initializes the conversation and handles user input.
    It provides options for changing the prefix, starting a new topic, and quitting the program.
    """
    info = "Welcome to ChatGPT!\nq - exit\nn - new topic\n0 - reset prefix \n00 - reset prefix and start new topic \n\
e - translate to English\np - translate to Polish\nrv - translate to Russian and provide usage examples\n\
r - translate to Russian\ns - save history conversation\nl - load istory conversation \nc - clear\nh - display help"
    print(info)
    global prefix

    bindings = KeyBindings()

    @bindings.add("f12")
    def _(event):
        """Clear the current input buffer."""
        event.current_buffer.reset()

    enter_count = 0
    last_enter_time = 0

    @bindings.add("enter")
    def _(event):
        """Handle Enter key."""
        nonlocal enter_count, last_enter_time
        current_time = time()

        # Check if the last enter was recent enough to count as double
        if (
            current_time - last_enter_time
        ) < 0.2:  # 1 second threshold for double press
            enter_count += 1
        else:
            enter_count = 1

        last_enter_time = current_time

        if enter_count == 2:
            # Process the buffer as a submission on double enter
            buffer = event.current_buffer
            buffer.validate_and_handle()
            enter_count = 0  # Reset counter after handling
        else:
            # Add a new line on single enter
            buffer = event.current_buffer
            document = buffer.document
            buffer.document = Document(
                text=document.text + "\n", cursor_position=document.cursor_position + 1
            )

    session = PromptSession(key_bindings=bindings)

    def get_multiline_input(prompt="\033[1;32mYou:\033[0m "):
        print(prompt)
        return session.prompt("")

    while True:

        user_input = get_multiline_input()

        if user_input.strip().lower() == "n":
            start_new_topic()
            print(
                """Start new Topic
                  To exit the mode, type - 00
                  To change the topic without changing the mode - 0
                  Help - h"""
            )
            continue
        elif user_input.strip().lower() == "q":
            break
        elif user_input.strip().lower() == "r":
            prefix = "Переведи на Русский только то что написано: "
            start_new_topic()
            print(
                """I will translate everything into Russian
                  To exit the mode, type - 00
                  To change the topic without changing the mode - 0
                  Help - h"""
            )
            continue
        elif user_input.strip().lower() == "e":
            prefix = "Translate into English Only what is written: "
            start_new_topic()
            print(
                """I will translate everything into ENGLISH.
                  To exit the mode, type - 00
                  To change the topic without changing the mode - 0
                  Help - h"""
            )
            continue
        elif user_input.strip().lower() == "0":
            prefix = """
                You must return the output strictly in Markdown format.
                Rules:

                Return all output strictly in Markdown.
                Rules:

                1. Any code or examples must be wrapped in triple backticks ``` with the language if known.
                2. Text explanations or comments should be separated by a blank line from code blocks.
                3. Do not add extra spaces or characters at the start of lines.
                4. Do not combine multiple code blocks into one line; each block should be separate.
                5. Keep all code and text in one continuous Markdown response.
                6. Use line breaks for readability: description, blank line, code block, blank line, description, etc.
                7. If language is unknown, still wrap code in ``` without specifying language.
                """
            print(
                """Removed context
                  To exit the mode, type - 00
                  To change the topic without changing the mode - 0
                  Help - h"""
            )
            continue
        elif user_input.strip().lower() == "c":
            os.system("clear")
            continue
        elif user_input.strip().lower() == "00":
            start_new_topic()
            print(
                """Removed context and cleared topic
                  To exit the mode, type - 00
                  To change the topic without changing the mode - 0
                  Help - h"""
            )
            prefix = """
                You must return the output strictly in Markdown format.
                Rules:

                Return all output strictly in Markdown.
                Rules:

                1. Any code or examples must be wrapped in triple backticks ``` with the language if known.
                2. Text explanations or comments should be separated by a blank line from code blocks.
                3. Do not add extra spaces or characters at the start of lines.
                4. Do not combine multiple code blocks into one line; each block should be separate.
                5. Keep all code and text in one continuous Markdown response.
                6. Use line breaks for readability: description, blank line, code block, blank line, description, etc.
                7. If language is unknown, still wrap code in ``` without specifying language.
                """
            continue
        elif user_input.strip().lower() == "s":
            save_load_history.save_to_file(conversation_history, "history.json")
            print("History saved to history.json")
            continue
        elif user_input.strip().lower() == "l":
            save_load_history.load_from_file("history.json")
            print("History loaded from history.json")
            continue
        elif user_input.strip().lower() == "p":
            prefix = "Переведи на Польский только то что написано: "
            start_new_topic()
            print(
                """I will translate everything into POLISH
                  To exit the mode, type - 00
                  To change the topic without changing the mode - 0
                  Help - h"""
            )
            continue
        elif user_input.strip().lower() == "rv":
            prefix = "Переведи, объясни смысл и приведи примеры на английском языке с переводами: "
            start_new_topic()
            print(
                """I will translate everything into Russian and provide examples of usage
                  To exit the mode, type - 00
                  To change the topic without changing the mode - 0
                  Help - h"""
            )
            continue
        elif user_input.strip().lower() == "h":
            print(info)
            continue

        response = ask_chatgpt(user_input)

        console = Console()
        print("\033[1;32mChatGPT:\033[0m")
        console.print(format_rich(response))
        print("")


if __name__ == "__main__":
    start()
