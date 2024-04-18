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

old_settings = None

def run(start_function=None):
    global old_settings
    os.system('cls' if os.name == 'nt' else 'clear')
    old_settings = termios.tcgetattr(sys.stdin)

    # try:
    tty.setcbreak(sys.stdin.fileno())
    if start_function:
        start_function()

    while True:
        key = sys.stdin.read(1)
        if hasattr(__main__, '__input__'):
            __main__.__input__(key)
    # finally:
    #     # Restore original terminal settings
    #     termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

def quit():
    clear()
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    os.system('stty echo')
    exit()



if __name__ == '__main__':

    def __input__(key):
        print_at(f'key: {key}', 4, 2)

    def start():
        print_at('TEST', 2, 2)

    run(start)
