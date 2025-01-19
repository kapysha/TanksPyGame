import pygame
import random
from globals import all_sprites


class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, fragment_images):
        super().__init__(all_sprites)
        self.image = random.choice(fragment_images)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)
        self.velocity = pygame.math.Vector2(
            random.uniform(-1, 1), random.uniform(-1, 1)
        ).normalize() * random.uniform(20, 30)  # Скорость от 20 до 30 пикселей
        self.lifetime = random.uniform(0.5, 1.5)  # Время жизни частицы
        self.spawn_time = pygame.time.get_ticks()

    def update(self, delta_time, _):
        self.pos += self.velocity * delta_time
        self.rect.center = self.pos

        if pygame.time.get_ticks() - self.spawn_time > self.lifetime * 1000:
            self.kill()


class Explosion:
    def __init__(self, pos, rgb: tuple[int, int, int, int]):
        self.particles = []
        fragment_1 = self.load_image_with_color('fragments/fragment_1.png', rgb)
        fragment_2 = self.load_image_with_color('fragments/fragment_2.png', rgb)
        fragment_3 = self.load_image_with_color('fragments/fragment_3.png', rgb)
        fragment_images = [fragment_1, fragment_2, fragment_3]
        for _ in range(20):
            particle = Particle(pos, fragment_images)
            self.particles.append(particle)

    @staticmethod
    def load_image_with_color(path: str, rgb: tuple):
        image = pygame.image.load(path).convert_alpha()
        color_overlay = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        color_overlay.fill(rgb)  # (R, G, B, A)
        image.blit(color_overlay, (0, 0), special_flags=3)
        return image
