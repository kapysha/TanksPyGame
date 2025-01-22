import pygame
import pygame_menu
from main import WIDTH, HEIGHT

WHITE = (255, 255, 255)
LIGHT_GREY = (211, 211, 211)
DARK_GREY = (169, 169, 169)
DARKER_GREY = (105, 105, 105)


def start_game():
    print("Game Started")


def open_shop():
    print("Shop Opened")


def open_settings():
    print("Settings Opened")


def exit_game():
    pygame.quit()
    quit()


def load_background():
    background_image = pygame.image.load('images/background.png')
    return background_image


def draw_screen(screen):
    background_image = load_background()
    screen.blit(background_image, (0, 0))
    pygame.display.update()


menu_theme = pygame_menu.themes.THEME_DARK.copy()
menu_theme.title_background_color = DARK_GREY
menu_theme.title_font_color = WHITE
menu_theme.widget_font_color = WHITE
menu_theme.widget_font = pygame.font.SysFont('Arial', 35)
menu_theme.widget_background_color = DARK_GREY
menu_theme.widget_border_color = DARKER_GREY
menu_theme.widget_border_width = 2
menu_theme.widget_selected_background_color = LIGHT_GREY
menu_theme.widget_selected_font_color = DARKER_GREY

screen = pygame.display.set_mode((WIDTH, HEIGHT))
menu = pygame_menu.Menu("Main Menu", WIDTH, HEIGHT, theme=menu_theme)

play = menu.add.button("Играть", start_game)
mag = menu.add.button("Магазин", open_shop)
settings = menu.add.button("Настройки", open_settings)
quit_btn = menu.add.button("Выйти", exit_game)

running = True
while running:
    screen.fill((0, 0, 0))
    background_image = load_background()
    screen.blit(background_image, (-30, -50))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for btn in [play, mag, settings, quit_btn]:
        btn.draw(screen)
    pygame.display.flip()
pygame.quit()
