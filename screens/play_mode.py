import pygame
import sys
from config.settings import LIGHT_GRAY, BLACK, SIZE_MENU, switch_mode
from screens.menu import Button, menu
from launcher import switch_screen
from screens.play import play


def play_mode():
    screen = pygame.display.set_mode(SIZE_MENU)
    running = True

    # Текущая выбранная инструкция
    current_instruction = None

    def select_mode(mode: bool):
        nonlocal running
        running = False
        switch_mode(mode)
        return switch_screen(play)  # Заменить на экран игры или что-то другое

    # Заголовок
    font_title = pygame.font.Font(None, 60)
    title_text = font_title.render("Выберите режим игры", True, BLACK)
    title_rect = title_text.get_rect(center=(SIZE_MENU[0] // 2, SIZE_MENU[1] // 5))

    # Кнопки расположены по горизонтали
    easy_button = Button(
        x=SIZE_MENU[0] // 2 - 270,
        y=SIZE_MENU[1] // 2 - 40,
        width=250,
        height=60,
        text="Простой",
        color=(200, 200, 200),
        hover_color=(170, 170, 170),
        text_color=BLACK,
        action=lambda: select_mode(False)
    )

    hard_button = Button(
        x=SIZE_MENU[0] // 2 + 15,
        y=SIZE_MENU[1] // 2 - 40,
        width=250,
        height=60,
        text="Сложный",
        color=(200, 200, 200),
        hover_color=(170, 170, 170),
        text_color=BLACK,
        action=lambda: select_mode(True)
    )

    # Кнопка "В меню"
    def return_to_menu():
        nonlocal running
        running = False
        return switch_screen(menu)

    menu_button = Button(
        x=10,
        y=SIZE_MENU[1] - 40,
        width=80,
        height=30,
        text="В меню",
        color=(200, 200, 200),
        hover_color=(170, 170, 170),
        text_color=BLACK,
        action=return_to_menu,
        text_size=26
    )

    # Текст инструкций
    font_instruction = pygame.font.Font(None, 36)

    easy_text = [
        "Простой режим:",
        "  • Ваши пули вас не убивают.",
        "  • Бот не получает урон от своих пуль."
    ]

    hard_text = [
        "Сложный режим:",
        "  • Ваши пули могут убить вас.",
        "  • Бот не получает урон от своих пуль.",
        "  • Бот быстрее движется, стреляет и поворачивает."
    ]

    # Функция отрисовки текста
    def draw_instructions(text, y_offset):
        for line in text:
            text_surface = font_instruction.render(line, True, BLACK)
            screen.blit(text_surface, (30, y_offset))
            y_offset += 40

    while running:
        screen.fill(LIGHT_GRAY)

        screen.blit(title_text, title_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            easy_button.handle_event(event)
            hard_button.handle_event(event)
            menu_button.handle_event(event)

        # Проверяем, на какой кнопке находимся
        if easy_button.is_hovered:
            current_instruction = easy_text
        elif hard_button.is_hovered:
            current_instruction = hard_text

        # Отрисовка кнопок
        easy_button.check_hover(pygame.mouse.get_pos())
        hard_button.check_hover(pygame.mouse.get_pos())
        menu_button.check_hover(pygame.mouse.get_pos())
        easy_button.draw(screen)
        hard_button.draw(screen)
        menu_button.draw(screen)

        if current_instruction:
            draw_instructions(current_instruction, SIZE_MENU[1] // 2 + 80)

        pygame.display.flip()
