import tkinter as tk

def board(canvas, height, width, cell, flicker):
    """
    This function draws the visual board using Tkinter package to draw the corresponding symbols in each cell. 
    Uses the measurements of the grid given to define each cell size and centralize the elements.

    Args:
        canvas: Tkinter object, visual board.
        height: Height of the board. 
        width: Width of the board. 
        cell: Filled board (grid).
        flicker: Defines blinking as False.

    Returns:
        None
    """

    # Defines the size of each cell based on the division of rows and columns by the grid size
    rows = ((height - 110) // len(cell))
    cols = (width // len(cell[0]))

    # Iterates through each cell, constructing the visual board based on the static board definition
    for i in range(len(cell)):
        for j in range(len(cell[i])):

            # Aligns the coordinates of each cell to display drawing centralized
            x_axis = j * cols + (0.5 * cols)
            y_axis = i * rows + (0.5 * rows)
            tag = ("dots", f"cell_{i}_{j}") # Defines the tag of each element to be able to delete it from canvas after

            # If a cell number is 1, it corresponds to a small dot 
            if cell[i][j] == 1: 
                canvas.create_oval(x_axis + 9, y_axis + 9, x_axis + cols - 10, y_axis + rows - 10, fill="white", tags=tag)

            # If a cell number is 2, it corresponds to a big dot 
            elif cell[i][j] == 2 and not flicker:
                canvas.create_oval(x_axis + 5, y_axis + 5, x_axis + cols - 5, y_axis + rows - 5, fill="white", tags=tag)

            # If a cell number is 3, it corresponds to a vertical wall
            elif cell[i][j] == 3:
                canvas.create_line(x_axis + cols // 2, y_axis, x_axis + cols // 2, y_axis + rows, width=3, fill="blue")
                
            # If a cell number is 4, it corresponds to a horizontal wall
            elif cell[i][j] == 4:
                canvas.create_line(x_axis, y_axis + rows // 2, x_axis + cols, y_axis + rows // 2, width=3, fill="blue")
                
            # If a cell number is 5, it corresponds to a top-right corner 
            elif cell[i][j] == 5:
                canvas.create_arc(j * cols, (i + 1) * rows, (j + 1) * cols, (i + 2) * rows, start=0, extent=90, width=3, outline="blue", style="arc")

            # If a cell number is 6, it corresponds to a top-left corner
            elif cell[i][j] == 6:
                canvas.create_arc((j + 1) * cols, (i + 1) * rows, (j + 2) * cols, (i + 2) * rows, start=90, extent=90, width=3, outline="blue", style="arc")

            # If a cell number is 7, it corresponds to a bottom-left corner 
            elif cell[i][j] == 7:
                canvas.create_arc((j + 1) * cols, i * rows, (j + 2) * cols, (i + 1) * rows, start=180, extent=90, width=3, outline="blue", style="arc")

            # If a cell number is 8, it corresponds to a bottom-right corner 
            elif cell[i][j] == 8:
                canvas.create_arc(j * cols, i * rows, (j + 1) * cols, (i + 1) * rows, start=270, extent=90, width=3, outline="blue", style="arc")

            # If a cell number is 9, it corresponds to the ghosts' gate
            elif cell[i][j] == 9:
                canvas.create_line(x_axis, y_axis + rows // 2, x_axis + cols, y_axis + rows // 2, width=3, fill="white")