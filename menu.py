import sys
import time

from render import THEMES, render, render_anima, CLEAR, HIDE_CURSOR, SHOW_CURSOR

def run_menu(maze, theme_names) -> None:
    theme_no = 0
    show_path = False
    animation = False

    try:
        sys.stdout.write(HIDE_CURSOR)
        while True:
            theme_name = theme_names[theme_no]

            sys.stdout.write(CLEAR)
