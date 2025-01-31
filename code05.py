import pygame
import random
import subprocess
import sys

# Константы
N = 15
CELL_SIZE = 40
MAZE_WIDTH, MAZE_HEIGHT = 600, 600
UI_WIDTH = 200
WIDTH, HEIGHT = MAZE_WIDTH + UI_WIDTH, MAZE_HEIGHT
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 200, 0)
BLUE = (0, 128, 255)
DIRECTIONS = [(-2, 0), (2, 0), (0, -2), (0, 2)]

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Infinite Maze ver 0.5")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Загрузка текстур
brick_texture = pygame.image.load("brick.png")
brick_texture = pygame.transform.scale(brick_texture, (CELL_SIZE, CELL_SIZE))

pacman_sprites = {
    "right": [pygame.image.load("pacman_closed.png"), pygame.image.load("pacman_half.png"), pygame.image.load("pacman_open.png")],
    "left": [], "up": [], "down": []
}

# Создание зеркальных спрайтов для направления
pacman_sprites["left"] = [pygame.transform.flip(sprite, True, False) for sprite in pacman_sprites["right"]]
pacman_sprites["up"] = [pygame.transform.rotate(sprite, 90) for sprite in pacman_sprites["right"]]
pacman_sprites["down"] = [pygame.transform.rotate(sprite, -90) for sprite in pacman_sprites["right"]]

# Масштабирование
for direction in pacman_sprites:
    pacman_sprites[direction] = [pygame.transform.scale(sprite, (CELL_SIZE, CELL_SIZE)) for sprite in pacman_sprites[direction]]


class Maze:
    """Класс для генерации лабиринта"""

    def __init__(self, size=N):
        self.size = size
        self.maze = [['#' for _ in range(size)] for _ in range(size)]

    def is_valid_move(self, x, y):
        """Проверяет, можно ли двигаться в данном направлении"""
        return 0 <= x < self.size and 0 <= y < self.size and self.maze[x][y] == '#'

    def generate(self, game):
        """Генерация лабиринта с анимацией"""
        self.maze = [['#' for _ in range(self.size)] for _ in range(self.size)]
        start_x, start_y = random.randrange(1, self.size, 2), random.randrange(1, self.size, 2)
        game.pacman.set_position(start_x, start_y)
        stack = [(start_x, start_y)]
        self.maze[start_x][start_y] = ' '

        while stack:
            x, y = stack[-1]
            directions = [(dx, dy) for dx, dy in DIRECTIONS if self.is_valid_move(x + dx, y + dy)]

            if directions:
                dx, dy = random.choice(directions)
                self.maze[x + dx // 2][y + dy // 2] = ' '
                self.maze[x + dx][y + dy] = ' '
                stack.append((x + dx, y + dy))
            else:
                stack.pop()

            game.draw_maze()
            pygame.time.delay(20)


class Pacman:
    """Класс для управления Pac-Man'ом"""

    def __init__(self, maze):
        self.x, self.y = 1, 1
        self.frame = 0
        self.maze = maze
        self.direction = "right"
        self.moving = False

    def set_position(self, x, y):
        """Устанавливает позицию Pac-Man'а"""
        self.x, self.y = x, y

    def move(self):
        """Перемещение Pac-Man'а"""
        if not self.moving:
            return

        dx, dy = 0, 0
        if self.direction == "up": dx, dy = -1, 0
        elif self.direction == "down": dx, dy = 1, 0
        elif self.direction == "left": dx, dy = 0, -1
        elif self.direction == "right": dx, dy = 0, 1

        new_x, new_y = self.x + dx, self.y + dy
        if 0 <= new_x < N and 0 <= new_y < N and self.maze.maze[new_x][new_y] == ' ':
            self.x, self.y = new_x, new_y
        else:
            self.moving = False

    def get_sprite(self):
        """Анимация Pac-Man'а"""
        self.frame = (self.frame + 1) % len(pacman_sprites["right"])
        return pacman_sprites[self.direction][self.frame]


class Game:
    """Класс для управления игровым процессом"""

    def __init__(self):
        self.maze = Maze(N)
        self.pacman = Pacman(self.maze)
        self.generate_button = None
        self.menu_button = None
        self.create_ui()
        self.maze.generate(self)

    def draw_maze(self):
        """Отрисовка лабиринта"""
        screen.fill(BLACK, (0, 0, MAZE_WIDTH, MAZE_HEIGHT))
        for i in range(N):
            for j in range(N):
                if self.maze.maze[i][j] == ' ':
                    pygame.draw.rect(screen, GRAY, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                else:
                    screen.blit(brick_texture, (j * CELL_SIZE, i * CELL_SIZE))

        # Отрисовка Pac-Man'а
        screen.blit(self.pacman.get_sprite(), (self.pacman.y * CELL_SIZE, self.pacman.x * CELL_SIZE))
        pygame.display.flip()

    def create_ui(self):
        """Создание UI"""
        pygame.draw.rect(screen, BLACK, (MAZE_WIDTH, 0, UI_WIDTH, HEIGHT))

        # Кнопка "GENERATE"
        self.generate_button = pygame.Rect(MAZE_WIDTH + 30, 50, 145, 40)
        pygame.draw.rect(screen, GREEN, self.generate_button)
        text = font.render("GENERATE", True, WHITE)
        screen.blit(text, (MAZE_WIDTH + 35, 60))

        # Кнопка "Главное меню"
        self.menu_button = pygame.Rect(MAZE_WIDTH + 10, 120, 180, 40)
        pygame.draw.rect(screen, BLUE, self.menu_button)
        menu_text = font.render("Главное меню", True, WHITE)
        screen.blit(menu_text, (MAZE_WIDTH + 15, 130))

    def run(self):
        """Запуск игрового цикла"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.generate_button.collidepoint(event.pos):
                        self.maze.generate(self)
                        self.create_ui()
                    elif self.menu_button.collidepoint(event.pos):  # Проверяем клик по кнопке меню
                        pygame.quit()  # Закрываем игру
                        subprocess.run(["python", "main_menu.py"])  # Запускаем главное меню
                        sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d):
                        directions = {
                            pygame.K_w: "up",
                            pygame.K_s: "down",
                            pygame.K_a: "left",
                            pygame.K_d: "right"
                        }
                        self.pacman.direction = directions[event.key]
                        self.pacman.moving = True

            self.pacman.move()
            self.draw_maze()
            pygame.display.flip()
            clock.tick(10)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
