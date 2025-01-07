import random
import pygame
from random import choice

RES = WIDTH, HEIGHT = 630, 630
TILE = 90
cols, rows = WIDTH // TILE, HEIGHT // TILE

pygame.init()
screen = pygame.display.set_mode(RES)
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
tanks_group = pygame.sprite.Group()
walls_group_horizontal = pygame.sprite.Group()
walls_group_vertical = pygame.sprite.Group()


class Wall(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        width = abs(x2 - x1) or 3
        if width == 3:
            self.add(walls_group_horizontal)

        height = abs(y2 - y1) or 3
        if height == 3:
            self.add(walls_group_vertical)

        self.image = pygame.Surface((width, height))
        self.image.fill(pygame.Color('black'))

        self.rect = self.image.get_rect()
        self.rect.topleft = (min(x1, x2), min(y1, y2))

        self.mask = pygame.mask.from_surface(self.image)


class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def draw(self):
        x, y = self.x * TILE, self.y * TILE

        if self.walls['top']:
            Wall(x, y, x + TILE, y)
        if self.walls['right']:
            Wall(x + TILE, y, x + TILE, y + TILE)
        if self.walls['bottom']:
            Wall(x + TILE, y + TILE, x, y + TILE)
        if self.walls['left']:
            Wall(x, y + TILE, x, y)

    def check_cell(self, x, y):
        if x < 0 or x >= cols or y < 0 or y >= rows:
            return False
        return grid_cells[x + y * cols]

    def check_neighbors(self):
        neighbors = []
        top = self.check_cell(self.x, self.y - 1)
        right = self.check_cell(self.x + 1, self.y)
        bottom = self.check_cell(self.x, self.y + 1)
        left = self.check_cell(self.x - 1, self.y)
        if top and not top.visited:
            neighbors.append(top)
        if right and not right.visited:
            neighbors.append(right)
        if bottom and not bottom.visited:
            neighbors.append(bottom)
        if left and not left.visited:
            neighbors.append(left)
        return choice(neighbors) if neighbors else False


def remove_walls(current, next_cell):
    dx = current.x - next_cell.x
    if dx == 1:
        current.walls['left'] = False
        next_cell.walls['right'] = False
    elif dx == -1:
        current.walls['right'] = False
        next_cell.walls['left'] = False
    dy = current.y - next_cell.y
    if dy == 1:
        current.walls['top'] = False
        next_cell.walls['bottom'] = False
    elif dy == -1:
        current.walls['bottom'] = False
        next_cell.walls['top'] = False


grid_cells = [Cell(col, row) for row in range(rows) for col in range(cols)]
current_cell = grid_cells[0]
stack = []


def generate_maze():
    global current_cell
    current_cell.visited = True
    next_cell = current_cell.check_neighbors()
    while True:
        if next_cell:
            next_cell.visited = True
            stack.append(current_cell)
            remove_walls(current_cell, next_cell)
            current_cell = next_cell
            next_cell = current_cell.check_neighbors()
        elif stack:
            current_cell = stack.pop()
            next_cell = current_cell.check_neighbors()
        else:
            break


generate_maze()  # Генерация лабиринта перед началом игры


class Tank(pygame.sprite.Sprite):
    image = pygame.image.load('tanks/tank_1.png').convert_alpha()
    image = pygame.transform.scale(image, (38, 53))
    original_image = image
    mask = pygame.mask.from_surface(image)

    def __init__(self):
        super().__init__(all_sprites, tanks_group)  # Modified
        self.original_image = Tank.original_image
        self.image = self.original_image
        self.angle = 0
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(self.random_position())
        self.rect.center = self.pos
        self.is_moving_forward = True  # для отслеживания направления движения
        self.mask = pygame.mask.from_surface(self.image)

        # Скорость танка
        self.movement_speed = 150
        # Скорость поворота
        self.rotation_speed = 210

    def check_collision(self, movement_vector) -> bool:
        """Проверяет, есть ли столкновение с другими спрайтами с использованием масок"""
        new_pos = self.pos + movement_vector
        temp_rect = self.image.get_rect(center=new_pos)
        temp_sprite = pygame.sprite.Sprite()

        temp_sprite.image = self.image
        temp_sprite.rect = temp_rect
        temp_sprite.mask = self.mask

        for sprite in all_sprites:
            if isinstance(sprite, Wall):
                if pygame.sprite.collide_mask(temp_sprite, sprite):
                    return True  # Есть столкновение
        return False  # Нет столкновения

    def random_position(self):
        available_cells = [
            cell for cell in grid_cells
            if not all(cell.walls.values())  # Клетка с хотя бы одним проходом
        ]
        if available_cells:
            for _ in range(100):
                random_cell = random.choice(available_cells)
                pos_x = random_cell.x * TILE + TILE // 2
                pos_y = random_cell.y * TILE + TILE // 2

                temp_pos = pygame.math.Vector2(pos_x, pos_y)

                temp_sprite = pygame.sprite.Sprite()
                temp_sprite.image = self.image
                temp_sprite.rect = self.image.get_rect(center=temp_pos)
                temp_sprite.mask = self.mask

                collision = False
                for sprite in all_sprites:
                    if isinstance(sprite, Wall):
                        if pygame.sprite.collide_mask(temp_sprite, sprite):
                            collision = True
                            break

                if not collision:
                    return pos_x, pos_y

            return TILE // 2, TILE // 2
        return TILE // 2, TILE // 2

    def move(self, forward, delta_time):
        direction = 1 if not forward else -1
        self.is_moving_forward = forward

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

        if not self.is_moving_forward:
            rotation_step = -rotation_step

        if direction == 'left':
            new_angle = (self.angle + rotation_step) % 360
        elif direction == 'right':
            new_angle = (self.angle - rotation_step) % 360
        else:
            return  # Неправильное направление

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

    def fire_bullet(self):
        offset = pygame.math.Vector2(0, -self.rect.height // 3).rotate(-self.angle)
        bullet_pos = self.pos + offset

        Bullets(bullet_pos, self.angle)

    def update(self, delta_time, keys_pressed):
        if keys_pressed[pygame.K_UP] and not keys_pressed[pygame.K_DOWN]:
            self.move(forward=True, delta_time=delta_time)
        elif keys_pressed[pygame.K_DOWN] and not keys_pressed[pygame.K_UP]:
            self.move(forward=False, delta_time=delta_time)

        if keys_pressed[pygame.K_LEFT]:
            self.rotate('left', delta_time=delta_time)
        if keys_pressed[pygame.K_RIGHT]:
            self.rotate('right', delta_time=delta_time)


class Bullets(pygame.sprite.Sprite):
    def __init__(self, pos, angle):
        super().__init__(all_sprites, bullets_group)
        self.radius = 4
        self.color = pygame.Color(54, 53, 51)
        self.speed = 300

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


tank = Tank()
for cell in grid_cells:
    cell.draw()

running = True
while running:
    current_delta_time = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                tank.fire_bullet()

    all_sprites.update(current_delta_time, pygame.key.get_pressed())

    screen.fill(pygame.Color('lightgrey'))
    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
