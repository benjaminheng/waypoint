## Waypoint

A wearable device to provide in-building navigation guidance for Jing Qin.

## Development setup

### Arduino

???

### Python app

This is a Python 2 app.

- Create a virtualenv with `virtualenv env`
- Activate the virtualenv with `. env/bin/activate`
- Copy `config.ini.example` to `config.ini`
- Install dependencies with `pip install -r rpi/requirements.txt`
- Run the app with `python rpi/app.py`

## Python style guide

(Try to) follow the [PEP8](https://www.python.org/dev/peps/pep-0008/) style guide! A summary of notable PEP8 guidelines:

- 4 spaces per indentation level.
- Variable and method names should be lowercase_with_underscores.
- Class names should be using CapWords.
- Try to limit lines to 79 characters.
- Use single-quotes for strings.
- Top-level classes/functions should be separated by two blank lines.
- Import modules on separate lines. (BAD: `import os, sys`)

The easiest way to follow these rules is to just use a linter. [Flake8](http://flake8.pycqa.org/en/latest/) is recommended.

- Vim (https://github.com/nvie/vim-flake8)
- Atom (https://github.com/AtomLinter/linter-flake8)
- Sublime (https://github.com/dreadatour/Flake8Lint)
- VSCode (https://marketplace.visualstudio.com/items?itemName=donjayamanne.python)
- Notepad++ (why are you using this)
