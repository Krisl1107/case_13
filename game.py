import pygame
import logging
from typing import Optional, Tuple, List

# Настройка логирования
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# ========== КОНСТАНТЫ ==========
# Цвета (RGB)
ALIVE_COLOR = (50, 205, 50)
DEAD_COLOR = (30, 30, 30)
GRID_COLOR = (60, 60, 60)
UI_TEXT_COLOR = (255, 255, 255)
HOVER_COLOR = (100, 100, 100)

# Настройки UI
UI_HEIGHT = 100
UI_PADDING = 10
CONTROLS_HEIGHT = 40

# Кэширование шрифтов
_font_cache = {}
_font_small_cache = {}


def _get_font(size: int = 24):
    """Кэшированное получение шрифта."""
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font(None, size)
    return _font_cache[size]


def _get_font_small(size: int = 18):
    """Кэшированное получение маленького шрифта."""
    if size not in _font_small_cache:
        _font_small_cache[size] = pygame.font.Font(None, size)
    return _font_small_cache[size]


# ========== ИНИЦИАЛИЗАЦИЯ ==========
def init_display(rows: int, cols: int, cell_size: int = 20) -> Tuple[pygame.Surface, int, int, int]:
    """
    Инициализирует окно Pygame.

    Returns:
        tuple: (screen, cell_size, rows, cols)
    """
    try:
        pygame.init()

        width = cols * cell_size
        height = rows * cell_size + UI_HEIGHT

        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Conway's Game of Life")

        # Удалите следующую строку, она некорректна
        # pygame.display.set_alpha(None)

        return screen, cell_size, rows, cols

    except pygame.error as e:
        logger.error(f"Failed to initialize display: {e}")
        raise


# ========== ОПТИМИЗИРОВАННАЯ ОТРИСОВКА СЕТКИ ==========
def draw_grid(screen: pygame.Surface, grid: List[List[int]],
              cell_size: int, hover_pos: Optional[Tuple[int, int]] = None) -> None:
    """
    Отрисовывает сетку клеток с оптимизацией.
    """
    if not grid:
        return

    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    try:
        # Оптимизация: предварительное создание rect
        rect = pygame.Rect(0, 0, cell_size, cell_size)

        # Отрисовка клеток
        for row in range(rows):
            rect.y = row * cell_size
            for col in range(cols):
                rect.x = col * cell_size

                # Быстрое определение цвета
                if grid[row][col]:
                    color = ALIVE_COLOR
                elif hover_pos and (row, col) == hover_pos:
                    color = HOVER_COLOR
                else:
                    continue  # Пропускаем отрисовку мёртвых клеток (экономия времени)

                pygame.draw.rect(screen, color, rect)

        # Отрисовка линий сетки (только если нужно)
        draw_grid_lines(screen, rows, cols, cell_size)

    except (IndexError, TypeError, pygame.error) as e:
        logger.error(f"Error drawing grid: {e}")


def draw_grid_lines(screen: pygame.Surface, rows: int, cols: int, cell_size: int) -> None:
    """
    Оптимизированная отрисовка линий сетки.
    """
    try:
        width = cols * cell_size
        height = rows * cell_size

        # Вертикальные линии (используем один вызов line для каждой)
        for x in range(0, width, cell_size):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, height))

        # Горизонтальные линии
        for y in range(0, height, cell_size):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (width, y))

    except pygame.error as e:
        logger.error(f"Error drawing grid lines: {e}")


# ========== РАБОТА С МЫШЬЮ ==========
def get_cell_from_mouse(pos: Tuple[int, int], cell_size: int,
                        rows: int, cols: int) -> Optional[Tuple[int, int]]:
    """
    Быстрое преобразование координат мыши в индексы клетки.
    """
    x, y = pos

    # Быстрая проверка границ
    if x < 0 or y < 0:
        return None

    grid_height = rows * cell_size
    if y >= grid_height:
        return None

    col = x // cell_size
    row = y // cell_size

    if row < rows and col < cols:
        return (row, col)
    return None


# ========== ОПТИМИЗИРОВАННЫЙ UI ==========
def draw_ui(screen: pygame.Surface, generation: int, speed: float,
            running: bool, rows: int, cols: int) -> None:
    """
    Отрисовывает UI с кэшированием текста.
    """
    try:
        font = _get_font(24)
        font_small = _get_font_small(18)

        screen_height = screen.get_height()

        # Статус с цветом
        status = "▶ RUNNING" if running else "⏸ PAUSED"
        status_color = (100, 255, 100) if running else (255, 100, 100)

        # Кэширование текста для часто обновляемых значений
        # (generation и speed обновляются часто, поэтому не кэшируем)
        info_items = [
            (f"Generation: {generation}", UI_TEXT_COLOR, (UI_PADDING, 5)),
            (f"Speed: {speed:.1f} FPS", UI_TEXT_COLOR, (UI_PADDING, 30)),
            (status, status_color, (UI_PADDING, 55)),
            (f"Grid: {rows}×{cols}", UI_TEXT_COLOR, (UI_PADDING, 80)),
        ]

        # Отрисовка информации
        for text, color, pos in info_items:
            surface = font.render(text, True, color)
            screen.blit(surface, pos)

        # Подсказки по управлению (статический текст, можно кэшировать)
        _draw_controls(screen, font_small, screen_height)

    except pygame.error as e:
        logger.error(f"Error drawing UI: {e}")


# Кэш для подсказок (рисуются один раз)
_controls_cache = None
_controls_positions = None


def _draw_controls(screen: pygame.Surface, font, screen_height: int) -> None:
    """
    Отрисовка подсказок с кэшированием.
    """
    global _controls_cache, _controls_positions

    if _controls_cache is None:
        controls = [
            "SPACE: Play/Pause | S/→: Step | R: Reset | C: Clear",
            "L: Load | F: Save | +/-: Speed | ESC: Exit"
        ]

        _controls_cache = []
        _controls_positions = []

        for i, control in enumerate(controls):
            surface = font.render(control, True, UI_TEXT_COLOR)
            _controls_cache.append(surface)
            _controls_positions.append((UI_PADDING, screen_height - CONTROLS_HEIGHT + i * 20))

    # Отрисовка кэшированных подсказок
    for surface, pos in zip(_controls_cache, _controls_positions):
        screen.blit(surface, pos)


# ========== УПРАВЛЕНИЕ ЦВЕТАМИ ==========
def handle_color_scheme(alive_color: Optional[Tuple[int, int, int]] = None,
                        dead_color: Optional[Tuple[int, int, int]] = None,
                        grid_color: Optional[Tuple[int, int, int]] = None,
                        ui_text_color: Optional[Tuple[int, int, int]] = None) -> None:
    """
    Обновляет цветовую схему.
    """
    global ALIVE_COLOR, DEAD_COLOR, GRID_COLOR, UI_TEXT_COLOR

    def is_valid_color(color):
        return (isinstance(color, (tuple, list)) and
                len(color) == 3 and
                all(0 <= c <= 255 for c in color))

    if alive_color is not None and is_valid_color(alive_color):
        ALIVE_COLOR = alive_color
    if dead_color is not None and is_valid_color(dead_color):
        DEAD_COLOR = dead_color
    if grid_color is not None and is_valid_color(grid_color):
        GRID_COLOR = grid_color
    if ui_text_color is not None and is_valid_color(ui_text_color):
        UI_TEXT_COLOR = ui_text_color

    # Сбрасываем кэш подсказок при смене цвета текста
    global _controls_cache
    if ui_text_color is not None:
        _controls_cache = None


# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def clear_screen(screen: pygame.Surface) -> None:
    """Очищает экран."""
    screen.fill(DEAD_COLOR)


def update_display() -> None:
    """Обновляет экран."""
    pygame.display.flip()


def get_display_size(screen: pygame.Surface, cell_size: int) -> Tuple[int, int]:
    """
    Возвращает количество строк и столбцов, помещающихся на экране.
    """
    width, height = screen.get_size()
    cols = width // cell_size
    rows = (height - UI_HEIGHT) // cell_size
    return rows, cols


def draw_cell(screen: pygame.Surface, row: int, col: int,
              cell_size: int, state: int) -> None:
    """
    Оптимизированная перерисовка одной клетки.
    """
    rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
    color = ALIVE_COLOR if state else DEAD_COLOR
    pygame.draw.rect(screen, color, rect)

    # Перерисовка линий сетки вокруг клетки
    x, y = rect.x, rect.y
    pygame.draw.line(screen, GRID_COLOR, (x, y), (x + cell_size, y))
    pygame.draw.line(screen, GRID_COLOR, (x, y), (x, y + cell_size))
    pygame.draw.line(screen, GRID_COLOR, (x + cell_size, y), (x + cell_size, y + cell_size))
    pygame.draw.line(screen, GRID_COLOR, (x, y + cell_size), (x + cell_size, y + cell_size))


# ========== ОПТИМИЗАЦИЯ ДЛЯ БОЛЬШИХ СЕТОК ==========
def draw_grid_optimized(screen: pygame.Surface, grid: List[List[int]],
                        cell_size: int, dirty_rects: List[pygame.Rect] = None) -> None:
    """
    Отрисовка только изменённых областей (для производительности).

    Args:
        dirty_rects: Список прямоугольников, которые нужно перерисовать
    """
    if dirty_rects is None:
        # Если нет списка изменений, рисуем всё
        draw_grid(screen, grid, cell_size)
        return

    for rect in dirty_rects:
        # Определяем границы в клетках
        start_row = rect.y // cell_size
        start_col = rect.x // cell_size
        end_row = (rect.y + rect.height) // cell_size + 1
        end_col = (rect.x + rect.width) // cell_size + 1

        # Перерисовываем только изменённые клетки
        for row in range(start_row, min(end_row, len(grid))):
            for col in range(start_col, min(end_col, len(grid[0]))):
                draw_cell(screen, row, col, cell_size, grid[row][col])
