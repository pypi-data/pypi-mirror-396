# ChatGPT CLI

**ChatGPT CLI** is a Python-based command-line interface for interacting with ChatGPT using the OpenAI API.

## Features

- 🌐 Multilingual support (English, Russian, Polish)
- 💾 Save and load conversation history
- ⚡ Quick-access commands (e.g. `q`, `n`, `e`, `r`)
- 🖋️ Formatted output using `rich`

## Installation

1. **installation**

```bash
pip install naf-chatgpt-cli
# or
git clone https://github.com/nafanius/ChatGptCLI.git
cd chatgptcli
pip install .
# or
poetry install

```

2. **Set up your OpenAI API key**

```bash
export GPT_API_KEY=sk_your_key
export SAVE_PATH_GPT_HISTORY=/path/to/your/history # optional, default is saved in user's home directory
```

## Usage

Launch the CLI with:

```bash
chatgpt_cli
```

### How it use:

After launching the application, you can start typing your questions or commands. Here are some examples:

```bash
Welcome to ChatGPT!
q - exit
n - new topic
0 - reset prefix
00 - reset prefix and start new topic
e - translate to English
p - translate to Polish
rv - translate to Russian and provide usage examples
r - translate to Russian
s - save history conversation
l - load istory conversation
c - clear
h - display help
You:
What is the capital of France?
<tap double enter>

ChatGPT:
The capital of France is Paris.

You:

```

### Available Commands

| Command | Description                                                             |
| ------- | ----------------------------------------------------------------------- |
| `q`     | Quit the application                                                    |
| `n`     | Start a new topic                                                       |
| `0`     | Reset prefix (exit translation mode)                                    |
| `00`    | Reset prefix and start a new topic                                      |
| `e`     | Translate input to **English**                                          |
| `p`     | Translate input to **Polish**                                           |
| `r`     | Translate input to **Russian**                                          |
| `rv`    | Translate to **Russian** and explain usage with examples in **English** |
| `s`     | Save conversation history to `history.json`                             |
| `l`     | Load conversation history from `history.json`                           |
| `c`     | Clear the screen                                                        |
| `h`     | Show help message                                                       |

## Dependencies

- [`openai`](https://pypi.org/project/openai/)
- [`rich`](https://pypi.org/project/rich/)
- `readline` (usually included in Unix-based systems)
- `prompt-toolkit` (optional, for enhanced input handling)

## License

MIT License
