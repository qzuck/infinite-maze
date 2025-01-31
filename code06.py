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
YELLOW = (255, 255, 0)
BLUE = (0, 128, 255)
DIRECTIONS = [(-2, 0), (2, 0), (0, -2), (0, 2)]

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Infinite Maze ver 0.6")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Загрузка текстур и звуков
brick_texture = pygame.image.load("brick.png")
brick_texture = pygame.transform.scale(brick_texture, (CELL_SIZE, CELL_SIZE))

eat_sounds = [pygame.mixer.Sound("eat_dot_0.wav"), pygame.mixer.Sound("eat_dot_1.wav")]

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

class Pacman:
    """Класс для управления Pac-Man'ом"""

    def __init__(self, game):
        self.x, self.y = 1, 1
        self.frame = 0
        self.game = game  # Теперь у Pac-Man есть ссылка на объект Game
        self.direction = "right"
        self.moving = False
        self.score = 0

    def set_position(self, x, y):
        """Устанавливает позицию Pac-Man'а"""
        self.x, self.y = x, y

    def move(self):
        """Передвижение Pac-Man'а и обработка поедания точек"""
        if not self.moving:
            return

        dx, dy = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}[self.direction]
        new_x, new_y = self.x + dx, self.y + dy

        # Проверяем, можно ли двигаться в новую ячейку
        if 0 <= new_x < N and 0 <= new_y < N and self.game.maze.maze[new_x][new_y] == ' ':
            self.x, self.y = new_x, new_y  # Обновляем позицию Pac-Man'а

            # Проверяем, съел ли Pac-Man точку
            if (self.x, self.y) in self.game.maze.dots:
                self.game.maze.dots.remove((self.x, self.y))
                self.score += 1
                random.choice(eat_sounds).play()

                # Если все точки съедены, генерируем новый лабиринт
                if not self.game.maze.dots:
                    self.game.maze.generate(self.game)  # Генерируем новый лабиринт без обнуления счёта
                    self.set_position(self.game.pacman.x, self.game.pacman.y)  # Перемещаем Pac-Man'а

    def get_sprite(self):
        """Анимация Pac-Man'а"""
        self.frame = (self.frame + 1) % len(pacman_sprites["right"])
        return pacman_sprites[self.direction][self.frame]

class Maze:
    """Класс для управления лабиринтом"""
    
    def __init__(self, size=N):
        self.size = size
        self.maze = [['#' for _ in range(size)] for _ in range(size)]
        self.dots = set()

    def is_valid_move(self, x, y):
        """Проверяет, можно ли двигаться в данном направлении"""
        return 0 <= x < self.size and 0 <= y < self.size and self.maze[x][y] == '#'

    def generate(self, game, reset_score=False):
        """Генерация нового лабиринта.
        reset_score=True — обнуляет счёт, иначе оставляет его нетронутым.
        """
        if reset_score:
            game.pacman.score = 0  # Обнуляем счёт только при нажатии кнопки GENERATE
        else:
            previous_score = game.pacman.score  # Сохраняем текущий счёт при обычной генерации

        self.maze = [['#' for _ in range(N)] for _ in range(N)]
        start_x, start_y = random.randrange(1, N, 2), random.randrange(1, N, 2)
        game.pacman.set_position(start_x, start_y)
        self.dots.clear()

        stack = [(start_x, start_y)]
        self.maze[start_x][start_y] = ' '

        while stack:
            x, y = stack[-1]
            directions = [(dx, dy) for dx, dy in DIRECTIONS if 0 <= x + dx < N and 0 <= y + dy < N and self.maze[x + dx][y + dy] == '#']

            if directions:
                dx, dy = random.choice(directions)
                self.maze[x + dx // 2][y + dy // 2] = ' '
                self.maze[x + dx][y + dy] = ' '
                stack.append((x + dx, y + dy))
            else:
                stack.pop()

            game.draw_maze()
            pygame.time.delay(20)

        for i in range(N):
            for j in range(N):
                if self.maze[i][j] == ' ' and (i + j) % 2 == 0:
                    self.dots.add((i, j))

        self.dots.discard((start_x, start_y))  # Убираем точку из стартовой позиции Pacman

        if not reset_score:
            game.pacman.score = previous_score  # Восстанавливаем счёт после поедания всех точек

        game.create_ui()  # Обновляем интерфейс после генерации

class Game:
    """Класс для управления игровым процессом"""

    def __init__(self):
        self.maze = Maze(N)
        self.pacman = Pacman(self)
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

        # Отрисовка точек
        for dot in self.maze.dots:
            pygame.draw.circle(screen, YELLOW, (dot[1] * CELL_SIZE + CELL_SIZE // 2, dot[0] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 6)

        # Отрисовка Pac-Man'а
        screen.blit(self.pacman.get_sprite(), (self.pacman.y * CELL_SIZE, self.pacman.x * CELL_SIZE))
        pygame.display.flip()

    def create_ui(self):
        """Создание и обновление UI"""
        pygame.draw.rect(screen, BLACK, (MAZE_WIDTH, 0, UI_WIDTH, HEIGHT))

        # Кнопка "GENERATE"
        self.generate_button = pygame.Rect(MAZE_WIDTH + 30, 50, 145, 40)
        pygame.draw.rect(screen, GREEN, self.generate_button)
        text = font.render("GENERATE", True, WHITE)
        screen.blit(text, (MAZE_WIDTH + 35, 60))

        # Кнопка "Главное меню"
        self.menu_button = pygame.Rect(MAZE_WIDTH + 10, 150, 180, 40)
        pygame.draw.rect(screen, BLUE, self.menu_button)
        menu_text = font.render("Главное меню", True, WHITE)
        screen.blit(menu_text, (MAZE_WIDTH + 15, 160))

        # Обновление счета
        score_text = font.render(f"Score: {self.pacman.score}", True, WHITE)
        screen.blit(score_text, (MAZE_WIDTH + 35, 110))

    def run(self):
        """Запуск игрового цикла"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.generate_button.collidepoint(event.pos):
                        self.maze.generate(self, reset_score=True)
                        self.create_ui()

                    elif self.menu_button.collidepoint(event.pos):
                        pygame.quit()
                        subprocess.run(["python", "main_menu.py"])
                        sys.exit()

                elif event.type == pygame.KEYDOWN:
                    keys = {pygame.K_w: "up", pygame.K_s: "down", pygame.K_a: "left", pygame.K_d: "right"}
                    if event.key in keys:
                        self.pacman.direction = keys[event.key]
                        self.pacman.moving = True

            self.pacman.move()
            self.draw_maze()
            self.create_ui()  # Перерисовываем UI с обновленным счетом
            pygame.display.flip()
            clock.tick(10)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()