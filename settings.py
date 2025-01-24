import pygame

SIZE = WIDTH, HEIGHT = 630, 630
SIZE_MENU = WIDTH_MENU, HEIGHT_MENU = 650, 640
TILE = 89
cols, rows = WIDTH // TILE, HEIGHT // TILE

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

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
LIGHT_GRAY = (230, 230, 230)


def load_image(path: str, rgb: tuple):
    image = pygame.image.load(path)
    image = image.convert()
    colorkey = image.get_at((0, 0))
    image.set_colorkey(colorkey)
    green_overlay = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    green_overlay.fill(rgb)  # (R, G, B, A) – A=100 для прозрачности
    image.blit(green_overlay, (0, 0), special_flags=3)
    original_image = image.copy()
    mask = pygame.mask.from_surface(image)
    return image, original_image, mask
