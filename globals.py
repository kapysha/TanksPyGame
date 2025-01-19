import pygame

RES = WIDTH, HEIGHT = 720, 720
TILE = 90
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
