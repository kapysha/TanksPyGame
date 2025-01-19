import pygame
from generate_maze import grid_cells
from ai_tank import build_graph, AITank
from tank import Tank
from generate_maze import generate_maze
from globals import all_sprites, players_group, bullets_group, ai_group, cols, rows, screen, clock


def main():
    generate_maze()

    for cell in grid_cells:
        cell.draw()

    graph = build_graph(grid_cells, cols, rows)

    tank = Tank(all_sprites, players_group)
    AITank(graph, tank)

    running = True
    while running:
        current_delta_time = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    tank.fire_bullet(owner='player')

        all_sprites.update(current_delta_time, pygame.key.get_pressed())

        for bullet in bullets_group:
            if bullet.owner == 'ai':
                if pygame.sprite.spritecollide(bullet, players_group, False):
                    print("В Игрока попали!")
                    bullet.kill()
            elif bullet.owner == 'player':
                if pygame.sprite.spritecollide(bullet, ai_group, False):
                    print("AI танк попали!")
                    bullet.kill()

        screen.fill(pygame.Color('lightgrey'))
        all_sprites.draw(screen)
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
