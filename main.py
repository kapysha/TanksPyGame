import pygame

RES = WIDTH, HEIGHT = 720, 720
TILE = 90
cols, rows = WIDTH // TILE, HEIGHT // TILE

pygame.init()
pygame.display.set_caption('Танчики')
clock = pygame.time.Clock()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

all_sprites = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
players_group = pygame.sprite.Group()
walls_group_horizontal = pygame.sprite.Group()
walls_group_vertical = pygame.sprite.Group()
ai_group = pygame.sprite.Group()
bullet_sound = pygame.mixer.Sound('sounds/bullet.ogg')


def load_image(path: str, rgb: tuple):
    image = pygame.image.load(path).convert_alpha()
    image.set_colorkey((255, 255, 255))
    image = pygame.transform.scale(image, (31, 52))
    green_overlay = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    green_overlay.fill(rgb)  # (R, G, B, A) – A=100 для прозрачности
    image.blit(green_overlay, (0, 0), special_flags=3)
    original_image = image.copy()
    mask = pygame.mask.from_surface(image)
    return image, original_image, mask


def main():
    screen = pygame.display.set_mode(RES)

    from ai_tank import build_graph, AITank
    from generate_maze import grid_cells
    from tank import Tank
    from generate_maze import generate_maze

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
