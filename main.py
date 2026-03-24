import pygame
import sys
from data import create_empty_grid, random_grid, load_grid_from_file
from rules import next_generation
import game


def handle_keyboard_input(event: pygame.event.Event, state: dict) -> tuple[list[list[int]], dict]:
    """
    Processes keyboard events to control the simulation.

    Args:
        event (pygame.event.Event): The keyboard event.
        state (dict): The current game state containing grid, running status, speed, and generation.

    Returns:
        tuple: Updated grid and game state dictionary.
    """
    grid = state['grid']
    running = state['running']
    speed = state['speed']
    generation = state['generation']

    if event.key == pygame.K_SPACE:
        state['running'] = not running
    elif event.key == pygame.K_s or event.key == pygame.K_RIGHT:
        grid = next_generation(grid, wrap_edges=True)
        state['generation'] = generation + 1
    elif event.key == pygame.K_r:
        grid = random_grid(len(grid), len(grid[0]), prob=0.5)
        state['generation'] = 0
    elif event.key == pygame.K_c:
        grid = create_empty_grid(len(grid), len(grid[0]))
        state['generation'] = 0
    elif event.key == pygame.K_l:
        filename = 'config.txt'
        grid = load_grid_from_file(filename)
        state['generation'] = 0
    elif event.key == pygame.K_f:
        filename = 'save.txt'
        save_grid_to_file(grid, filename)
    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
        state['speed'] = min(state['speed'] + 1, 60)
    elif event.key == pygame.K_MINUS:
        state['speed'] = max(state['speed'] - 1, 1)
    elif event.key == pygame.K_q:
        pygame.quit()
        sys.exit()

    return grid, state


def handle_mouse_click(event: pygame.event.Event, grid: list[list[int]], rows: int, cols: int) -> list[list[int]]:
    """
    Handles mouse click events to toggle individual cells on the grid.

    Args:
        event (pygame.event.Event): Mouse event.
        grid (list of list of int): The current grid.
        rows (int): Number of rows in the grid.
        cols (int): Number of columns in the grid.

    Returns:
        list of list of int: The updated grid after toggling the clicked cell.
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


def save_grid_to_file(grid: list[list[int]], filename: str) -> None:
    """
    Saves the current grid configuration into a text file.

    Args:
        grid (list of list of int): The grid to save.
        filename (str): Path to the file where grid will be saved.

    Returns:
        None
    """
    try:
        with open(filename, 'w') as f:
            for row in grid:
                line = ''.join(str(cell) for cell in row)
                f.write(line + '\n')
        print(f"Configuration saved successfully to {filename}")
    except Exception:
        print(f"Error writing to file {filename}")


def main() -> None:
    """
    Main function for the game loop.

    Initializes display, grid, and state, then processes events,
    updates grid, and renders frames continuously.
    """
    rows, cols = 30, 40
    cell_size = 20
    screen, cell_size, rows, cols = game.init_display(rows, cols, cell_size)

    grid = random_grid(rows, cols, prob=0.5)
    state = {
        'grid': grid,
        'running': False,
        'speed': 10,
        'generation': 0
    }

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                state['grid'], state = handle_keyboard_input(event, state)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                state['grid'] = handle_mouse_click(event, state['grid'], rows, cols)

        if state['running']:
            state['grid'] = next_generation(state['grid'], wrap_edges=True)
            state['generation'] += 1

        screen.fill(game.DEAD_COLOR)
        mouse_pos = pygame.mouse.get_pos()
        hover_cell = game.get_cell_from_mouse(mouse_pos, cell_size, rows, cols)
        game.draw_grid(screen, state['grid'], cell_size, hover_cell)
        game.draw_ui(screen, state['generation'], state['speed'], state['running'], rows, cols)
        pygame.display.flip()
        clock.tick(state['speed'])


if __name__ == "__main__":
    main()
