import pygame
import sys
from data import create_empty_grid, random_grid, load_grid_from_file
from rules import next_generation
import game


def handle_keyboard_input(event, state):
    """
    Обрабатывает события клавиш.
    Передает состояние через словарь 'state', который содержит:
    - 'grid'
    - 'running'
    - 'speed'
    - 'generation'
    """
    grid = state['grid']
    running = state['running']
    speed = state['speed']
    generation = state['generation']

    if event.key == pygame.K_SPACE:
        # Запуск/пауза симуляции
        state['running'] = not running
    elif event.key == pygame.K_s or event.key == pygame.K_RIGHT:
        # Шаг вручную
        grid = next_generation(grid, wrap_edges=True)
        state['generation'] = generation + 1
    elif event.key == pygame.K_r:
        # Ресет (случайное заполнение)
        grid = random_grid(len(grid), len(grid[0]), prob=0.5)
        state['generation'] = 0
    elif event.key == pygame.K_c:
        # Очистка сетки
        grid = create_empty_grid(len(grid), len(grid[0]))
        state['generation'] = 0
    elif event.key == pygame.K_l:
        # Загрузить конфигурацию из файла
        filename = 'config.txt'  # Можно изменить или получить из диалога
        grid = load_grid_from_file(filename)
        state['generation'] = 0
    elif event.key == pygame.K_f:
        # Сохранить текущую конфигурацию
        filename = 'save.txt'
        save_grid_to_file(grid, filename)
    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
        # Увеличить скорость
        state['speed'] = min(state['speed'] + 1, 60)
    elif event.key == pygame.K_MINUS:
        # Уменьшить скорость
        state['speed'] = max(state['speed'] - 1, 1)
    elif event.key == pygame.K_q:
        # Выход
        pygame.quit()
        sys.exit()

    return grid, state


def handle_mouse_click(event, grid, rows, cols):
    """
    Обработка клика мышкой по сетке для переключения клетки.
    """
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = pygame.mouse.get_pos()
        rows, cols = 30, 40
        cell_size = 20
        screen, cell_size, rows, cols = game.init_display(rows, cols, cell_size)
        row, col = game.get_cell_from_mouse(mouse_pos, cell_size, rows, cols)
        if row is not None and col is not None:
            grid[row][col] = 1 - grid[row][col]
    return grid


def save_grid_to_file(grid, filename):
    # Реализуйте функцию сохранения в файл
    try:
        with open(filename, 'w') as f:
            for row in grid:
                line = ''.join(str(cell) for cell in row)
                f.write(line + '\n')
        print(f"Конфигурация сохранена в {filename}")
    except Exception:
        print(f"Ошибка записи файла {filename}")


def main():
    # Инициализация
    rows, cols = 30, 40  # например
    cell_size = 20
    screen, cell_size, rows, cols = game.init_display(rows, cols, cell_size)

    # Задача: можно задать начальную конфигурацию
    grid = random_grid(rows, cols, prob=0.5)  # или create_empty_grid, или загрузить
    state = {
        'grid': grid,
        'running': False,
        'speed': 10,
        'generation': 0
    }

    clock = pygame.time.Clock()

    while True:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                state['grid'], state = handle_keyboard_input(event, state)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                state['grid'] = handle_mouse_click(event, state['grid'], rows, cols)

        # Автоматическое обновление
        if state['running']:
            state['grid'] = next_generation(state['grid'], wrap_edges=True)
            state['generation'] += 1

        # Отрисовка
        screen.fill(game.DEAD_COLOR)
        mouse_pos = pygame.mouse.get_pos()
        hover_cell = game.get_cell_from_mouse(mouse_pos, cell_size, rows, cols)
        game.draw_grid(screen, state['grid'], cell_size, hover_cell)
        game.draw_ui(screen, state['generation'], state['speed'], state['running'], rows, cols)
        pygame.display.flip()
        clock.tick(state['speed'])


if __name__ == "__main__":
    main()
