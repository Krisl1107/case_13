from typing import List, Tuple


neighbor_offsets = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1), (1, 0), (1, 1)
]


def fix_grid_boundaries(
    game_board: List[List[int]],
    current_row: int,
    current_col: int,
    wrap_edges: bool = True
) -> Tuple[int, int]:
    """
    Ensures that the coordinates stay within the grid boundaries, or wraps them if needed.

    Args:
        game_board: The game board as a list of lists
        current_row: Current row index
        current_col: Current column index
        wrap_edges: Whether to enable wrap-around for edges

    Returns:
        Tuple with corrected (row, column) indices
    """
    if not wrap_edges:
        return current_row, current_col

    total_rows = len(game_board)
    total_cols = len(game_board[0])

    corrected_row = current_row % total_rows
    corrected_col = current_col % total_cols

    return corrected_row, corrected_col


def count_live_neighbors(
    game_board: List[List[int]],
    row_index: int,
    col_index: int,
    wrap_edges: bool = True
) -> int:
    """
    Counts how many neighboring cells are alive around a specific cell.

    Args:
        game_board: The game board as a list of lists
        row_index: Row position of the cell
        col_index: Column position of the cell
        wrap_edges: Whether to enable wrap-around for edges

    Returns:
        Number of live neighboring cells (0-8)
    """
    total_rows = len(game_board)
    total_cols = len(game_board[0])
    alive_neighbors_count = 0

    for delta_row, delta_col in neighbor_offsets:
        neighbor_row = row_index + delta_row
        neighbor_col = col_index + delta_col

        if wrap_edges:
            neighbor_row, neighbor_col = fix_grid_boundaries(
                game_board, neighbor_row, neighbor_col, wrap_edges
            )
        else:
            if (
                neighbor_row < 0
                or neighbor_row >= total_rows
                or neighbor_col < 0
                or neighbor_col >= total_cols
            ):
                continue

        alive_neighbors_count += game_board[neighbor_row][neighbor_col]

    return alive_neighbors_count

def next_generation(
    current_board: List[List[int]],
    wrap_edges: bool = True
) -> List[List[int]]:
    """
    Creates the next generation based on the current state following "Game of Life" rules.

    Args:
        current_board: The current grid of cells
        wrap_edges: Whether to enable wrap-around for edges

    Returns:
        New grid of cells representing the next generation
    """
    rows_count = len(current_board)
    cols_count = len(current_board[0])

    new_board = [[0 for _ in range(cols_count)] for _ in range(rows_count)]

    for row_idx in range(rows_count):
        for col_idx in range(cols_count):
            neighbors = count_live_neighbors(current_board, row_idx, col_idx, wrap_edges)

            if (current_board[row_idx][col_idx] == 1 and neighbors in (2, 3)) or \
               (current_board[row_idx][col_idx] == 0 and neighbors == 3):
                new_board[row_idx][col_idx] = 1

    return new_board

def count_live_cells_on_board(
    game_board: List[List[int]]
) -> int:
    """
    Counts how many cells are alive on the entire board.

    Args:
        game_board: The game board as a list of lists

    Returns:
        Total number of live cells
    """
    total_alive = sum(sum(row) for row in game_board)
    return total_alive

def check_if_stable(
    prev_board: List[List[int]],
    current_board: List[List[int]]
) -> bool:
    """
    Checks if the game has stabilized — that is, no changes between generations.

    Args:
        prev_board: The previous generation grid
        current_board: The current generation grid

    Returns:
        True if no changes occur, false otherwise
    """
    return prev_board == current_board
