import pygame
import sys


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=(0, 0, 0), action=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.rect = pygame.Rect(x, y, width, height)
        self.is_hovered = False
        self.action = action

    def draw(self, screen):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect, border_radius=10)  # Скругленные углы
        pygame.draw.rect(screen, (50, 50, 50), self.rect, 2, border_radius=10)  # Граница кнопки

        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.action:
                self.action()


pygame.init()

WIDTH, HEIGHT = 630, 630
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ТАНКИ")

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
LIGHT_GRAY = (230, 230, 230)
background_color = pygame.image.load('images/background.png')
background_color = pygame.transform.scale(background_color, (WIDTH, HEIGHT))


def start_game():
    print("Начало игры")


def open_shop():
    print("Магазин открыт")


def view_statistics():
    print("Просмотр статистики")


def exit_game():
    pygame.quit()
    sys.exit()


def main_menu():
    start_button = Button(WIDTH / 2 - 125, 355, 250, 60, "Играть", LIGHT_GRAY, GRAY, text_color=BLACK,
                          action=start_game)
    shop_button = Button(WIDTH / 2 - 190, 425, 180, 60, "Магазин", LIGHT_GRAY, GRAY, text_color=BLACK, action=open_shop)
    statistics_button = Button(WIDTH / 2 + 5, 425, 180, 60, "Статистика", LIGHT_GRAY, GRAY, text_color=BLACK,
                               action=view_statistics)
    exit_button = Button(WIDTH / 2 - 125, 495, 250, 60, "Выйти", LIGHT_GRAY, GRAY, text_color=BLACK, action=exit_game)

    running = True
    while running:
        screen.blit(background_color, (0, 0))

        font = pygame.font.Font(None, 72)
        text_surface = font.render("ТАНКИ", True, BLACK)
        text_rect = text_surface.get_rect(center=(WIDTH / 2, 60))
        screen.blit(text_surface, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            for btn in [start_button, shop_button, statistics_button, exit_button]:
                btn.handle_event(event)

        for btn in [start_button, shop_button, statistics_button, exit_button]:
            btn.check_hover(pygame.mouse.get_pos())
            btn.draw(screen)

        pygame.display.flip()


main_menu()
