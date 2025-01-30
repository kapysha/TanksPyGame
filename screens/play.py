import sys
import time
import pygame
from database.queries import update_battle_stats
from game_logic.generate_maze import grid_cells, Wall
from game_logic.ai_tank import build_graph, AITank
from launcher import switch_screen
from screens.menu import Button, menu
from game_logic.tank import Tank
from game_logic.generate_maze import generate_maze
from config.settings import all_sprites, players_group, cols, rows, bullets_group, ai_group, kill_sound, WIDTH, HEIGHT, \
    WHITE, clock, ringtone
from effects.particle import Explosion, Particle


def play():
    ringtone.stop()
    image_player_tank = Explosion.load_image_with_color('assets/images/tank_player.png', (70, 255, 0, 0))
    image_ai_tank = Explosion.load_image_with_color('assets/images/tank_ai.png', (152, 51, 51, 0))

    FONT = pygame.font.Font(None, 40)
    PLAYER_WINS = 0
    AI_WINS = 0
    BATTLE_START_TIME = time.time()

    screen = pygame.Surface((WIDTH, HEIGHT))

    big_screen_size = (WIDTH + 20, HEIGHT + 100)
    big_screen = pygame.display.set_mode(big_screen_size)

    offset_x = (big_screen_size[0] - WIDTH) // 2
    offset_y = 10

    generate_maze()  # Генерация лабиринта
    graph = build_graph(grid_cells, cols, rows)
    tank = Tank(all_sprites, players_group)
    ai_tank = AITank(graph, tank)

    frozen = False
    freeze_start_time = None
    freeze_duration = 3

    def exit_play():
        nonlocal running, tank, ai_tank
        tank.kill()
        ai_tank.kill()

        # очищаем все пульки с поля
        for bullet in bullets_group:
            bullet.kill()

        # очищаем все стены
        for sprite in all_sprites:
            if isinstance(sprite, (Wall, Particle)):
                sprite.kill()

        running = False
        return switch_screen(menu)

    exit_button = Button(x=10, y=big_screen_size[1] - 40, width=80, height=30, text="Выйти", color=(128, 128, 128),
                         hover_color=(160, 160, 160), text_color=WHITE, action=exit_play,
                         text_size=28)  # Кнопка выхода с игры

    def reset_battle():
        nonlocal tank, ai_tank, graph, BATTLE_START_TIME
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

        BATTLE_START_TIME = time.time()

    running = True
    while running:
        current_delta_time = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and not frozen:
                tank.fire_bullet(owner='player')

            exit_button.check_hover(pygame.mouse.get_pos())
            exit_button.handle_event(event)

        if frozen:
            ai_tank.fix()
            if time.time() - freeze_start_time >= freeze_duration:
                frozen = False
                reset_battle()

            all_sprites.update(current_delta_time, None)
        else:
            all_sprites.update(current_delta_time, pygame.key.get_pressed())

            for bullet in bullets_group:
                current_time = pygame.time.get_ticks()

                if bullet.owner == 'player' and pygame.sprite.spritecollideany(bullet, players_group):
                    if current_time < bullet.invulnerable_time:
                        continue  # Игнорируем попадание в своего танка

                if bullet.owner == 'ai' and pygame.sprite.spritecollideany(bullet, ai_group):
                    if current_time < bullet.invulnerable_time:
                        continue  # Игнорируем попадание в своего же AI

                killed = False
                if bullet.owner == 'player':
                    if pygame.sprite.spritecollide(bullet, ai_group, False):
                        pos = ai_tank.pos
                        ai_tank.kill()
                        bullet.kill()
                        kill_sound.play()
                        Explosion(pos, (152, 51, 51, 0))
                        PLAYER_WINS += 1
                        killed = True

                    elif pygame.sprite.spritecollide(bullet, players_group, False):
                        pos = tank.pos
                        tank.kill()
                        bullet.kill()
                        kill_sound.play()
                        Explosion(pos, (70, 255, 0, 0))
                        AI_WINS += 1
                        killed = True

                elif bullet.owner == 'ai':
                    if pygame.sprite.spritecollide(bullet, players_group, False):
                        pos = tank.pos
                        tank.kill()
                        bullet.kill()
                        kill_sound.play()
                        Explosion(pos, (70, 255, 0, 0))
                        AI_WINS += 1
                        killed = True

                    elif pygame.sprite.spritecollide(bullet, ai_group, False):
                        pos = ai_tank.pos
                        ai_tank.kill()
                        bullet.kill()
                        kill_sound.play()
                        Explosion(pos, (152, 51, 51, 0))
                        PLAYER_WINS += 1
                        killed = True

                if killed:
                    frozen = True
                    freeze_start_time = time.time()
                    for b in bullets_group:
                        b.kill()
                    battle_duration = time.time() - BATTLE_START_TIME
                    update_battle_stats('player' if bullet.owner == 'player' else 'ai', battle_duration)

        screen.fill(pygame.Color('lightgrey'))
        all_sprites.draw(screen)

        big_screen.fill('grey')
        big_screen.blit(screen, (offset_x, offset_y))
        big_screen.blit(image_player_tank, (WIDTH * 0.65, HEIGHT + 20))
        big_screen.blit(image_ai_tank, (WIDTH * 0.2, HEIGHT + 20))

        player_score_text = FONT.render(str(PLAYER_WINS), True, pygame.Color('black'))
        ai_score_text = FONT.render(str(AI_WINS), True, pygame.Color('black'))

        big_screen.blit(player_score_text, (WIDTH * 0.65 - 20, HEIGHT + 50))
        big_screen.blit(ai_score_text, (WIDTH * 0.2 + 105, HEIGHT + 50))

        exit_button.draw(big_screen)
        pygame.display.flip()
