from random import randint
from typing import Tuple, List, Optional

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета:
BOARD_BACKGROUND_COLOR = (0, 0, 0)          # Черный
BORDER_COLOR = (93, 216, 228)              # Голубой
APPLE_COLOR = (255, 0, 0)                  # Красный
SNAKE_COLOR = (0, 255, 0)                  # Зеленый
INCORRECT_FOOD_COLOR = (255, 165, 0)       # Оранжевый
OBSTACLE_COLOR = (128, 128, 128)           # Серый

# Скорость движения змейки:
DEFAULT_SPEED = 10

# Настройка игрового окна:
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position: Tuple[int, int] = (0, 0),
                 body_color: Tuple[int, int, int] = (255, 255, 255)) -> None:
        """
        Инициализирует базовые атрибуты игрового объекта.

        :param position: Кортеж с координатами (x, y).
        :param body_color: Цвет объекта в формате RGB.
        """
        self.position = position
        self.body_color = body_color

    def draw(self) -> None:
        """Отрисовывает объект на игровом поле."""
        raise NotImplementedError(
            "Метод draw должен быть реализован в подклассе."
        )


class Apple(GameObject):
    """Класс, описывающий яблоко."""

    def __init__(self, obstacles: Optional[List['Obstacle']] = None) -> None:
        """
        Инициализирует яблоко с случайной позицией.

        :param obstacles: Список препятствий, чтобы яблоко не появилось на них.
        """
        super().__init__(position=(0, 0), body_color=APPLE_COLOR)
        self.randomize_position(obstacles)

    def randomize_position(
        self,
        obstacles: Optional[List['Obstacle']] = None
    ) -> None:
        """
        Устанавливает случайную позицию яблока на игровом поле.

        :param obstacles: Список препятствий, чтобы яблоко не появилось на них.
        """
        while True:
            x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            self.position = (x, y)
            if obstacles:
                if any(obstacle.position == self.position
                       for obstacle in obstacles):
                    continue
            break

    def draw(self) -> None:
        """Отрисовывает яблоко на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class IncorrectFood(GameObject):
    """Класс, описывающий "неправильную" еду."""

    def __init__(self, obstacles: Optional[List['Obstacle']] = None) -> None:
        """
        Инициализирует неправильную еду с случайной позицией.

        :param obstacles: Список препятствий, чтобы еда не появилась на них.
        """
        super().__init__(position=(0, 0), body_color=INCORRECT_FOOD_COLOR)
        self.randomize_position(obstacles)

    def randomize_position(
        self,
        obstacles: Optional[List['Obstacle']] = None
    ) -> None:
        """
        Устанавливает случайную позицию неправильной еды на игровом поле.

        :param obstacles: Список препятствий, чтобы еда не появилась на них.
        """
        while True:
            x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            self.position = (x, y)
            if obstacles:
                if any(obstacle.position == self.position
                       for obstacle in obstacles):
                    continue
            break

    def draw(self) -> None:
        """Отрисовывает неправильную еду на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Obstacle(GameObject):
    """Класс, описывающий препятствие."""

    def __init__(self, position: Tuple[int, int]) -> None:
        """
        Инициализирует препятствие с заданной позицией.

        :param position: Кортеж с координатами (x, y).
        """
        super().__init__(position=position, body_color=OBSTACLE_COLOR)

    def draw(self) -> None:
        """Отрисовывает препятствие на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс, описывающий змейку."""

    def __init__(self) -> None:
        """Инициализирует змейку в начальной позиции."""
        initial_position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        super().__init__(position=initial_position, body_color=SNAKE_COLOR)
        self.positions: List[Tuple[int, int]] = [initial_position]
        self.direction: Tuple[int, int] = RIGHT
        self.next_direction: Optional[Tuple[int, int]] = None
        self.length: int = 1

    def update_direction(self) -> None:
        """Обновляет текущее направление движения змейки."""
        if self.next_direction:
            opposite_direction = (-self.next_direction[0],
                                  -self.next_direction[1])
            if opposite_direction != self.direction:
                self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """
        Двигает змейку в текущем направлении.
        Добавляет новую голову и удаляет хвост, если длина не увеличилась.
        """
        current_head = self.positions[0]
        new_head = (
            (current_head[0] + self.direction[0] * GRID_SIZE) %
            SCREEN_WIDTH,
            (current_head[1] + self.direction[1] * GRID_SIZE) %
            SCREEN_HEIGHT
        )
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()

    def grow(self) -> None:
        """Увеличивает длину змейки на один сегмент."""
        self.length += 1

    def shrink(self) -> None:
        """Уменьшает длину змейки на один сегмент, если это возможно."""
        if self.length > 1:
            self.length -= 1
            self.positions.pop()

    def draw(self) -> None:
        """Отрисовывает змейку на игровом поле."""
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def get_head_position(self) -> Tuple[int, int]:
        """
        Возвращает позицию головы змейки.

        :return: Кортеж с координатами головы (x, y).
        """
        return self.positions[0]

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        initial_position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [initial_position]
        self.direction = RIGHT
        self.next_direction = None
        self.length = 1


def handle_keys(snake: Snake) -> None:
    """
    Обрабатывает нажатия клавиш для изменения направления движения змейки.

    :param snake: Объект змейки.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT:
                snake.next_direction = RIGHT


def main() -> None:
    """Основная функция игры. Запускает игровой цикл."""
    # Создание объектов
    snake = Snake()
    obstacles = [
        Obstacle(position=(100, 100)),
        Obstacle(position=(200, 200)),
        Obstacle(position=(300, 300)),
        Obstacle(position=(400, 100)),
        Obstacle(position=(500, 200))
    ]
    apple = Apple(obstacles=obstacles)
    incorrect_food = IncorrectFood(obstacles=obstacles)

    running = True
    while running:
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Проверка столкновений с препятствиями
        if any(
            snake.get_head_position() == obstacle.position
            for obstacle in obstacles
        ):
            snake.reset()
            apple.randomize_position(obstacles)
            incorrect_food.randomize_position(obstacles)

        # Проверка столкновений с собой
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(obstacles)
            incorrect_food.randomize_position(obstacles)

        # Проверка съедения яблока
        if snake.get_head_position() == apple.position:
            snake.grow()
            apple.randomize_position(obstacles)
            incorrect_food.randomize_position(obstacles)

        # Проверка съедения неправильной еды
        if snake.get_head_position() == incorrect_food.position:
            snake.shrink()
            incorrect_food.randomize_position(obstacles)

        # Отрисовка
        screen.fill(BOARD_BACKGROUND_COLOR)
        for obstacle in obstacles:
            obstacle.draw()
        apple.draw()
        incorrect_food.draw()
        snake.draw()
        pygame.display.update()

        clock.tick(DEFAULT_SPEED)


if __name__ == '__main__':
    main()
