"""
Модуль с логикой игры "Жизнь".
Роль B: Подсчёт соседей и вычисление следующих поколений.
"""

from typing import List, Tuple


# Смещения для 8 соседних клеток
NEIGHBOR_OFFSETS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1), (1, 0), (1, 1)
]


def apply_boundary_condition(
    board: List[List[int]],
    row: int,
    col: int,
    wrap_edges: bool = True
) -> Tuple[int, int]:
    """
    Корректирует координаты с учётом границ.

    Args:
        board: Игровое поле
        row: Индекс строки
        col: Индекс столбца
        wrap_edges: Флаг замкнутых границ

    Returns:
        Скорректированные координаты (row, col)
    """
    if not wrap_edges:
        return row, col

    total_rows = len(board)
    total_cols = len(board[0])

    return row % total_rows, col % total_cols


def count_live_neighbors(
    board: List[List[int]],
    row: int,
    col: int,
    wrap_edges: bool = True
) -> int:
    """
    Считает количество живых соседей вокруг клетки.

    Args:
        board: Игровое поле
        row: Индекс строки
        col: Индекс столбца
        wrap_edges: Флаг замкнутых границ

    Returns:
        Количество живых соседей (от 0 до 8)
    """
    total_rows = len(board)
    total_cols = len(board[0])
    live_neighbors = 0

    for row_offset, col_offset in NEIGHBOR_OFFSETS:
        neighbor_row = row + row_offset
        neighbor_col = col + col_offset

        if wrap_edges:
            neighbor_row, neighbor_col = apply_boundary_condition(
                board, neighbor_row, neighbor_col, wrap_edges
            )
        else:
            if (
                neighbor_row < 0
                or neighbor_row >= total_rows
                or neighbor_col < 0
                or neighbor_col >= total_cols
            ):
                continue

        live_neighbors += board[neighbor_row][neighbor_col]

    return live_neighbors


def next_generation(
    board: List[List[int]],
    wrap_edges: bool = True
) -> List[List[int]]:
    """
    Создаёт следующее поколение клеток по правилам игры "Жизнь".

    Args:
        board: Текущее поколение
        wrap_edges: Флаг замкнутых границ

    Returns:
        Новое поколение клеток
    """
    total_rows = len(board)
    total_cols = len(board[0])

    new_board = [[0 for _ in range(total_cols)] for _ in range(total_rows)]

    for row in range(total_rows):
        for col in range(total_cols):
            neighbors_count = count_live_neighbors(
                board, row, col, wrap_edges
            )

            if (
                (board[row][col] == 1 and neighbors_count in (2, 3))
                or (board[row][col] == 0 and neighbors_count == 3)
            ):
                new_board[row][col] = 1

    return new_board


def count_live_cells(board: List[List[int]]) -> int:
    """
    Возвращает общее количество живых клеток.

    Args:
        board: Игровое поле

    Returns:
        Количество живых клеток
    """
    return sum(sum(row) for row in board)


def is_stable(
    previous_board: List[List[int]],
    current_board: List[List[int]]
) -> bool:
    """
    Проверяет, стабилизировалась ли система (нет изменений).

    Args:
        previous_board: Предыдущее поколение
        current_board: Текущее поколение

    Returns:
        True если поколения идентичны
    """
    return previous_board == current_board
