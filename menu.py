import pygame
import pygame_menu
from main import WIDTH, HEIGHT

WHITE = (255, 255, 255)
LIGHT_GREY = (211, 211, 211)
DARK_GREY = (169, 169, 169)
DARKER_GREY = (105, 105, 105)

# Фонт
font = pygame_menu.font.FONT_8BIT


# Функции для кнопок
def start_game():
    print("Game Started")


def open_shop():
    print("Shop Opened")


def open_settings():
    print("Settings Opened")


def exit_game():
    pygame.quit()
    quit()


# Функция для загрузки фона
def load_background():
    background_image = pygame.image.load('images/background.png')  # Укажи путь к своему фону
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))  # Масштабируем изображение
    return background_image


# Функция для рисования экрана
def draw_screen(screen):
    background_image = load_background()
    screen.blit(background_image, (0, 0))  # Отображаем фон на экране
    pygame.display.update()


# Меню
menu_theme = pygame_menu.themes.THEME_DARK.copy()  # Копируем стандартную темную тему
menu_theme.title_background_color = DARK_GREY  # Фон заголовка
menu_theme.title_font_color = WHITE  # Цвет шрифта заголовка
menu_theme.widget_font_color = WHITE  # Цвет текста для кнопок
menu_theme.widget_font = pygame.font.SysFont('Arial', 35)  # Шрифт для текста на кнопках
menu_theme.widget_background_color = DARK_GREY  # Цвет фона кнопок
menu_theme.widget_border_color = DARKER_GREY  # Цвет границ кнопок
menu_theme.widget_border_width = 2  # Толщина границ кнопок
menu_theme.widget_selected_background_color = LIGHT_GREY  # Цвет фона кнопки при наведении
menu_theme.widget_selected_font_color = DARKER_GREY  # Цвет текста кнопки при наведении

# Создаем экран и меню
screen = pygame.display.set_mode((WIDTH, HEIGHT))
menu = pygame_menu.Menu("Main Menu", WIDTH, HEIGHT, theme=menu_theme)

# Кнопки в меню
menu.add.button("Играть", start_game)
menu.add.button("Магазин", open_shop)
menu.add.button("Настройки", open_settings)
menu.add.button("Выйти", exit_game)
