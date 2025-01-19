import pygame

RES = WIDTH, HEIGHT = 630, 630
TILE = 89
cols, rows = WIDTH // TILE, HEIGHT // TILE

pygame.init()
screen = pygame.display.set_mode(RES)
pygame.display.set_caption('Танчики')
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
players_group = pygame.sprite.Group()
walls_group_horizontal = pygame.sprite.Group()
walls_group_vertical = pygame.sprite.Group()
ai_group = pygame.sprite.Group()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
bullet_sound = pygame.mixer.Sound('sounds/bullet.ogg')
kill_sound = pygame.mixer.Sound('sounds/kill.ogg')


def load_image(path: str, rgb: tuple):
    image = pygame.image.load(path).convert_alpha()
    image.set_colorkey((255, 255, 255))
    green_overlay = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    green_overlay.fill(rgb)  # (R, G, B, A) – A=100 для прозрачности
    image.blit(green_overlay, (0, 0), special_flags=3)
    original_image = image.copy()
    mask = pygame.mask.from_surface(image)
    return image, original_image, mask
