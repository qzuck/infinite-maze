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
pygame.display.set_caption("Infinite Maze ver 0.2")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)


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

            game.draw_maze()  # Отрисовка лабиринта на каждом шаге
            pygame.time.delay(20)


class Game:
    """Класс для управления игровым процессом"""

    def __init__(self):
        self.maze = Maze(N)
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
                    pygame.draw.rect(screen, WHITE, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.display.flip()

    def create_ui(self):
        """Создание UI"""
        pygame.draw.rect(screen, GRAY, (MAZE_WIDTH, 0, UI_WIDTH, HEIGHT))

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

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
