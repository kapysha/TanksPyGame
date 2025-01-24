from collections import deque
import pygame
from globals import load_image, all_sprites, ai_group, TILE, walls_group_horizontal, walls_group_vertical
from tank import Tank


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
    image, original_image, mask = load_image('tanks/tank_1.png', (152, 51, 51, 0))

    def __init__(self, graph, target):
        super().__init__(all_sprites, ai_group)
        self.fire_frames = [load_image('tanks/tank_1.png', (152, 51, 51, 0))[0],
                            load_image('tanks/tank_2.png', (152, 51, 51, 0))[0],
                            load_image('tanks/tank_3.png', (152, 51, 51, 0))[0]]
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
        self.shooting_angle_threshold = 60  # Градусы
        self.shoot_cooldown = 0.4
        self.time_since_last_shot = 0.0  # Таймер

        # Скорость танка
        self.movement_speed = 200
        # Скорость поворота
        self.rotation_speed = 230

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
                angle = 1
            else:
                angle = 5

            desired_angle = direction_vector.angle_to(
                pygame.math.Vector2(0, -1))  # под каким углом направлен direction_vector относительно "вверх"
            angle_diff = (desired_angle - self.angle + 180) % 360 - 180  # Чтобы в диапазоне от 180 до -180

            if angle_diff > angle:
                self.rotate('left', delta_time)
            elif angle_diff < -angle:
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
        if not self.target.alive():
            return  # Не делаем ничего, если цель уничтожена

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

        super().update(delta_time, None)

    def distance_to_player(self):
        return (self.pos - self.target.pos).length()
