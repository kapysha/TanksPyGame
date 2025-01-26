from config.settings import walls_group_horizontal, walls_group_vertical, all_sprites, bullets_group
import pygame


class Bullets(pygame.sprite.Sprite):
    def __init__(self, pos, angle, owner=None):
        super().__init__(all_sprites, bullets_group)
        self.radius = 4
        self.color = pygame.Color(54, 53, 51)
        self.speed = 300
        self.owner = owner

        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.pos = pygame.math.Vector2(pos)
        self.velocity = pygame.math.Vector2(0, -1).rotate(-angle) * self.speed

        self.spawn_time = pygame.time.get_ticks() + 9000

    def update(self, delta_time, _):
        if pygame.time.get_ticks() >= self.spawn_time:
            self.kill()

        self.pos += self.velocity * delta_time
        self.rect.center = self.pos

        if pygame.sprite.spritecollideany(self, walls_group_horizontal):
            self.velocity.x *= -1
        if pygame.sprite.spritecollideany(self, walls_group_vertical):
            self.velocity.y *= -1
