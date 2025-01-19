from random import choice
from globals import all_sprites, walls_group_vertical, TILE, cols, rows, walls_group_horizontal
import pygame


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
