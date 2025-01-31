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
pygame.display.set_caption("Infinite Maze ver 0.7")
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

# Загрузка спрайтов призраков
ghost_sprites = {
    "red": [pygame.image.load("ghost_red_1.png"), pygame.image.load("ghost_red_2.png")],
    "green": [pygame.image.load("ghost_green_1.png"), pygame.image.load("ghost_green_2.png")],
    "blue": [pygame.image.load("ghost_blue_1.png"), pygame.image.load("ghost_blue_2.png")]
}

# Масштабирование
for color in ghost_sprites:
    ghost_sprites[color] = [pygame.transform.scale(sprite, (CELL_SIZE, CELL_SIZE)) for sprite in ghost_sprites[color]]

# Создание зеркальных спрайтов для направления
pacman_sprites["left"] = [pygame.transform.flip(sprite, True, False) for sprite in pacman_sprites["right"]]
pacman_sprites["up"] = [pygame.transform.rotate(sprite, 90) for sprite in pacman_sprites["right"]]
pacman_sprites["down"] = [pygame.transform.rotate(sprite, -90) for sprite in pacman_sprites["right"]]

# Масштабирование
for direction in pacman_sprites:
    pacman_sprites[direction] = [pygame.transform.scale(sprite, (CELL_SIZE, CELL_SIZE)) for sprite in pacman_sprites[direction]]

# Загрузка музыки
pygame.mixer.music.load("start.wav")  # Музыка для генерации лабиринта
collision_sound = pygame.mixer.Sound("death.wav")  # Музыка для столкновения

class Pacman:
    """Класс для управления Pac-Man'ом"""
    def __init__(self, game):
        self.game = game
        self.x, self.y = 1, 1
        self.frame = 0
        self.direction = "right"
        self.moving = False
        self.score = 0

    def set_position(self, x, y):
        """Устанавливает позицию Pac-Man'а"""
        self.x, self.y = x, y

    def move(self):
        """Pac-Man движется по одной клетке за тик, пока не упрется в стену."""
        if self.game.check_collision():
            return  # Если столкнулся с призраком, не двигаемся

        dx, dy = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}[self.direction]

        # Проверяем следующую клетку, если это не стена — двигаемся
        new_x, new_y = self.x + dx, self.y + dy
        if 0 <= new_x < N and 0 <= new_y < N and self.game.maze.maze[new_x][new_y] == ' ':
            self.x, self.y = new_x, new_y

            # Если есть точка — съедаем ее
            if (self.x, self.y) in self.game.maze.dots:
                self.game.maze.dots.remove((self.x, self.y))
                self.score += 1
                random.choice(eat_sounds).play()

                # Если все точки съедены — победа
                if not self.game.maze.dots:
                    self.game.win()
        else:
            # Если впереди стена — Pac-Man останавливается
            self.moving = False
    
    def stop(self):
        """Pac-Man останавливается (неуязвим)"""
        self.moving = False

    def get_sprite(self):
        """Возвращает текущий спрайт Pac-Man'а"""
        self.frame = (self.frame + 1) % len(pacman_sprites["right"])
        return pacman_sprites[self.direction][self.frame]

ghost_count = 1  # Количество призраков из скроллбара

game_message = ""  # Сообщение о победе или поражении
message_timer = 0  # Таймер для скрытия сообщения

class Ghost:
    """Класс для управления призраками"""
    def __init__(self, game, color):
        self.game = game
        self.color = color
        self.frame = 0
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])

        # Генерация случайного места появления
        while True:
            self.x, self.y = random.randint(1, N-2), random.randint(1, N-2)
            if self.game.maze.maze[self.x][self.y] == ' ' and (self.x, self.y) != (self.game.pacman.x, self.game.pacman.y):
                break

    def move(self):
        """Перемещение призрака"""
        dx, dy = self.direction
        new_x, new_y = self.x + dx, self.y + dy

        if 0 <= new_x < N and 0 <= new_y < N and self.game.maze.maze[new_x][new_y] == ' ':
            self.x, self.y = new_x, new_y
        else:
            self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])

        self.frame = (self.frame + 1) % 2  # Меняем анимацию

    def get_sprite(self):
        """Возвращает текущий спрайт призрака"""
        return ghost_sprites[self.color][self.frame]

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
        """Генерация нового лабиринта"""
        
        # 🔊 Воспроизводим музыку генерации лабиринта
        pygame.mixer.music.stop()  # Останавливаем текущую музыку
        pygame.mixer.music.load("start.wav")  # Загружаем музыку
        pygame.mixer.music.play()  # Запускаем проигрывание

        if reset_score:
            game.pacman.score = 0  
        else:
            previous_score = game.pacman.score  

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
            pygame.time.delay(20)  # Задержка для эффекта анимации

        for i in range(N):
            for j in range(N):
                if self.maze[i][j] == ' ' and (i + j) % 2 == 0:
                    self.dots.add((i, j))

        self.dots.discard((start_x, start_y))

        if not reset_score:
            game.pacman.score = previous_score  

        game.create_ui()
        game.spawn_ghosts()

class Game:
    """Класс для управления игровым процессом"""

    def __init__(self):
        self.maze = Maze(N)
        self.pacman = Pacman(self)
        self.ghosts = []
        self.ghost_count = 1
        self.high_score = 0
        self.message = ""
        self.message_timer = 0
        self.generate_button = None
        self.menu_button = None
        self.create_ui()
        self.maze.generate(self)
        self.spawn_ghosts()
    
    def check_collision(self):
        """Проверка столкновения Pac-Man'а с призраком"""

        for ghost in self.ghosts:
            if (self.pacman.x, self.pacman.y) == (ghost.x, ghost.y):
                if self.pacman.score > self.high_score:
                    self.high_score = self.pacman.score
                self.pacman.score = 0
                pygame.mixer.music.stop()
                collision_sound.play()
                self.message = "Вас поймали!"
                self.message_timer = pygame.time.get_ticks() + 2000  

                self.draw_maze()
                pygame.display.flip()
                pygame.time.delay(2000)  

                self.message = ""
                self.maze.generate(self, reset_score=True)
                self.spawn_ghosts()
                return True
        return False
    
    def spawn_ghosts(self):
        """Создание призраков на основе выбранного количества"""
        self.ghosts = []
        colors = ["red", "green", "blue"]
        
        for i in range(self.ghost_count):  # Используем выбранное значение
            color = colors[i % len(colors)]  # Чередуем цвета
            self.ghosts.append(Ghost(self, color))
    
    def draw_message(self):
        """Отображение сообщения о победе или проигрыше"""
        if not self.message:
            return  # Если нет сообщения, просто выходим

        rect_width, rect_height = 300, 100
        rect_x = (MAZE_WIDTH - rect_width) // 2
        rect_y = (MAZE_HEIGHT - rect_height) // 2

        pygame.draw.rect(screen, WHITE, (rect_x, rect_y, rect_width, rect_height))
        pygame.draw.rect(screen, BLACK, (rect_x, rect_y, rect_width, rect_height), 3)

        text = font.render(self.message, True, BLACK)
        text_rect = text.get_rect(center=(MAZE_WIDTH // 2, MAZE_HEIGHT // 2))
        screen.blit(text, text_rect)

        if pygame.time.get_ticks() > self.message_timer:
            self.message = ""

    def draw_maze(self):
        """Отрисовка лабиринта"""
        screen.fill(BLACK, (0, 0, MAZE_WIDTH, MAZE_HEIGHT))
        
        # Отрисовка лабиринта
        for i in range(N):
            for j in range(N):
                if self.maze.maze[i][j] == ' ':
                    pygame.draw.rect(screen, GRAY, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                else:
                    screen.blit(brick_texture, (j * CELL_SIZE, i * CELL_SIZE))
        
        # Отрисовка точек
        for dot in self.maze.dots:
            pygame.draw.circle(screen, YELLOW, (dot[1] * CELL_SIZE + CELL_SIZE // 2, dot[0] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 6)
        
        # Отрисовка персонажей
        screen.blit(self.pacman.get_sprite(), (self.pacman.y * CELL_SIZE, self.pacman.x * CELL_SIZE))
        for ghost in self.ghosts:
            screen.blit(ghost.get_sprite(), (ghost.y * CELL_SIZE, ghost.x * CELL_SIZE))
        
        self.draw_message()  # Показываем сообщение, если оно есть
        pygame.display.flip()

    def create_ui(self):
        """Создание и обновление UI"""
        pygame.draw.rect(screen, BLACK, (MAZE_WIDTH, 0, UI_WIDTH, HEIGHT))

        self.generate_button = pygame.Rect(MAZE_WIDTH + 30, 50, 145, 40)
        pygame.draw.rect(screen, GREEN, self.generate_button)
        text = font.render("GENERATE", True, WHITE)
        screen.blit(text, (MAZE_WIDTH + 35, 60))

        self.menu_button = pygame.Rect(MAZE_WIDTH + 10, 150, 180, 40)
        pygame.draw.rect(screen, BLUE, self.menu_button)
        menu_text = font.render("Главное меню", True, WHITE)
        screen.blit(menu_text, (MAZE_WIDTH + 15, 160))

        score_text = font.render(f"Score: {self.pacman.score}", True, WHITE)
        screen.blit(score_text, (MAZE_WIDTH + 35, 110))

        high_score_text = font.render(f"High Score: {self.high_score}", True, WHITE)
        screen.blit(high_score_text, (MAZE_WIDTH + 15, 220))

        ghost_text = font.render(f"Ghosts: {self.ghost_count}", True, WHITE)
        screen.blit(ghost_text, (MAZE_WIDTH + 35, 260))

        # Ползунок выбора количества призраков
        pygame.draw.rect(screen, WHITE, (MAZE_WIDTH + 30, 300, 140, 5))
        slider_x = MAZE_WIDTH + 30 + (self.ghost_count / 3) * 140
        pygame.draw.circle(screen, YELLOW, (int(slider_x), 302), 8)

    def win(self):
        """Pac-Man съел все точки"""
        self.message = "Вы победили!"
        self.message_timer = pygame.time.get_ticks() + 2000  # Показываем 2 секунды

        # Перерисовываем экран с сообщением и ждем 2 секунды
        self.draw_maze()
        pygame.display.flip()
        pygame.time.delay(2000)  # Ждем перед перезапуском

        # Очищаем сообщение и перезапускаем игру
        self.message = ""
        self.maze.generate(self)
        self.spawn_ghosts()

game = Game()
running = True
dragging_slider = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game.generate_button.collidepoint(event.pos):
                game.maze.generate(game, reset_score=True)
                game.create_ui()
            elif game.menu_button.collidepoint(event.pos):
                pygame.quit()
                subprocess.run(["python", "main_menu.py"])
                sys.exit()
            elif MAZE_WIDTH + 30 <= event.pos[0] <= MAZE_WIDTH + 170 and 290 <= event.pos[1] <= 310:
                dragging_slider = True  # Начало перетаскивания
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_slider = False  # Завершение перетаскивания
        elif event.type == pygame.MOUSEMOTION:
            if dragging_slider:  # Если двигаем ползунок
                game.ghost_count = max(0, min(3, round((event.pos[0] - (MAZE_WIDTH + 30)) / 140 * 3)))
                game.create_ui()
        elif event.type == pygame.KEYDOWN:
            keys = {pygame.K_w: "up", pygame.K_s: "down", pygame.K_a: "left", pygame.K_d: "right"}
            if event.key in keys:
                game.pacman.direction = keys[event.key]
                game.pacman.moving = True  # Начинаем движение

    if game.pacman.moving:
        game.pacman.move()

    for ghost in game.ghosts:
        ghost.move()

    game.draw_maze()
    game.create_ui()
    pygame.display.flip()
    clock.tick(10)

pygame.quit()
