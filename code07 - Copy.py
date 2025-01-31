import pygame
import random
import subprocess

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

# Переменные игры
maze = []
dots = set()
pacman_x, pacman_y = 1, 1
pacman_frame = 0
pacman_direction = "right"
pacman_moving = False
score = 0
high_score = 0

# Призраки
dragging_slider = False
ghosts = []
ghost_count = 1  # Количество призраков из скроллбара
ghost_directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Возможные направления движения

game_message = ""  # Сообщение о победе или поражении
message_timer = 0  # Таймер для скрытия сообщения

def move_pacman():
    global pacman_x, pacman_y, pacman_moving, score, dots, game_message, message_timer
    
    if check_collision():  # Проверяем столкновение перед движением
        return
    
    dx, dy = 0, 0
    if pacman_direction == "up": dx, dy = -1, 0
    elif pacman_direction == "down": dx, dy = 1, 0
    elif pacman_direction == "left": dx, dy = 0, -1
    elif pacman_direction == "right": dx, dy = 0, 1
    
    new_x, new_y = pacman_x + dx, pacman_y + dy
    if 0 <= new_x < N and 0 <= new_y < N and maze[new_x][new_y] == ' ':
        pacman_x, pacman_y = new_x, new_y
        if (pacman_x, pacman_y) in dots:
            dots.remove((pacman_x, pacman_y))
            score += 1
            random.choice(eat_sounds).play()
            if not dots:
                game_message = "Вы победили!"
                message_timer = pygame.time.get_ticks() + 2000  # Показывать 2 секунды
                generate_maze()
    else:
        pacman_moving = False

    if check_collision():  # Проверяем снова после движения
        return
    
def move_ghosts():
    global ghosts
    for ghost in ghosts:
        dx, dy = ghost["direction"]
        new_x, new_y = ghost["x"] + dx, ghost["y"] + dy
        
        if 0 <= new_x < N and 0 <= new_y < N and maze[new_x][new_y] == ' ':
            ghost["x"], ghost["y"] = new_x, new_y
        else:
            # Меняем направление, если призрак столкнулся со стеной
            ghost["direction"] = random.choice(ghost_directions)
        
        ghost["frame"] = (ghost["frame"] + 1) % 2  # Меняем анимацию

def is_valid_move(x, y):
    return 0 <= x < N and 0 <= y < N and maze[x][y] == '#'

def spawn_ghosts():
    global ghosts
    ghosts = []
    ghost_colors = ["red", "green", "blue"]
    
    if ghost_count == 0:
        return  # Не создаем призраков, если их 0
    
    for i in range(ghost_count):
        while True:
            x, y = random.randint(1, N-2), random.randint(1, N-2)
            if maze[x][y] == ' ' and (x, y) != (pacman_x, pacman_y):
                ghosts.append({"x": x, "y": y, "color": ghost_colors[i], "frame": 0, "direction": random.choice(ghost_directions)})
                break

def check_collision():
    global pacman_x, pacman_y, score, high_score, game_message, message_timer
    for ghost in ghosts:
        if (pacman_x, pacman_y) == (ghost["x"], ghost["y"]):
            if score > high_score:  # Сохранение рекорда
                high_score = score
            score = 0  # Обнуляем очки при столкновении
            
            pygame.mixer.music.stop()  # Останавливаем фоновую музыку
            collision_sound.play()  # Проигрываем звук столкновения
            
            game_message = "Вас поймали!"
            message_timer = pygame.time.get_ticks() + 2000  # Показывать 2 секунды
            
            pygame.time.delay(2000)  # Ждем 2 секунды перед сбросом
            
            generate_maze()  # Генерируем новый лабиринт
            spawn_ghosts()
            
            return True
    return False

def draw_maze():
    screen.fill(BLACK, (0, 0, MAZE_WIDTH, MAZE_HEIGHT))
    for i in range(N):
        for j in range(N):
            if maze[i][j] == ' ':
                pygame.draw.rect(screen, GRAY, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            else:
                screen.blit(brick_texture, (j * CELL_SIZE, i * CELL_SIZE))
    
    for dot in dots:
        pygame.draw.circle(screen, YELLOW, (dot[1] * CELL_SIZE + CELL_SIZE // 2, dot[0] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 6)
    
    screen.blit(pacman_sprites[pacman_direction][pacman_frame], (pacman_y * CELL_SIZE, pacman_x * CELL_SIZE))
    
    for ghost in ghosts:
        screen.blit(ghost_sprites[ghost["color"]][ghost["frame"]], (ghost["y"] * CELL_SIZE, ghost["x"] * CELL_SIZE))

    draw_message()
    pygame.display.flip()


def generate_maze():
    global maze, pacman_x, pacman_y, pacman_moving, pacman_direction, dots, score
    
    pygame.mixer.music.stop()  # Останавливаем возможную текущую музыку
    pygame.mixer.music.play()  # Запускаем музыку зацикленно
    
    maze = [['#' for _ in range(N)] for _ in range(N)]
    start_x, start_y = random.randrange(1, N, 2), random.randrange(1, N, 2)
    pacman_x, pacman_y = start_x, start_y
    pacman_moving = False
    pacman_direction = "right"
    dots.clear()
    
    stack = [(start_x, start_y)]
    maze[start_x][start_y] = ' '
    
    while stack:
        x, y = stack[-1]
        directions = [(dx, dy) for dx, dy in DIRECTIONS if is_valid_move(x + dx, y + dy)]
        
        if directions:
            dx, dy = random.choice(directions)
            maze[x + dx // 2][y + dy // 2] = ' '
            maze[x + dx][y + dy] = ' '
            stack.append((x + dx, y + dy))
        else:
            stack.pop()
        
        draw_maze()
        pygame.time.delay(20)
    
    for i in range(N):
        for j in range(N):
            if maze[i][j] == ' ' and (i + j) % 2 == 0:
                dots.add((i, j))
    
    dots.remove((start_x, start_y))

    draw_maze()
    spawn_ghosts()

def draw_message():
    if game_message:
        # Размеры прямоугольника
        rect_width, rect_height = 300, 100
        rect_x = (MAZE_WIDTH - rect_width) // 2  # Центр лабиринта по X
        rect_y = (MAZE_HEIGHT - rect_height) // 2  # Центр лабиринта по Y
        
        # Рисуем белый прямоугольник в центре лабиринта
        pygame.draw.rect(screen, WHITE, (rect_x, rect_y, rect_width, rect_height))
        pygame.draw.rect(screen, BLACK, (rect_x, rect_y, rect_width, rect_height), 3)  # Чёрная рамка
        
        # Отображаем текст внутри прямоугольника
        text = font.render(game_message, True, BLACK)
        text_rect = text.get_rect(center=(MAZE_WIDTH // 2, MAZE_HEIGHT // 2))  # Центр лабиринта
        screen.blit(text, text_rect)

def draw_ui():
    pygame.draw.rect(screen, BLACK, (MAZE_WIDTH, 0, UI_WIDTH, HEIGHT))
    
    # Кнопка "GENERATE"
    generate_button = pygame.Rect(MAZE_WIDTH + 30, 50, 145, 40)
    pygame.draw.rect(screen, GREEN, generate_button)
    text = font.render("GENERATE", True, WHITE)
    screen.blit(text, (MAZE_WIDTH + 35, 60))

    # Кнопка "Главное меню"
    menu_button = pygame.Rect(MAZE_WIDTH + 10, 150, 180, 40)
    pygame.draw.rect(screen, BLUE, menu_button)  # Синяя кнопка
    menu_text = font.render("Главное меню", True, WHITE)
    screen.blit(menu_text, (MAZE_WIDTH + 15, 160))

    # Отображение счёта
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (MAZE_WIDTH + 35, 110))

    # Отображение рекорда
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    screen.blit(high_score_text, (MAZE_WIDTH + 15, 220))

    # Текст количества призраков
    ghost_text = font.render(f"Ghosts: {ghost_count}", True, WHITE)
    screen.blit(ghost_text, (MAZE_WIDTH + 35, 260))

    # Ползунок
    pygame.draw.rect(screen, WHITE, (MAZE_WIDTH + 30, 300, 140, 5))
    slider_x = MAZE_WIDTH + 30 + (ghost_count / 3) * 140
    pygame.draw.circle(screen, YELLOW, (int(slider_x), 302), 8)

    return generate_button, menu_button  # Возвращаем обе кнопки

generate_button, menu_button = draw_ui()
generate_maze()
draw_maze()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if generate_button.collidepoint(event.pos):
                generate_maze()
                draw_ui()
            elif menu_button.collidepoint(event.pos):  # Проверяем клик по кнопке меню
                pygame.quit()  # Закрываем игру
                subprocess.run(["python", "main_menu.py"])  # Запускаем главное меню
                exit()  # Выход из текущего скрипта
            elif MAZE_WIDTH + 30 <= event.pos[0] <= MAZE_WIDTH + 170 and 290 <= event.pos[1] <= 310:
                dragging_slider = True  # Начинаем перетаскивание
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_slider = False  # Завершаем перетаскивание
        elif event.type == pygame.MOUSEMOTION:
            if dragging_slider:  # Если двигаем ползунок
                ghost_count = max(0, min(3, round((event.pos[0] - (MAZE_WIDTH + 30)) / 140 * 3)))
                draw_ui()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                pacman_direction = "up"
                pacman_moving = True
            elif event.key == pygame.K_s:
                pacman_direction = "down"
                pacman_moving = True
            elif event.key == pygame.K_a:
                pacman_direction = "left"
                pacman_moving = True
            elif event.key == pygame.K_d:
                pacman_direction = "right"
                pacman_moving = True

    
    if pacman_moving:
        move_pacman()
    
    move_ghosts()

    pacman_frame = (pacman_frame + 1) % len(pacman_sprites["right"])
    
    if game_message and pygame.time.get_ticks() > message_timer:
        game_message = ""
    
    draw_maze()
    draw_ui()
    pygame.display.flip()
    clock.tick(10)

pygame.quit()
