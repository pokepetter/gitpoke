from pathlib import Path
import os.path
import time
from datetime import datetime
import math
from rich import print
from rich.panel import Panel
from rich.layout import Layout
from rich.syntax import Syntax
from rich.console import Console
from rich.markup import escape
import re
import sys
import os

SHOW_CHANGES = False
FILES = []
Y = 0
SCROLL = 0
MAX_WIDTH = 50
MAX_HEIGHT = 30
CURSOR_Y = Y

console = Console()
layout = Layout()
layout.split_row(
    Layout(name='file_view', minimum_size=100),
    Layout(name='changes')
)

repo = Path('.').resolve()
if not (repo / '.git').exists():
    print('[red]Not a git repo')
    exit()
# print(repo)

import subprocess
status_map = {
    ' M' : '[bright_yellow]~[/]',
    'M ' : '[bright_yellow]~[/]',
    'R ' : '[bright_yellow]R[/]',
    '??' : '[bright_green]+[/]',
    'A ' : '[bright_green]+[/]',
    ' D' : '[bright_red]-[/]',
    }


def clamp(value, floor, ceiling):
    return max(min(value, ceiling), floor)

def print_at(text, y=0, x=0):
    sys.stdout.write("\033[{};{}H".format(y, x))
    sys.stdout.write("\033[K")
    print(text)
    sys.stdout.flush()
    # sys.stdout.write(f'\033[{y};{x}H{text}')
    # sys.stdout.write('\033[K')
    # # sys.stdout.write(text)
    # sys.stdout.flush()
    # sys.stdout.write(f'\33[%d;%dH%s" "$Y" "$X" "$CHAR")


def get_status(scroll_to_bottom=False):
    os.system('cls' if os.name == 'nt' else 'clear')
    global FILES, SCROLL, Y
    FILES = [{
                'status' : line[:2],
                'path' : Path(line[3:].strip('"')),
                'modification_time' : Path(line[3:].strip('"')).stat().st_mtime if Path(line[3:].strip('"')).exists() else datetime.now().timestamp(),
                }
            for line in subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True).stdout.split('\n') if line]

    staged_files = [Path(line.strip('"')) for line in subprocess.run(['git', 'diff', '--name-only', '--cached'], capture_output=True, text=True).stdout.split('\n') if line]
    # paths = [Path(line) for line in subprocess.run(['git', 'ls-files'], capture_output=True, text=True).stdout.split('\n')]

    # modification_times = [e['path'].stat().st_mtime for e in files]
    # modification_dates = [time.ctime(e) for e in modification_times]    # convert the modification time to a readable format
    FILES.sort(key=lambda x: x['modification_time'])
    if scroll_to_bottom:
        Y = len(FILES)-1
        SCROLL = Y-MAX_HEIGHT+1

    file_view = ''

    scroll_indicator = ' ' * ((MAX_WIDTH // 2)+6-2) + '...\n'
    file_view += scroll_indicator if SCROLL > 0 else '\n'

    for i, e in enumerate(FILES[SCROLL:MAX_HEIGHT+SCROLL]):
        status, path, modification_time = e.values()
        # if status == 'R ':  # renamed
        #     path = Path(str(path).split(' -> ')[0])

        status = status_map.get(status, ''+status)
        # path = Path(path)
        difference = datetime.now() - datetime.strptime(time.ctime(modification_time), '%c')
        duration_in_s = difference.total_seconds()
        # years = divmod(duration_in_s, 31536000)[0]
        days = math.floor(duration_in_s / 86400)
        # hours = divmod(days[1], 3600)
        # staged_status = '\[[blue on white]staged][/]' + ' '*16 if path in staged_files else ''
        staged_status = '        [bold]' if (path in staged_files or (' -> ' in path.name and Path(path.name.split(' -> ')[1])) in staged_files) else ''

        cursor = f'[white on blue]>' if Y == i+SCROLL else '[default on default not bold] '

        path_as_str = escape(str(path))
        if len(path_as_str) > MAX_WIDTH:
            path_as_str = '...' + path_as_str[-(MAX_WIDTH-3):]

        file_view += f'{i+SCROLL} {cursor}{staged_status} {status} {path_as_str : <{MAX_WIDTH}} [grey50]{days}d[default on default]\n'

    file_view += scroll_indicator if SCROLL+MAX_HEIGHT < len(FILES) else '\n'
    file_view += '\n[grey50 on black]\[w] up    \[s] down    \[d] stage    \[a] unstage    \[q] quit    \n'

    # layout['file_view'].update(file_view)
    print_at(f'| Y:{Y}/{len(FILES)-1} scroll:{SCROLL}\n', y=0)
    print_at(file_view, y=2)


    current_file = FILES[Y]['path']

    if SHOW_CHANGES:
        if current_file not in staged_files:
            file_changes = subprocess.run(['git', '--no-pager', 'diff', current_file], capture_output=True, text=True).stdout
        else:
            file_changes = subprocess.run(['git', '--no-pager', 'diff', '--staged', current_file], capture_output=True, text=True).stdout

        file_changes = [l[:60] for l in file_changes.split('\n') if l.startswith('+') or l.startswith('-')]
        diff = 'changes:\n' + str(current_file) + '\n'.join(file_changes).replace('\n+','\n[black on bright_green] + [/] ').replace('\n-','\n[black on bright_red] - [/] ')
        # layout['changes'].update(diff))

        # print_at(diff, y=2, x=50)
        # print_at('HWELLO WORLD', y=2, x=50)
        for i, line in enumerate(diff.split('\n')[:40]):
            print_at(line, y=i+1, x=80)

    # # layout['changes'].update('changes:\n' + str(path) + file_changes)
    # # console.print(Syntax(file_changes, 'python'))
    # with console.capture() as capture:
    #     console.print(syntax)
    #
    # file_changes = capture.get()
    # # ansi_escape = re.compile(r'\x1b\[(\d+)(;\d+)?m')
    # # # Replace ANSI escape codes with Rich style formatting
    # # file_changes = ansi_escape.sub(lambda m: f"[{'bold ' if m.group(1) == '1' else ''}{'red' if m.group(1) == '31' else ''}]", file_changes)
    # layout['changes'].update(file_changes)


    # print(layout)


def stage(index):
    file = str(FILES[index]['path'])
    if ' -> ' in file:
        file = file.split(' -> ')[1]

    print('stage file', file)
    subprocess.run(['git', 'add', file])

def unstage(index):
    file = str(FILES[index]['path'])
    if ' -> ' in file:
        file = file.split(' -> ')[1]
    print('unstage file', file)
    subprocess.run(['git', 'reset', file])


get_status(scroll_to_bottom=True)
while True:
    choice = input()
    if choice == 'q':
        os.system('cls' if os.name == 'nt' else 'clear')
        exit()
    elif choice:
        for char in choice:
            if char == 'w':
                Y -= 1
                if Y < SCROLL:
                    SCROLL -= 1
            elif char == 'W':
                Y -= 10
                if Y < SCROLL:
                    SCROLL -= 10
            elif char == 's':
                Y += 1
                if Y >= MAX_HEIGHT-SCROLL:
                    SCROLL += 1

            elif char == 'S':
                Y += 10
                if Y >= MAX_HEIGHT-SCROLL:
                    SCROLL += 10
            elif char == 'd':
                stage(Y)
            elif char == 'a':
                unstage(Y)
            elif char == 'p':
                with console.capture() as capture:
                    console.print(syntax)
            elif char == 'c':
                SHOW_CHANGES = not SHOW_CHANGES

            elif char == 'f':
                SCROLL += 1
                Y -= 1
            elif char == 'e':
                SCROLL -= 1
                Y += 1
            SCROLL = clamp(SCROLL, 0, len(FILES)-MAX_HEIGHT)

            Y = clamp(Y, 0, len(FILES)-1)
            # if Y > MAX_HEIGHT:
            #     SCROLL = Y - MAX_HEIGHT + 1

        get_status()
    else:
        get_status()
    # if choice == 'w':
    #     get_status()

# print(result)


if __name__ == '__main__':
    main()
