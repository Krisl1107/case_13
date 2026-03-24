import pygame
import logging
from typing import Optional, Tuple, List

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Colors for the game: Alive cells, Dead cells, Grid lines, UI text, highlight on hover
ALIVE_COLOR = (255, 20, 147)
DEAD_COLOR = (30, 30, 30)
GRID_LINE_COLOR = (60, 60, 60)
UI_TEXT_COLOR = (255, 255, 255)
HOVER_COLOR = (100, 100, 100)

# Interface settings
UI_PANEL_HEIGHT = 100  # Height of the UI panel at the bottom
UI_MARGIN = 10         # Margins around UI elements
CONTROLS_HEIGHT = 40   # Height of control instructions area

# Fonts cache
_fonts_cache = {}
_small_fonts_cache = {}

def get_font(size: int = 24):
    """
    Get a font of the specified size. Caches fonts for better performance.

    Args:
        size (int): Font size.

    Returns:
        pygame.font.Font: Font object.
    """
    if size not in _fonts_cache:
        _fonts_cache[size] = pygame.font.Font(None, size)
    return _fonts_cache[size]

def get_small_font(size: int = 18):
    """
    Get a small font of the specified size. Uses caching.

    Args:
        size (int): Font size.

    Returns:
        pygame.font.Font: Font object.
    """
    if size not in _small_fonts_cache:
        _small_fonts_cache[size] = pygame.font.Font(None, size)
    return _small_fonts_cache[size]

def init_display(total_rows: int, total_cols: int, cell_size: int = 20) -> Tuple[pygame.Surface, int, int, int]:
    """
    Initialize the game window based on grid dimensions.

    Args:
        total_rows (int): Number of rows.
        total_cols (int): Number of columns.
        cell_size (int): Size of each cell.

    Returns:
        Tuple containing the display surface, cell size, total rows, and total columns.
    """
    pygame.init()
    width = total_cols * cell_size
    height = total_rows * cell_size + UI_PANEL_HEIGHT
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Conway's Game of Life")
    return screen, cell_size, total_rows, total_cols

def draw_grid(screen: pygame.Surface, grid: List[List[int]],
              cell_size: int, hover_cell: Optional[Tuple[int, int]] = None) -> None:
    """
    Draws the current state of the grid. Efficiently renders only necessary parts,
    highlighting the cell under the cursor.

    Args:
        screen (pygame.Surface): Surface to draw on.
        grid (list of list of int): 2D array with cell states.
        cell_size (int): Size of each cell.
        hover_cell (tuple, optional): Cell coordinates under the cursor.
    """
    if not grid:
        return
    total_rows = len(grid)
    total_cols = len(grid[0]) if total_rows > 0 else 0
    rect = pygame.Rect(0, 0, cell_size, cell_size)
    try:
        for row_idx in range(total_rows):
            rect.y = row_idx * cell_size
            for col_idx in range(total_cols):
                rect.x = col_idx * cell_size
                cell_value = grid[row_idx][col_idx]
                if cell_value:
                    color = ALIVE_COLOR
                elif hover_cell and (row_idx, col_idx) == hover_cell:
                    color = HOVER_COLOR
                else:
                    continue
                pygame.draw.rect(screen, color, rect)
        draw_grid_lines(screen, total_rows, total_cols, cell_size)
    except (IndexError, TypeError, pygame.error) as e:
        logger.error(f"Error during drawing: {e}")

def draw_grid_lines(screen: pygame.Surface, rows: int, cols: int, cell_size: int) -> None:
    """
    Draws grid lines on the surface.

    Args:
        screen (pygame.Surface): Surface to draw on.
        rows (int): Number of rows.
        cols (int): Number of columns.
        cell_size (int): Size of each cell.
    """
    try:
        width = cols * cell_size
        height = rows * cell_size
        for x in range(0, width, cell_size):
            pygame.draw.line(screen, GRID_LINE_COLOR, (x, 0), (x, height))
        for y in range(0, height, cell_size):
            pygame.draw.line(screen, GRID_LINE_COLOR, (0, y), (width, y))
    except pygame.error as e:
        logger.error(f"Error during drawing grid lines: {e}")

def get_cell_from_mouse(mouse_pos: Tuple[int, int], cell_size: int,
                        total_rows: int, total_cols: int) -> Optional[Tuple[int, int]]:
    """
    Converts mouse position to grid cell coordinates.

    Args:
        mouse_pos (tuple): Mouse position (x, y).
        cell_size (int): Size of each cell.
        total_rows (int): Total number of rows.
        total_cols (int): Total number of columns.

    Returns:
        Tuple (row, col) if inside the grid, or None.
    """
    x, y = mouse_pos
    if x < 0 or y < 0:
        return None
    grid_height = total_rows * cell_size
    if y >= grid_height:
        return None
    col_idx = x // cell_size
    row_idx = y // cell_size
    if row_idx < total_rows and col_idx < total_cols:
        return (row_idx, col_idx)
    return None

def draw_ui(screen: pygame.Surface, generation: int, speed: float,
            is_running: bool, total_rows: int, total_cols: int) -> None:
    """
    Draws info panel: current generation, speed, game state, and grid size.

    Args:
        screen (pygame.Surface): Surface to draw on.
        generation (int): Current generation number.
        speed (float): Simulation speed (FPS).
        is_running (bool): Game running or paused.
        total_rows (int): Number of rows.
        total_cols (int): Number of columns.
    """
    try:
        main_font = get_font(24)
        small_font = get_small_font(18)
        height = screen.get_height()
        status_text = "▶ RUNNING" if is_running else "⏸ PAUSED"
        status_color = (100, 255, 100) if is_running else (255, 100, 100)
        info_items = [
            (f"Generation: {generation}", UI_TEXT_COLOR, (UI_MARGIN, 5)),
            (f"Speed: {speed:.1f} FPS", UI_TEXT_COLOR, (UI_MARGIN, 30)),
            (status_text, status_color, (UI_MARGIN, 55)),
            (f"Grid: {total_rows}×{total_cols}", UI_TEXT_COLOR, (UI_MARGIN, 80)),
        ]
        for text, color, position in info_items:
            surface = main_font.render(text, True, color)
            screen.blit(surface, position)
        _draw_control_instructions(screen, small_font, height)
    except pygame.error as e:
        logger.error(f"Error during UI drawing: {e}")

_controls_cache = None
_controls_positions = None

def _draw_control_instructions(screen: pygame.Surface, font, screen_height: int) -> None:
    """
    Draws control instructions at the bottom of the screen. Uses cache.

    Args:
        screen (pygame.Surface): Surface to draw on.
        font (pygame.font.Font): Font for text.
        screen_height (int): Height of the window.
    """
    global _controls_cache, _controls_positions
    if _controls_cache is None:
        controls_lines = [
            "SPACE: Play/Pause | S/→: Step | R: Reset | C: Clear",
            "L: Load | F: Save | +/-: Speed | ESC: Exit"
        ]
        _controls_cache = []
        _controls_positions = []
        for idx, line in enumerate(controls_lines):
            text_surf = font.render(line, True, UI_TEXT_COLOR)
            _controls_cache.append(text_surf)
            _controls_positions.append((UI_MARGIN, screen_height - CONTROLS_HEIGHT + idx * 20))
    for surf, pos in zip(_controls_cache, _controls_positions):
        screen.blit(surf, pos)

def handle_color_scheme(alive: Optional[Tuple[int, int, int]] = None,
                        dead: Optional[Tuple[int, int, int]] = None,
                        grid: Optional[Tuple[int, int, int]] = None,
                        ui_text: Optional[Tuple[int, int, int]] = None) -> None:
    """
    Changes colors: for alive cells, dead cells, grid lines, and UI text.

    Args:
        alive (tuple, optional): RGB for alive cells.
        dead (tuple, optional): RGB for dead cells.
        grid (tuple, optional): RGB for grid lines.
        ui_text (tuple, optional): RGB for UI text.
    """
    global ALIVE_COLOR, DEAD_COLOR, GRID_LINE_COLOR, UI_TEXT_COLOR
    def valid_color(c):
        return isinstance(c, (tuple, list)) and len(c) == 3 and all(0 <= val <= 255 for val in c)
    if alive and valid_color(alive):
        ALIVE_COLOR = alive
    if dead and valid_color(dead):
        DEAD_COLOR = dead
    if grid and valid_color(grid):
        GRID_LINE_COLOR = grid
    if ui_text and valid_color(ui_text):
        UI_TEXT_COLOR = ui_text
    global _controls_cache
    if ui_text:
        _controls_cache = None

def clear_screen(screen: pygame.Surface) -> None:
    """
    Clears the entire surface.

    Args:
        screen (pygame.Surface): Surface to clear.
    """
    screen.fill(DEAD_COLOR)

def update_display() -> None:
    """
    Updates the display.
    """
    pygame.display.flip()

def get_display_size(screen: pygame.Surface, cell_size: int) -> Tuple[int, int]:
    """
    Returns the size of the display in cells.

    Args:
        screen (pygame.Surface): Surface.
        cell_size (int): Size of each cell.

    Returns:
        Tuple (rows, cols).
    """
    width, height = screen.get_size()
    total_rows = height // cell_size
    total_cols = width // cell_size
    return total_rows, total_cols
