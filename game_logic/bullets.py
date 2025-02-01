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
        self.mask = pygame.mask.from_surface(self.image)  # Маска пули
        self.pos = pygame.math.Vector2(pos)
        self.velocity = pygame.math.Vector2(0, -1).rotate(-angle) * self.speed

        self.creation_time = pygame.time.get_ticks()  # Фиксируем время появления пули
        self.spawn_time = self.creation_time + 5000  # Время удаления пули через 5 сек
        self.invulnerable_time = self.creation_time + 115  # Неуязвимость в мс

    def update(self, delta_time, _):
        if pygame.time.get_ticks() >= self.spawn_time:
            self.kill()

        self.pos += self.velocity * delta_time
        self.rect.center = self.pos

        temp_sprite = pygame.sprite.Sprite()
        temp_sprite.image = self.image
        temp_sprite.rect = temp_sprite.image.get_rect(center=self.pos + self.velocity * delta_time)
        temp_sprite.mask = pygame.mask.from_surface(temp_sprite.image)

        for wall in walls_group_horizontal:
            if pygame.sprite.collide_mask(temp_sprite, wall):
                self.velocity.x *= -1
                break

        for wall in walls_group_vertical:
            if pygame.sprite.collide_mask(temp_sprite, wall):
                self.velocity.y *= -1
                break
