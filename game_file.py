import sys
import time
import pygame
from generate_maze import grid_cells, Wall
from ai_tank import build_graph, AITank
from launcher import switch_screen
from menu_file import Button, menu
from tank import Tank
from generate_maze import generate_maze
from globals import all_sprites, players_group, cols, rows, bullets_group, ai_group, kill_sound, WIDTH, HEIGHT, \
    WHITE, clock
from particle import Explosion


def play():
    image_player_tank = Explosion.load_image_with_color('images/tank_player.png', (70, 255, 0, 0))
    image_ai_tank = Explosion.load_image_with_color('images/tank_ai.png', (152, 51, 51, 0))

    font = pygame.font.Font(None, 40)

    player_wins = 0
    ai_wins = 0

    generate_maze()

    base_screen_size = (WIDTH, HEIGHT)
    screen = pygame.Surface(base_screen_size)

    additional_width = 20
    additional_height = 100
    big_screen_size = (WIDTH + additional_width, HEIGHT + additional_height)
    big_screen = pygame.display.set_mode(big_screen_size)

    def exit_play():
        nonlocal running, tank, ai_tank
        tank.kill()
        ai_tank.kill()

        # очищаем все пульки с поля
        for bullet in bullets_group:
            bullet.kill()

        # очищаем все стены
        for sprite in all_sprites:
            if isinstance(sprite, Wall):
                sprite.kill()

        running = False
        return switch_screen(menu)

    exit_button = Button(
        x=10,
        y=big_screen_size[1] - 40,
        width=80,
        height=30,
        text="Выйти",
        color=(128, 128, 128),
        hover_color=(160, 160, 160),
        text_color=WHITE,
        action=exit_play,
        text_size=28
    )

    def reset_battle():
        nonlocal tank, ai_tank, graph
        tank.kill()
        ai_tank.kill()

        # очищаем все пульки с поля
        for bullet in bullets_group:
            bullet.kill()

        # очищаем все стены
        for sprite in all_sprites:
            if isinstance(sprite, Wall):
                sprite.kill()

        generate_maze()
        graph = build_graph(grid_cells, cols, rows)

        tank = Tank(all_sprites, players_group)
        ai_tank = AITank(graph, tank)

    graph = build_graph(grid_cells, cols, rows)
    tank = Tank(all_sprites, players_group)
    ai_tank = AITank(graph, tank)

    frozen = False
    freeze_start_time = None
    freeze_duration = 5

    running = True
    while running:
        current_delta_time = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not frozen:
                    tank.fire_bullet(owner='player')

            exit_button.check_hover(pygame.mouse.get_pos())
            exit_button.handle_event(event)

        if frozen:
            if time.time() - freeze_start_time >= freeze_duration:
                frozen = False
                reset_battle()
            all_sprites.update(current_delta_time, None)
            screen.fill(pygame.Color('lightgrey'))
            all_sprites.draw(screen)
        else:
            all_sprites.update(current_delta_time, pygame.key.get_pressed())

            for bullet in bullets_group:
                if bullet.owner == 'ai':
                    if pygame.sprite.spritecollide(bullet, players_group, False):
                        pos = tank.pos
                        tank.kill()
                        bullet.kill()
                        kill_sound.play()
                        Explosion(pos, (70, 255, 0, 0))
                        ai_wins += 1
                        frozen = True
                        freeze_start_time = time.time()

                elif bullet.owner == 'player':
                    if pygame.sprite.spritecollide(bullet, ai_group, False):
                        pos = ai_tank.pos
                        ai_tank.kill()
                        bullet.kill()
                        kill_sound.play()
                        Explosion(pos, (152, 51, 51, 0))
                        player_wins += 1
                        frozen = True
                        freeze_start_time = time.time()

            screen.fill(pygame.Color('lightgrey'))
            all_sprites.draw(screen)

        big_screen.fill('grey')

        offset_x = (big_screen_size[0] - WIDTH) // 2
        offset_y = 10

        big_screen.blit(screen, (offset_x, offset_y))

        big_screen.blit(image_player_tank, (WIDTH * 0.65, HEIGHT + 20))
        big_screen.blit(image_ai_tank, (WIDTH * 0.2, HEIGHT + 20))

        player_score_text = font.render(str(player_wins), True, pygame.Color('black'))
        ai_score_text = font.render(str(ai_wins), True, pygame.Color('black'))

        big_screen.blit(player_score_text, (WIDTH * 0.65 - 20, HEIGHT + 50))
        big_screen.blit(ai_score_text, (WIDTH * 0.2 + 105, HEIGHT + 50))

        exit_button.draw(big_screen)

        pygame.display.flip()
