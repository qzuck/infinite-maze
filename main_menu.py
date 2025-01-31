import pygame
import subprocess
import random
import sys
import os

# Инициализация Pygame
pygame.init()

if not pygame.get_init():
    print("Ошибка: Pygame не была инициализирована!")
    sys.exit()

# Проверяем, существуют ли файлы перед загрузкой
if not os.path.exists("intermission.wav"):
    print("Ошибка: Файл intermission.wav не найден!")
    sys.exit()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Главное меню")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 128, 255)
DARK_BLUE = (0, 102, 204)
GREY = (200, 200, 200)
LIGHT_GREY = (220, 220, 220)

# Список доступных изображений для фона
background_images = [
    "pacman_closed.png", "pacman_half.png", "pacman_open.png",
    "ghost_red_1.png", "ghost_red_2.png",
    "ghost_blue_1.png", "ghost_blue_2.png",
    "ghost_green_1.png", "ghost_green_2.png"
]

for image in background_images:
    if not os.path.exists(image):
        print(f"Ошибка: Файл {image} не найден!")
        sys.exit()

# Выбираем случайный фон
random_background = random.choice(background_images)
background_image = pygame.image.load(random_background)
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))  # Масштабирование под экран

# Проигрывание музыки главного меню
pygame.mixer.music.load("intermission.wav")
pygame.mixer.music.play(-1)  # -1 означает бесконечный цикл

# Шрифты
font = pygame.font.Font(None, 48)
button_font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)

# Доступные версии
versions = ["0.0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7"]

# Класс для кнопки
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.action = action

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
            if mouse_click[0] == 1:
                self.action()
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        
        if not pygame.get_init():
            print("Ошибка: Pygame был завершен перед рендерингом!")
            return

        text_surface = button_font.render(self.text, True, self.text_color)
        screen.blit(text_surface, (self.rect.x + (self.rect.width - text_surface.get_width()) // 2,
                                   self.rect.y + (self.rect.height - text_surface.get_height()) // 2))

# Класс для слайдера (выбор версии)
class VersionSlider:
    def __init__(self, x, y, width):
        self.rect = pygame.Rect(x, y, width, 10)
        self.circle_x = x
        self.circle_y = y + 5
        self.circle_radius = 10
        self.min_index = 0
        self.max_index = len(versions) - 1
        self.value = self.max_index
        self.circle_x = self.rect.x + self.rect.width
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if (self.circle_x - event.pos[0]) ** 2 + (self.circle_y - event.pos[1]) ** 2 <= self.circle_radius ** 2:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.circle_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
                self.value = round((self.circle_x - self.rect.x) / self.rect.width * self.max_index)

    def draw(self, screen):
        pygame.draw.rect(screen, LIGHT_GREY, self.rect)
        pygame.draw.circle(screen, BLUE, (int(self.circle_x), self.circle_y), self.circle_radius)

    def get_version(self):
        return versions[self.value]

# Действие кнопки для запуска выбранной версии
def start_selected_version():
    pygame.mixer.music.stop()  # Останавливаем музыку перед запуском игры
    pygame.quit()
    selected_version = version_slider.get_version()
    filename = f"code0{int(float(selected_version) * 10)}.py"  # Формируем имя файла (например, 0.2 → code02.py)
    subprocess.run(["python", filename])  # Запуск нужного файла

def load_description(version):
    filename = f"code0{int(float(version) * 10)}.txt"  # Преобразуем 0.1 → code01.txt
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return file.read().strip()  # Читаем файл и удаляем лишние пробелы/переносы
    except FileNotFoundError:
        return "Описание этой версии отсутствует."  # Если файла нет, выводим сообщение

def draw_text():
    # === Прямоугольник и текст для заголовка ===
    title_text = font.render("БЕСКОНЕЧНЫЙ ЛАБИРИНТ :)", True, BLACK)

    rect_width, rect_height = title_text.get_width() + 40, title_text.get_height() + 20
    rect_x = (WIDTH - rect_width) // 2
    rect_y = HEIGHT // 2 - 250

    pygame.draw.rect(screen, GREY, (rect_x, rect_y, rect_width, rect_height))  # Серый фон
    pygame.draw.rect(screen, BLACK, (rect_x, rect_y, rect_width, rect_height), 2)  # Чёрная рамка
    screen.blit(title_text, (rect_x + 20, rect_y + 10))  # Текст внутри прямоугольника

    # === Прямоугольник и текст для автора ===
    author_text_1 = small_font.render("Автор:", True, BLACK)
    author_text_2 = small_font.render("Daryn Musabek", True, BLACK)
    author_text_3 = small_font.render("SE-2428", True, BLACK)

    author_rect_width = 250
    author_rect_height = 75
    author_rect_x = (WIDTH - author_rect_width) // 2
    author_rect_y = HEIGHT // 2 - 180

    pygame.draw.rect(screen, GREY, (author_rect_x, author_rect_y, author_rect_width, author_rect_height))
    pygame.draw.rect(screen, BLACK, (author_rect_x, author_rect_y, author_rect_width, author_rect_height), 2)

    screen.blit(author_text_1, (author_rect_x + 20, author_rect_y + 5))
    screen.blit(author_text_2, (author_rect_x + 20, author_rect_y + 30))
    screen.blit(author_text_3, (author_rect_x + 20, author_rect_y + 55))

    # === Прямоугольник и текст для выбора версии ===
    selected_version = version_slider.get_version()
    version_text = small_font.render(f"Выбранная версия: {selected_version}", True, BLACK)

    version_rect_width, version_rect_height = version_text.get_width() + 40, version_text.get_height() + 20
    version_rect_x = (WIDTH - version_rect_width) // 2
    version_rect_y = HEIGHT // 2 - 100

    pygame.draw.rect(screen, GREY, (version_rect_x, version_rect_y, version_rect_width, version_rect_height))
    pygame.draw.rect(screen, BLACK, (version_rect_x, version_rect_y, version_rect_width, version_rect_height), 2)
    screen.blit(version_text, (version_rect_x + 20, version_rect_y + 10))

    # === Прямоугольник для описания версии ===
    description = load_description(selected_version)

    desc_rect_width, desc_rect_height = 800, 160
    desc_rect_x = (WIDTH - desc_rect_width) // 2
    desc_rect_y = HEIGHT // 2 + 120

    pygame.draw.rect(screen, GREY, (desc_rect_x, desc_rect_y, desc_rect_width, desc_rect_height))
    pygame.draw.rect(screen, BLACK, (desc_rect_x, desc_rect_y, desc_rect_width, desc_rect_height), 2)

    # Отображаем описание внутри серого прямоугольника
    lines = description.split("\n")
    y_offset = desc_rect_y + 10
    for line in lines:
        line_surface = small_font.render(line, True, BLACK)
        screen.blit(line_surface, (desc_rect_x + 10, y_offset))
        y_offset += 25

# Основная функция для главного меню
def main_menu():
    global version_slider
    button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50, "Запустить игру", BLUE, DARK_BLUE, WHITE, start_selected_version)
    version_slider = VersionSlider(WIDTH // 2 - 150, HEIGHT // 2 - 50, 300)
    version_slider.value = version_slider.max_index  # Устанавливаем начальную версию на 0.7
    version_slider.circle_x = version_slider.rect.x + version_slider.rect.width  # Сдвигаем круг вправо


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()

            version_slider.handle_event(event)
            pygame.display.flip()  # Перерисовываем экран, чтобы обновить описание версии


        # Отрисовка заднего фона
        screen.blit(background_image, (0, 0))

        # Отрисовка текста
        draw_text()

        # Отрисовка ползунка и кнопки
        version_slider.draw(screen)
        button.draw(screen)

        # Отображение текущей выбранной версии
        version_text = small_font.render(f"Выбранная версия: {version_slider.get_version()}", True, WHITE)
        screen.blit(version_text, (WIDTH // 2 - version_text.get_width() // 2, HEIGHT // 2 - 90))

        pygame.display.flip()

if __name__ == "__main__":
    main_menu()
