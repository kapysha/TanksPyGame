import pygame
from typing import Callable
from config.settings import SIZE_MENU
from database.config import create_db
from screens.menu import menu

pygame.init()
pygame.font.init()
pygame.display.set_mode(SIZE_MENU)
pygame.display.set_caption("Танчики")

current_screen: Callable | None = None


def switch_screen(screen: Callable | None):
    global current_screen
    current_screen = screen


create_db()
switch_screen(menu)

while current_screen is not None:
    current_screen()
pygame.quit()
