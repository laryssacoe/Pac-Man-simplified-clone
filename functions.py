from maze_drawing import board
from collections import deque

def find_pacman(cells):
    """
    Finds the current position of Pacman by keeping track of the representation of number 10 as the character.

    Args:
        cell: Board representation of state. 

    Returns:
        i: int
            Position row of Pacman.
        j: int
            Position column of Pacman.
    """
    for i, row in enumerate(cells): # Enumerates each row and searchs the columns of each row to find a cell = 10
        for j, cell in enumerate(row):
            if cell == 10:  
                return i, j
            
def draw_pacman(canvas, height, width, cell, row, col, flicker, image):
    """
    This function updated Pacman's position as it moves through the board by updating its image position.

    Args:
        canvas: Tkinter object, visual board.
        height: Height of the board. 
        width: Width of the board. 
        cell: Filled board (grid).
        row: Current row for Pacman.
        col: Current column for Pacman.
        flicker: Defines blinking as False.
        image: Path to Pacman's image.

    Returns:
        None
    """

    # Calculates the division of cells in the board 
    rows = ((height - 110) // len(cell))
    cols = (width // len(cell[0]))

    # Centralizes the image by getting the top-left corner
    x_axis = col * cols + (0.5 * cols)
    y_axis = row * rows + (0.5 * rows)

    # Creates Pacman's image in the given position (anchoring centralized)
    canvas.create_image(x_axis, y_axis, image=image, anchor="nw", tags="pacman")

    # Redraws the board sending a new canvas with updated image
    board(canvas, height, width, cell, False)

def get_ghosts_by_id(ghosts, id):
    """
    This function returns the ghost object given the list of objects and its id. 
    It is later used to get each ghost position.

    Args:
        ghosts: List of ghosts objects. 
        id: String representing the id of each Ghost object. 

    Returns:
        ghost: object. 
            Ghost object of the class 'Ghost'.
    """
    
    for ghost in ghosts:
        if ghost.id == id:
            return ghost
        
def boundaries(row, col, cell): 
    """
    This function intends to ensure that the rows and columns of a ghost's target is within the boundaries of the board. 

    Args:
        row: Current row of the ghost.
        col: Current column of the ghost.
        cell: Filled board (grid).

    Returns:
        current_row: int
            Updated row target for ghost.
        current_col: int
            Updated column target for ghost.
    """

    max_rows = len(cell) 
    max_cols = len(cell[0]) 
    current_row = row
    current_col = col

    # Ensures neither the rows or columns are smaller than 0 or bigger that its rows/cols boundaries
    if row < 0:
        current_row = 0

        if col < 0:
            current_col = 0 
        elif col > max_cols:
            current_col = max_cols - 1
        
    elif row >= max_rows:
        current_row = max_rows -1 

        if col < 0:
            current_col = 0 
        elif col > max_cols:
            current_col = max_cols - 1
        
    else:
        if col < 0:
            current_col = 0 
        elif col > max_cols:
            current_col = max_cols - 1

    return current_row, current_col # Returns the value of the row and column that are within board

def adjust_target(row, col, cell):
    """
    This function adjusts a ghost's target if it is within an unaccessible cell. 

    Args:
        row: Current row of the ghost.
        col: Current column of the ghost.
        cell: Filled board (grid).

    Returns:
        current_row: int
            Updated row target for ghost.
        current_col: int
            Updated column target for ghost.
    """

    max_rows = len(cell)
    max_cols = len(cell[0])

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (1, -1), (-1, 1), (-1, -1)]  # Left, right, up, down, diagonals

    row, col = boundaries(row, col, cell) # Gets the row and column within the boundaries

    # Initializes visited set and queue of successor nodes
    queue = [(row, col)]
    visited = set([(row, col)])  

    while queue:
        current_row, current_col = queue.pop(0)

        # Check if position is within boundaries and not a wall
        if cell[current_row][current_col] not in [3, 4, 5, 6, 7, 8]: 
            return current_row, current_col 

        # Add adjacent positions to the queue
        for x, y in directions:
            new_row, new_col = current_row + x, current_col + y
            if 0 <= new_row < max_rows and 0 <= new_col < max_cols:
                if (new_row, new_col) not in visited:
                    visited.add((new_row, new_col))
                    queue.append((new_row, new_col))