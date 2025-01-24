import pygame
from launcher import switch_screen
from globals import LIGHT_GRAY, BLACK, SIZE_MENU
from menu_file import menu, Button


def instructions():
    screen = pygame.display.set_mode(SIZE_MENU)
    pygame.display.set_caption("Инструкция")

    running = True

    def exit_to_menu():
        nonlocal running
        running = False
        switch_screen(menu)

    font_title = pygame.font.Font(None, 60)
    font_text = pygame.font.Font(None, 36)
    font_bold = pygame.font.Font(None, 40)

    title_text = font_title.render("Инструкция", True, BLACK)
    title_rect = title_text.get_rect(center=(SIZE_MENU[0] // 2, 50))

    instructions_text = [
        "• Ездить: стрелочки на клавиатуре",
        "• Стрелять: пробел",
        "",
        "• Режимы игры:",
        "  • Простой:",
        "    — Ваши пульки вас не убивают.",
        "    — AI не получает урон от своих пуль.",
        "  • Сложный:",
        "    — Ваши пульки вас убивают.",
        "    — AI не получает урон от своих пуль."
    ]

    back_button = Button(
        x=SIZE_MENU[0] // 2 - 100,
        y=SIZE_MENU[1] - 70,
        width=200,
        height=50,
        text="Назад",
        color=(200, 200, 200),
        hover_color=(170, 170, 170),
        text_color=BLACK,
        action=exit_to_menu,
    )

    while running:
        screen.fill(LIGHT_GRAY)
        screen.blit(title_text, title_rect)

        # Отрисовка текста инструкции
        y_offset = 100
        for i, line in enumerate(instructions_text):
            is_bold = line.startswith("  •") or line.startswith("• Режимы игры:")
            font = font_bold if is_bold else font_text
            text_surface = font.render(line, True, BLACK)
            screen.blit(text_surface, (50, y_offset))
            y_offset += 40 if line else 20  # Увеличиваем отступ для пустых строк

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit()

            back_button.handle_event(event)

        back_button.check_hover(pygame.mouse.get_pos())
        back_button.draw(screen)

        pygame.display.flip()
