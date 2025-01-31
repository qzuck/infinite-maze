import random
import os

class Maze:
    def __init__(self, size=15):
        """Инициализация лабиринта"""
        self.size = size
        self.maze = [['#' for _ in range(size)] for _ in range(size)]

    def initialize_maze(self):
        """Заполняет лабиринт стенами '#'"""
        for i in range(self.size):
            for j in range(self.size):
                self.maze[i][j] = '#'

    def print_maze(self):
        """Вывод лабиринта в консоль"""
        os.system("cls" if os.name == "nt" else "clear")  # Очистка консоли
        for row in self.maze:
            print(" ".join(row))

    def is_valid_move(self, x, y):
        """Проверяет, можно ли двигаться в данном направлении"""
        return 0 <= x < self.size and 0 <= y < self.size and self.maze[x][y] == '#'

    def generate_maze(self, start_x, start_y):
        """Создаёт лабиринт с помощью алгоритма DFS"""
        dx = [-2, 2, 0, 0]
        dy = [0, 0, -2, 2]

        stack = [(start_x, start_y)]
        self.maze[start_x][start_y] = ' '  # Начальная точка

        while stack:
            x, y = stack[-1]

            # Собираем возможные направления движения
            directions = []
            for i in range(4):
                nx, ny = x + dx[i], y + dy[i]
                if self.is_valid_move(nx, ny):
                    directions.append((nx, ny, dx[i] // 2, dy[i] // 2))

            if directions:
                # Случайный выбор направления
                nx, ny, mx, my = random.choice(directions)

                # Пробиваем стену между текущей точкой и новой
                self.maze[x + mx][y + my] = ' '

                # Обновляем новую точку как часть пути
                self.maze[nx][ny] = ' '

                # Добавляем новую точку в стек
                stack.append((nx, ny))
            else:
                # Если нет доступных направлений, возвращаемся назад
                stack.pop()

if __name__ == "__main__":
    random.seed()  # Инициализация генератора случайных чисел

    maze = Maze(size=15)  # Создаём объект лабиринта
    maze.initialize_maze()  # Заполняем его стенами

    # Выбор случайной стартовой точки (нечетные координаты)
    start_x = random.randrange(1, maze.size, 2)
    start_y = random.randrange(1, maze.size, 2)

    maze.generate_maze(start_x, start_y)  # Генерируем лабиринт
    maze.print_maze()
    os.system("pause")
