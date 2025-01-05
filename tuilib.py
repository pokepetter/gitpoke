import tty
import termios
import os
import sys
import shutil
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
        hex_int = None
        try:
            # as_hex = int(key, 16)
            # as_hex = bytes.fromhex(key).decode('utf-8')
            hex_int = ord(hex_str[2:].decode('unicode_escape'))
        except:
            pass
        clear()
        print(hex_int)
        if hex_int == 1:        key = 'control+a'
        elif key == '\x02':     key = 'control+b'
        elif key == '\x05':     key = 'control+e'
        elif key == '\x7f':     key = 'backspace'
        elif key == '\x08':     key = 'control+backspace'
        elif key == '\x12':     key = 'control+r'
        elif key == '\x17':     key = 'control+w'
        elif ord(key) == 27:    key = 'escape'
        elif key == '\x1b':
            quit()

        if hasattr(__main__, '__input__'):
            __main__.__input__(key)
    # finally:
    #     # Restore original terminal settings
    #     termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

def quit(message=''):
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    os.system('stty echo')
    print(message)
    exit()


def get_terminal_height():
    return shutil.get_terminal_size().lines

def get_terminal_width():
    return shutil.get_terminal_size().columns



if __name__ == '__main__':

    def __input__(key):
        print_at(f'key: {key}', 5, 2)

    def start():
        print_at('TEST', 2, 2)
        print_at(f'terminal height: {get_terminal_height()}', 3, 0)
        print_at(f'terminal width: {get_terminal_width()}', 4, 0)
    # print('hi')

    run(start)
