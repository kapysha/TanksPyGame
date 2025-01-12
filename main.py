import random
from collections import deque
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
players_group = pygame.sprite.Group()
walls_group_horizontal = pygame.sprite.Group()
walls_group_vertical = pygame.sprite.Group()
ai_group = pygame.sprite.Group()


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


def load_image(path: str):
    image = pygame.image.load(path).convert_alpha()
    image = pygame.transform.scale(image, (38, 53))
    original_image = image
    mask = pygame.mask.from_surface(image)
    return image, original_image, mask


class Tank(pygame.sprite.Sprite):
    image, original_image, mask = load_image('tanks/tank_1.png')

    def __init__(self, *groups):
        super().__init__(*groups)  # Modified
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
        self.is_moving = True
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

        if not self.is_moving_forward and self.is_moving:
            rotation_step = -rotation_step

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
        offset = pygame.math.Vector2(0, -self.rect.height // 3).rotate(-self.angle)
        bullet_pos = self.pos + offset

        Bullets(bullet_pos, self.angle, owner=owner)

    def update(self, delta_time, keys_pressed):
        self.is_moving = False

        if keys_pressed[pygame.K_UP] and not keys_pressed[pygame.K_DOWN]:
            self.move(forward=True, delta_time=delta_time)
        elif keys_pressed[pygame.K_DOWN] and not keys_pressed[pygame.K_UP]:
            self.move(forward=False, delta_time=delta_time)

        if keys_pressed[pygame.K_LEFT]:
            self.rotate('left', delta_time=delta_time)
        if keys_pressed[pygame.K_RIGHT]:
            self.rotate('right', delta_time=delta_time)


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


def build_graph(grid_cells, cols, rows):
    graph = {}
    for cell in grid_cells:
        x, y = cell.x, cell.y
        neighbors = []
        if not cell.walls['top'] and y > 0:
            neighbors.append((x, y - 1))
        if not cell.walls['bottom'] and y < rows - 1:
            neighbors.append((x, y + 1))
        if not cell.walls['left'] and x > 0:
            neighbors.append((x - 1, y))
        if not cell.walls['right'] and x < cols - 1:
            neighbors.append((x + 1, y))
        graph[(x, y)] = neighbors
    return graph


def find_path(graph, start, end):
    queue = deque([start])
    distances = {start: 0}  # расстояние
    predecessors = {start: None}  # хранит предшественника каждой вершины

    while queue:
        current = queue.popleft()
        if current == end:
            break
        for neighbor in graph.get(current, []):
            if neighbor not in distances:
                distances[neighbor] = distances[current] + 1
                predecessors[neighbor] = current
                queue.append(neighbor)

    if end not in predecessors:
        return None  # Путь не найден

    # Восстановление пути
    path = []
    current = end
    while current != start:
        path.append(current)
        current = predecessors[current]
    path.append(start)
    path.reverse()
    return path


class AITank(Tank):
    image, original_image, mask = load_image('tanks/tank_2.png')

    def __init__(self, graph, target):
        super().__init__(all_sprites, ai_group)

        self.original_image = AITank.original_image
        self.image = self.original_image
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=self.pos)

        self.graph = graph
        self.target = target
        self.path = []
        self.path_index = 0
        self.path_update_interval = 0.5  # Интервал обновления пути в секундах
        self.time_since_last_path = 0.0  # Таймер для обновления пути

        self.shooting_range = 350  # Пиксели
        self.shooting_angle_threshold = 20  # Градусы
        self.shoot_cooldown = 1.0
        self.time_since_last_shot = 0.0  # Таймер

    def find_grid_position(self, pos):
        x, y = int(pos.x // TILE), int(pos.y // TILE)
        return x, y

    def update_path(self):
        start = self.find_grid_position(self.pos)
        end = self.find_grid_position(self.target.pos)

        path = find_path(self.graph, start, end)
        if path:
            self.path = path[1:]
            self.path_index = 0
        else:
            self.path = []
            self.path_index = 0

    def follow_path(self, delta_time):
        if self.path and self.path_index < len(self.path):
            target_cell = self.path[self.path_index]
            target_pos = pygame.math.Vector2(
                target_cell[0] * TILE + TILE // 2,
                target_cell[1] * TILE + TILE // 2
            )

            direction_vector = target_pos - self.pos
            distance = direction_vector.length()

            if distance < 5:
                self.path_index += 1
                return

            desired_angle = direction_vector.angle_to(
                pygame.math.Vector2(0, -1))  # под каким углом направлен direction_vector относительно "вверх"
            angle_diff = (desired_angle - self.angle + 180) % 360 - 180  # Чтобы в диапазоне от 180 до -180

            if angle_diff > 5:
                self.rotate('left', delta_time)
            elif angle_diff < -5:
                self.rotate('right', delta_time)
            else:
                self.angle = desired_angle
                self.image = pygame.transform.rotate(self.original_image, self.angle)
                self.rect = self.image.get_rect(center=self.rect.center)
                self.mask = pygame.mask.from_surface(self.image)

                self.move(forward=True, delta_time=delta_time)

    def is_player_in_range(self):
        distance = self.distance_to_player()
        return distance <= self.shooting_range

    def is_barrel_aimed_at_player(self):
        direction_to_player = self.target.pos - self.pos
        desired_angle = direction_to_player.angle_to(pygame.math.Vector2(0, -1))
        angle_diff = (desired_angle - self.angle + 180) % 360 - 180
        return abs(angle_diff) <= self.shooting_angle_threshold

    def has_line_of_sight(self):
        start = self.pos
        end = self.target.pos

        direction = end - start
        distance = direction.length()

        direction = direction.normalize()

        for i in range(round(distance)):
            point = start + direction * i
            point_sprite = pygame.sprite.Sprite()
            point_sprite.rect = pygame.Rect(point.x, point.y, 2, 2)
            if pygame.sprite.spritecollideany(point_sprite, walls_group_horizontal) or \
                    pygame.sprite.spritecollideany(point_sprite, walls_group_vertical):
                return False  # Стена блокирует
        return True  # Нет стен

    def update(self, delta_time, keys_pressed):
        self.time_since_last_path += delta_time
        if self.time_since_last_path >= self.path_update_interval:
            self.update_path()
            self.time_since_last_path = 0.0

        self.follow_path(delta_time)

        self.time_since_last_shot += delta_time

        # Проверка условий для стрельбы
        # Игрок в радиусе
        # Ствол направлен на игрока и нет стен между AI и игроком
        if (self.is_player_in_range() and
            (self.is_barrel_aimed_at_player() and self.has_line_of_sight())) and \
                self.time_since_last_shot >= self.shoot_cooldown:
            self.fire_bullet(owner='ai')
            self.time_since_last_shot = 0.0

    def distance_to_player(self):
        return (self.pos - self.target.pos).length()


graph = build_graph(grid_cells, cols, rows)

for cell in grid_cells:
    cell.draw()

tank = Tank(all_sprites, players_group)

ai_tank = AITank(graph, tank)

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
