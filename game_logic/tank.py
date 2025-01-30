import random
import time
import pygame
from database.queries import add_shots
from game_logic.bullets import Bullets
from game_logic.generate_maze import Wall, grid_cells
from config.settings import load_image, all_sprites, players_group, ai_group, TILE, bullet_sound


class Tank(pygame.sprite.Sprite):
    image, original_image, mask = load_image('assets/tanks_images/tank_1.png', (70, 255, 0, 0))

    def __init__(self, *groups):
        super().__init__(*groups)
        self.fire_frames = [load_image('assets/tanks_images/tank_1.png', (70, 255, 0, 0))[0],
                            load_image('assets/tanks_images/tank_2.png', (70, 255, 0, 0))[0],
                            load_image('assets/tanks_images/tank_3.png', (70, 255, 0, 0))[0]]
        self.original_image = Tank.original_image
        self.image = self.original_image
        self.angle = 0
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(self.random_position())
        self.rect.center = self.pos
        self.mask = pygame.mask.from_surface(self.image)

        self.current_fire_frame = 0
        self.is_firing = False
        self.fire_animation_time = 0.05  # Время между кадрами анимации
        self.fire_timer = 0.0

        # Скорость танка
        self.movement_speed = 160
        # Скорость поворота
        self.rotation_speed = 220

        self.last_fire_time = 0.0  # Время последнего выстрела

    def check_collision(self, movement_vector) -> bool:
        new_pos = self.pos + movement_vector
        temp_sprite = pygame.sprite.Sprite()

        temp_sprite.image = pygame.transform.rotate(self.original_image, self.angle)
        temp_sprite.rect = temp_sprite.image.get_rect(center=new_pos)
        temp_sprite.mask = pygame.mask.from_surface(temp_sprite.image)

        for sprite in all_sprites:
            if isinstance(sprite, Wall):
                if pygame.sprite.collide_mask(temp_sprite, sprite):
                    return True

        all_tanks = pygame.sprite.Group(players_group, ai_group)

        for tank in all_tanks:
            if tank == self:
                continue  # Пропустить самого себя
            if pygame.sprite.collide_mask(temp_sprite, tank):
                return True

        return False  # Нет столкновения

    def random_position(self):
        available_cells = [
            cell for cell in grid_cells
            if not all(cell.walls.values())  # Клетка с хотя бы одним проходом
        ]
        for _ in range(100):
            random_cell = random.choice(available_cells)
            pos_x = random_cell.x * TILE + TILE // 2
            pos_y = random_cell.y * TILE + TILE // 2

            temp_pos = pygame.math.Vector2(pos_x, pos_y)

            temp_sprite = pygame.sprite.Sprite()
            temp_sprite.image = self.image
            temp_sprite.rect = temp_sprite.image.get_rect(center=temp_pos)
            temp_sprite.mask = pygame.mask.from_surface(temp_sprite.image)

            collision = False
            for sprite in all_sprites:
                if isinstance(sprite, Wall):
                    if pygame.sprite.collide_mask(temp_sprite, sprite):
                        collision = True

                if isinstance(sprite, Tank) and pygame.sprite.collide_mask(temp_sprite, sprite):
                    collision = True

            if not collision:
                return pos_x, pos_y

        return TILE // 2, TILE // 2

    def move(self, forward, delta_time):
        direction = 1 if not forward else -1

        movement_distance = direction * self.movement_speed * delta_time

        movement_vector = pygame.math.Vector2(0, movement_distance).rotate(-self.angle)

        dx, dy = movement_vector.x, movement_vector.y

        if not self.check_collision(pygame.math.Vector2(dx, 0)):
            self.pos.x += dx

        if not self.check_collision(pygame.math.Vector2(0, dy)):
            self.pos.y += dy

        self.rect.center = self.pos

    def rotate(self, direction, delta_time):
        rotation_step = self.rotation_speed * delta_time

        if direction == 'left':
            new_angle = (self.angle + rotation_step) % 360
        elif direction == 'right':
            new_angle = (self.angle - rotation_step) % 360

        temp_image = pygame.transform.rotate(self.original_image, new_angle)
        temp_sprite = pygame.sprite.Sprite()

        temp_sprite.image = temp_image
        temp_sprite.rect = temp_image.get_rect(center=self.rect.center)
        temp_sprite.mask = pygame.mask.from_surface(temp_image)

        collision = False
        for sprite in all_sprites:
            if isinstance(sprite, Wall):
                if pygame.sprite.collide_mask(temp_sprite, sprite):
                    collision = True
                    break

        if not collision:
            if direction == 'left':
                self.angle += rotation_step
            elif direction == 'right':
                self.angle -= rotation_step

            self.angle %= 360

            self.image = pygame.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)

            self.mask = pygame.mask.from_surface(self.image)

    def fire_bullet(self, owner='player'):
        current_time = time.time()
        if current_time - self.last_fire_time >= (0 if owner == 'ai' else 1.0):
            if not self.is_firing:
                self.is_firing = True
                self.current_fire_frame = 0
                self.fire_timer = 0.0

                offset = pygame.math.Vector2(0, -self.rect.height // 3).rotate(-self.angle)
                bullet_pos = self.pos + offset

                Bullets(bullet_pos, self.angle, owner=owner)
                add_shots(owner)
                bullet_sound.play()

                # Обновляем время последнего выстрела
                self.last_fire_time = current_time

    def update(self, delta_time, keys_pressed):
        if keys_pressed:
            if keys_pressed[pygame.K_UP] and not keys_pressed[pygame.K_DOWN]:
                self.move(forward=True, delta_time=delta_time)
            elif keys_pressed[pygame.K_DOWN] and not keys_pressed[pygame.K_UP]:
                self.move(forward=False, delta_time=delta_time)

            if keys_pressed[pygame.K_LEFT]:
                self.rotate('left', delta_time=delta_time)
            elif keys_pressed[pygame.K_RIGHT]:
                self.rotate('right', delta_time=delta_time)

        if self.is_firing:
            self.fire_timer += delta_time
            if self.fire_timer >= self.fire_animation_time:
                self.fire_timer -= self.fire_animation_time
                self.current_fire_frame += 1
                if self.current_fire_frame < len(self.fire_frames):
                    self.image = pygame.transform.rotate(self.fire_frames[self.current_fire_frame], self.angle)
                    self.rect = self.image.get_rect(center=self.rect.center)
                    self.mask = pygame.mask.from_surface(self.fire_frames[self.current_fire_frame])
                else:
                    self.is_firing = False
                    self.image = pygame.transform.rotate(self.original_image, self.angle)
                    self.rect = self.image.get_rect(center=self.rect.center)
                    self.mask = pygame.mask.from_surface(self.original_image)
