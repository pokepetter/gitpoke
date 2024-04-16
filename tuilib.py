import tty
import termios
import os
import sys
from rich import print as print_rich
import __main__


def print_at(text, y=0, x=0):
    sys.stdout.write("\033[{};{}H".format(y, x))
    sys.stdout.write("\033[K")
    print_rich(text)
    sys.stdout.flush()


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def run(start_function=None):
    os.system('cls' if os.name == 'nt' else 'clear')

    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    if start_function:
        start_function()

    while True:
        key = sys.stdin.read(1)
        if hasattr(__main__, '__input__'):
            __main__.__input__(key)


if __name__ == '__main__':

    def __input__(key):
        print_at(f'key: {key}', 4, 2)

    def start():
        print_at('TEST', 2, 2)

    run(start)
