#include <iostream>
#include <cstdlib>
#include <ctime>
#include <stack>
#include <vector>
#define n 15
using namespace std;

// Структура для представления координат точки
struct Point {
    int x, y;
};

// Лабиринт
char maze[n][n];

// Инициализация лабиринта (все ячейки заполняются стенами '#')
void initializeMaze() {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            maze[i][j] = '#';
        }
    }
}

// Вывод лабиринта
void printMaze() {
    system("cls"); // Очистка консоли (Windows)
    cout << endl;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            cout << maze[i][j] << " ";
        }
        cout << endl;
    }
}

// Проверка, можно ли двигаться в данном направлении
bool isValidMove(int x, int y) {
    return (x >= 0 && x < n && y >= 0 && y < n && maze[x][y] == '#');
}

// Создание лабиринта с использованием алгоритма Depth-First Search (DFS)
void generateMaze(int startX, int startY) {
    // Смещения для движения: вверх, вниз, влево, вправо
    int dx[] = {-2, 2, 0, 0};
    int dy[] = {0, 0, -2, 2};

    stack<Point> s;
    s.push({startX, startY});
    maze[startX][startY] = ' '; // Начальная точка

    while (!s.empty()) {
        Point current = s.top();
        int x = current.x;
        int y = current.y;

        // Собираем возможные направления движения
        vector<int> directions;
        for (int i = 0; i < 4; i++) {
            int nx = x + dx[i];
            int ny = y + dy[i];
            if (isValidMove(nx, ny)) {
                directions.push_back(i);
            }
        }

        if (!directions.empty()) {
            // Случайный выбор направления
            int randomIndex = rand() % directions.size();
            int dir = directions[randomIndex];

            // Новые координаты
            int nx = x + dx[dir];
            int ny = y + dy[dir];

            // Пробиваем стену между текущей точкой и новой
            maze[x + dx[dir] / 2][y + dy[dir] / 2] = ' ';

            // Обновляем новую точку как часть пути
            maze[nx][ny] = ' ';

            // Добавляем новую точку в стек
            s.push({nx, ny});
        } else {
            // Если нет доступных направлений, возвращаемся назад
            s.pop();
        }
    }
}

int main() {
    srand(time(NULL)); // Инициализация генератора случайных чисел

    initializeMaze(); // Заполнение лабиринта стенами

    // Выбор случайной стартовой точки (нечетные координаты)
    int startX = (rand() % (n / 2)) * 2 + 1;
    int startY = (rand() % (n / 2)) * 2 + 1;

    generateMaze(startX, startY); // Генерация лабиринта

    printMaze(); // Вывод сгенерированного лабиринта

    system("pause");
    return 0;
}
