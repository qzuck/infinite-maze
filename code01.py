import pygame
import random

# Константы
N = 15
CELL_SIZE = 40
WIDTH, HEIGHT = N * CELL_SIZE, N * CELL_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DIRECTIONS = [(-2, 0), (2, 0), (0, -2), (0, 2)]

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Generator")
clock = pygame.time.Clock()


class Maze:
    """Класс для генерации лабиринта"""
    
    def __init__(self, size=N):
        self.size = size
        self.maze = [['#' for _ in range(size)] for _ in range(size)]

    def is_valid_move(self, x, y):
        """Проверяет, можно ли двигаться в данном направлении"""
        return 0 <= x < self.size and 0 <= y < self.size and self.maze[x][y] == '#'

    def generate(self, start_x, start_y, game):
        """Создаёт лабиринт с анимацией"""
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

            game.draw_maze()  # Отрисовываем лабиринт на каждом шаге
            pygame.time.delay(20)  # Небольшая задержка для анимации


class Game:
    """Класс, управляющий отрисовкой и игровым циклом"""

    def __init__(self):
        self.maze = Maze(N)
        self.start_x = random.randrange(1, N, 2)
        self.start_y = random.randrange(1, N, 2)

    def draw_maze(self):
        """Отрисовка лабиринта"""
        screen.fill(BLACK)
        for i in range(N):
            for j in range(N):
                if self.maze.maze[i][j] == ' ':
                    pygame.draw.rect(screen, WHITE, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.display.flip()

    def run(self):
        """Главный игровой цикл"""
        self.maze.generate(self.start_x, self.start_y, self)  # Генерация с анимацией
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            clock.tick(30)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
