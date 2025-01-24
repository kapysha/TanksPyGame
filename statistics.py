import pygame
from launcher import switch_screen
from settings import LIGHT_GRAY, BLACK, SIZE_MENU
from menu import Button, menu

game_stats = {
    "total_battles": 0,
    "player_wins": 0,
    "ai_wins": 0,
    "player_shots": 0,
    "ai_shots": 0,
    "longest_battle_time": 0,
    "shortest_battle_time": 0,
}


def statistics():
    screen = pygame.display.set_mode(SIZE_MENU)

    running = True

    def exit_to_menu():
        nonlocal running
        running = False
        switch_screen(menu)

    font_title = pygame.font.Font(None, 60)
    font_text = pygame.font.Font(None, 36)

    title_text = font_title.render("Статистика", True, BLACK)
    title_rect = title_text.get_rect(center=(SIZE_MENU[0] // 2, 50))

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

        stats_text = [
            f"Всего боёв: {game_stats['total_battles']}",
            f"Победы игрока: {game_stats['player_wins']}",
            f"Победы AI: {game_stats['ai_wins']}",
            f"Выстрелы игрока: {game_stats['player_shots']}",
            f"Выстрелы AI: {game_stats['ai_shots']}",
            f"Самый длинный бой: {game_stats['longest_battle_time']} сек.",
            f"Самый короткий бой: {game_stats['shortest_battle_time']} сек." if game_stats[
                                                                                    'shortest_battle_time'] != float(
                'inf') else "Самый короткий бой: N/A",
        ]

        y_offset = 120
        for stat in stats_text:
            text_surface = font_text.render(stat, True, BLACK)
            screen.blit(text_surface, (50, y_offset))
            y_offset += 40

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit()

            back_button.handle_event(event)

        back_button.check_hover(pygame.mouse.get_pos())
        back_button.draw(screen)

        pygame.display.flip()
