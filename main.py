# Imports the necessary packages and functions to define the algorithm
import copy
import math
import tkinter as tk
from boards import static_board, modes
from maze_drawing import board
from PIL import Image, ImageTk
from functions import find_pacman, draw_pacman, get_ghosts_by_id, adjust_target
import random
from search import solvePacman, manhattan
import time

# Initializes important variables
height = 900
width = 800
cell = copy.deepcopy(static_board)
rows = ((height - 110) // len(cell))
cols = (width // len(cell[0]))
score = 0
state = 1
current_mode_index = 0
current_mode, mode_duration = modes[current_mode_index]
start_time = time.time()

def load_images():
    """
    This function initializes all images at once to avoid delays and glitching throughout the game.
    """
    global pacman_image, game_over_photo, press_start_image, ready_image, winning_image

    pacman_image = Image.open("pacman.png")
    pacman_image = pacman_image.resize((int(cols * 1.2), int(rows * 1.2)), Image.Resampling.LANCZOS)
    pacman_image = ImageTk.PhotoImage(pacman_image)

    press_start_image = Image.open("press_start.png")
    press_start_image = press_start_image.resize((int(cols * 25), int(rows * 16)), Image.Resampling.LANCZOS)
    press_start_image = ImageTk.PhotoImage(press_start_image)

    game_over_image = Image.open("game_over.png")
    game_over_image = game_over_image.resize((int(cols * 7), int(rows * 6)), Image.Resampling.LANCZOS)
    game_over_photo = ImageTk.PhotoImage(game_over_image)

    ready_image = Image.open("ready.png")
    ready_image = ready_image.resize((int(cols * 7), int(rows * 4)), Image.Resampling.LANCZOS)
    ready_image = ImageTk.PhotoImage(ready_image)

    winning_image = Image.open("winning.png")
    winning_image = winning_image.resize((int(cols * 20), int(rows * 20)), Image.Resampling.LANCZOS)
    winning_image = ImageTk.PhotoImage(winning_image)


def setup_game(canvas):
    """
    This function sets up the game initially by loading all images, defining positions and directions, and initiating objects and events. 
    
    Args:
        canvas: Filled board (grid).
    """

    global pacman_image, ghosts, game_over_photo, pacman_direction, state
    
    # Draws the initial canvas from the root definitions
    canvas.config(bg="black")
    load_images()
    state  = 1

    pacman_direction = "right"  
    # Updates Pacman's direction as a global variable being sent to the root as the user moves through keyboard.
    def update_pacman_direction(direction):
        pacman_direction = direction
        return pacman_direction

    # Creates a list for ghosts' images and defines their position and id accordingly
    ghost_images = [f"red.png", f"pink.png", f"blue.png", f"orange.png"]
    ghosts = []
    for i, image in enumerate(ghost_images): 
        if i == 0: 
            position = (13, 15)
            id = "blinky"
        if i == 1:
            position = (14, 16)
            id = "pinky"
        if i == 2:
            position = (16, 16)
            id = "inky"
        if i == 3: 
            position = (17, 15)
            id = "clyde"

        # Creates an object for each ghost, resizing the images to the cell size and adding the images to the canvas
        ghost = Ghost(image, position, id=id)
        ghost_image = Image.open(image)
        ghost_image = ghost_image.resize((int(cols * 1.2), int(rows * 1.2)), Image.Resampling.LANCZOS)
        ghost.photo = ImageTk.PhotoImage(ghost_image)
        ghost.image_id = canvas.create_image(
            # Centralizes the images' position
            (ghost.position[0] * cols),  
            (ghost.position[1] * rows),  
            image=ghost.photo, anchor="nw", tags=("ghost", ghost.id)  
        )
        ghosts.append(ghost) 

    # Makes each arrow key refer to an event update in Pacman's position
    root.bind("<Left>", lambda event: move_pacman(cell, update_pacman_direction("left"), canvas, height, width, pacman_image))
    root.bind("<Right>", lambda event: move_pacman(cell, update_pacman_direction("right"), canvas, height, width, pacman_image))
    root.bind("<Up>", lambda event: move_pacman(cell, update_pacman_direction("up"), canvas, height, width, pacman_image))
    root.bind("<Down>", lambda event: move_pacman(cell, update_pacman_direction("down"), canvas, height, width, pacman_image))
    draw_pacman(canvas, height, width , cell, 24, 14, False, pacman_image) 

def reset_game(canvas):
    """
    This function resets the game from a winning or losing state by redefining pacman's and ghosts' positions, deleting visual elements and setting up the game.

    Args:
        canvas: Filled board (grid).
    """

    global score, cell, pacman_direction, pacman_position

    # Resets default elements
    pacman_position = (24, 14)  
    pacman_direction = "right"
    score = 0

    canvas.delete("pacman")
    canvas.delete("ghost")
    canvas.delete("game_over")

    # Draws the game again
    cell = copy.deepcopy(static_board)
    setup_game(canvas)
    draw_pacman(canvas, height, width, cell, *pacman_position, False, pacman_image)

    # Unless the ghost is red, by default assume they start trapped in ghost house
    for ghost in ghosts:
        if ghost.id == "blinky":
            ghost.trapped = False
        ghost.reset_position()

    # Initiates additional images and gets event called to initiate game if space key is pressed
    canvas.create_image(5 * cols - (2.1 * cols), 7 * rows - (2.5 * rows), image=press_start_image, anchor="nw", tags="press_start")
    canvas.create_image(14 * cols - (1.7 * cols), 18 * rows - (0.6 * rows), image=ready_image, anchor="nw", tags="ready")
    root.unbind("<space>")
    root.bind("<space>", lambda event: start_game(canvas, ghosts))

def start_game(canvas, ghosts):
    """
    This function properly starts the game by deleting the additional images and running the game loop. 
    """

    global state 
    state = 1

    canvas.delete("ready")
    canvas.delete("press_start")
    canvas.delete("winning")
    run_game_loop(canvas, ghosts)

def update_score():
    """
    Updates the state and the score. Used as a function to be called after a delay.
    """

    global score, state
    score = 0
    state = 1

def run_game_loop(canvas, ghosts):
    """
    Defines the main game loop functionality by recursively calling update function to itself.
    """

    global root 

    def update(): 
        """
        Continuously update the game checking the current state, score, ghost state, time, and collision. 
        """

        global mode_index, current_mode, mode_duration, start_time

        if state != 1:
            return 
        
        if score >= 249: # If a winning state is found, update game 
            win(canvas, ghosts)
            root.after(100, update_score())
            return

        manage_ghost_release() # Check if any ghosts can be released

        # Keeps track of time to change the different modes (chase, scatter) throughout the game 
        current_time = time.time()
        if (current_time - start_time) >= mode_duration * 60:  
            mode_index += 1
            if mode_index < len(modes):
                current_mode, mode_duration = modes[mode_index]
                start_time = current_time  # Resets start time
            else:
                mode_index = len(modes) - 1
        
        # Updates the position of the ghosts and its mode if it is not trapped
        for ghost in ghosts:
            if not ghost.trapped:
                ghost.mode = current_mode 
                ghost.update(canvas)
                canvas.tag_raise(ghost.image_id)
        canvas.tag_raise("ghost")

        # Updates the game state continuously calling the update function if state is running and no winning mode was found
        update_game_state(canvas, ghosts, pacman_image) 
        if state == 1 and score < 249:
            root.after(100, update)

    update()

def update_game_state(canvas, ghosts, pacman_image):
    """
    Updates the state of the game by finding pacman's position, updating ghosts and checking if a collision was identified.
    """

    global state
    pacman_position = find_pacman(cell) 

    for ghost in ghosts:
        ghost.update(canvas)
        canvas.tag_raise(ghost.image_id)  

    # If a collision is found, resets state to 0
    if check_collision(pacman_position, ghosts, canvas): 
        state = 0
    
def win(canvas, ghosts): 
    """
    This function executes the appropriate actions if a winning state is identified (score >= 249).
    """

    global state 

    # Assigns game state as winning and resets the ghosts position
    state = 2 
    for ghost in ghosts:
        ghost.reset_position()

    # Deletes all the elements that could be moved in the board
    canvas.delete("ready")
    canvas.delete("game_over")
    canvas.delete("ghost")
    canvas.delete("dots")

    # Draws winning image and restarts the game after some seconds
    canvas.create_image(7 * cols - (1.4 * cols), 8 * rows - (0.6 * rows), image=winning_image, anchor="nw", tags="winning")
    canvas.create_image(5 * cols - (2 * cols), 14 * rows - (0.6 * rows), image=press_start_image, anchor="nw", tags="press_start")
    root.after(1000, lambda: reset_game(canvas))


def handle_collision(canvas):
    """
    This function executes the appropriate actions if collision is identified. 
    """
    global score, state

    if state != 1: # Ensures game is running
        return
    
    # Resets game state and score
    score = 0 
    state = 0 

    # Showcases game over image and resets the game after some seconds
    canvas.create_image(14 * cols - (1.75 * cols), 18 * rows - (1.9 * rows), image=game_over_photo, anchor="nw", tags="game_over")
    root.after(1000, lambda: reset_game(canvas))

def check_collision(pacman_position, ghosts, canvas):
    """
    Check if Pacman's position is the same as any of the ghosts' for collision. 

    Args:
        pacman_position: Current node of Pacman.
        ghosts: Objects of the class Ghost.
        canvas: Filled board (grid).

    Returns:
        bool: Boolean value for collision. 
    """

    global state

    if state != 1: # Ensures that if the game is not running, collision is always false
        return False

    for ghost in ghosts:
        if pacman_position == ghost.position:
            handle_collision(canvas)  # Takes action after collision is identified
            return True

def manage_ghost_release():
    """
    This function uses global variables of each ghost to update whether a ghost can go out of the ghost house or not based on the game score.
    """

    global score, ghosts

    ghosts[0].trapped = False # Red ghost is always free

    if score >= 60 and ghosts[1].trapped:  
        ghosts[1].trapped = False
    if score >= 160 and ghosts[2].trapped:  
        ghosts[2].trapped = False
    if score == 210 and ghosts[3].trapped:  
        ghosts[3].trapped = False

def main():
    """
    This function defines the main functionality of the game by defining Pacman, the ghosts, and initiating the game loop. 
    """

    global score, root, pacman_direction, pacman_image, ghosts

    # Initializes the root of the game using Tkinter
    root = tk.Tk()
    root.geometry("800x900")
    root.title("Let's Play Pacman!")

    # Draws the initial canvas from the root definitions
    canvas = tk.Canvas(root, width=width, height=height)
    canvas.pack()

    # Draws the game images for initial position
    setup_game(canvas)

    canvas.create_image(14 * cols - (1.7 * cols), 18 * rows - (0.6 * rows), image=ready_image, anchor="nw", tags="ready")
    canvas.create_image(5 * cols - (2.1 * cols), 7 * rows - (2.5 * rows), image=press_start_image, anchor="nw", tags="press_start")
    root.bind("<space>", lambda event: start_game(canvas, ghosts))

    root.mainloop()

class Ghost:
    def __init__(self, image_path, position, id):
        """
        Initializes an instance of the Ghost class.

        Parameters 
        ----------
        image_path: linked path
            A path to the ghost images in the folder.
        position: tuple
            Tuple containing the x and y positions of the ghost. 
        mode: string, default
            Defines the current mode of the ghosts.
        direction: string, default
            Initializes the current direction of the ghosts as left by default.
        id: string
            String representation of each ghosts' id.
        trapped: boolean, default
            Defines if ghost is in ghost house or not.
        move_update: int, fixed
            Defines the movement of the ghosts after three updates.
        counter: int 
            Counter for the current updates.
        """

        self.image = Image.open(image_path)
        self.position = position
        self.mode = "chase"  
        self.speed = 1 
        self.direction = "left"
        self.id = id
        self.trapped = True
        self.move_update = 3  
        self.counter = 0

    def reset_position(self): 
        """
        Once the game resets or the ghost is unable to play, reset its position to initial position (ghost house).
        """
        if self.id == "blinky":
            self.position = (13, 15)
        if self.id == "pinky":
            self.position = (14, 16)
        if self.id == "inky":
            self.position = (16, 16)
        if self.id == "clyde": 
            self.position = (17, 15)

    def update(self, canvas):
        """
        Possible modes for classic Pacman game are chase, and scatter. Defines the actions according to the current mode of each ghost.
        Ensures the ghost is not in the ghost house (still not in game) before proceeding and counts the time for each updating movement (makes the ghosts slower).
        """

        if self.trapped or self.counter < self.move_update:
            self.counter += 1
            return
        self.counter = 0

        if self.mode == "chase":
            pacman_row, pacman_col = find_pacman(cell)
            # If chase mode, each ghost will follow pacman
            self.move_towards_pacman(pacman_row, pacman_col, canvas)
        elif self.mode == "scatter":
            self.move_scatter(canvas)

    def move_towards_pacman(self, pacman_row, pacman_col, canvas):
        """
        This function defines the movement of each ghost by calculating its target position and finding the optimal path. 
        It continuously update its target as the game updates and Pacman moves

        Args:
            pacman_row: Current row of Pacman.
            pacman_col: Current column of Pacman.
            canvas: Visual definition of the board.
        """

        target_row, target_col = 0, 0

        if self.id == "blinky":  
            # Calculates Blinky's current target and finds the optimal path to the target
            target_row, target_col = pacman_row, pacman_col
            target_row, target_col = adjust_target(target_row, target_col, cell)
            path = solvePacman(self.position, (target_row, target_col), cell, manhattan)

            # If a path exists, gets the next step of action
            if path: 
                next_position = path[0]  
                self.position = next_position
                
                # Redraws the canvas with the updated ghost position
                canvas.coords(
                    self.image_id,
                    (self.position[1] * cols) + (cols // 2),
                    (self.position[0] * rows) + (rows // 2)
                )

        elif self.id == "pinky":  
            # Calculates Pinky's current target and finds the optimal path to the target
            target_row, target_col = self.calculate_pinky_target(pacman_row, pacman_col)
            target_row, target_col = adjust_target(target_row, target_col, cell)
            path = solvePacman(self.position, (target_row, target_col), cell, manhattan)

            # If a path exists, gets the next step of action 
            if path:
                next_position = path[0] 
                self.position = next_position
                
                # Redraws the canvas with the updated ghost position
                canvas.coords(
                    self.image_id,
                    (self.position[1] * cols) + (cols // 2),
                    (self.position[0] * rows) + (rows // 2)
                )

        elif self.id == "inky":  
            # Calculate Inky's target based on Pacman's position and Blinky's position
            blinky = get_ghosts_by_id(ghosts, "blinky")
            blinky_row, blinky_col = blinky.position

            target_row, target_col = self.calculate_inky_target(pacman_row, pacman_col, blinky_row, blinky_col, pacman_direction)
            target_row, target_col = adjust_target(target_row, target_col, cell)
            path = solvePacman(self.position, (target_row, target_col), cell, manhattan)

            # If a path exists, gets the next step of action
            if path:
                next_position = path[0] 
                self.position = next_position
                
                # Redraws the canvas with the updated ghost position
                canvas.coords(
                    self.image_id,
                    (self.position[1] * cols) + (cols // 2),
                    (self.position[0] * rows) + (rows // 2)
                )
            
        elif self.id == "clyde":  
            
            self.move_randomly(canvas)
        
    def calculate_pinky_target(self, pacman_row, pacman_col):
        """
        This function calculates the target node for the ghost pink. 

        Args:
            pacman_row: Current row of Pacman.
            pacman_col: Current column of Pacman.

        Returns:
            row, col: tuple
                Tuple of updated position for pinky.
        """

        if pacman_direction == "left":
            return pacman_row, pacman_col - 4
        
        elif pacman_direction == "right":
            return pacman_row, pacman_col + 4
        
        elif pacman_direction == "up":
            return pacman_row - 4, pacman_col - 4
        
        elif pacman_direction == "down":
            return pacman_row + 4, pacman_col

    def calculate_inky_target(self, pacman_row, pacman_col, blinky_row, blinky_col, pacman_direction):
        """
        This function returns the appropriate target for the ghost blue by Pacman's and Blinky's positions.

        Args:
            pacman_row: Current row of Pacman.
            pacman_col: Current column of Pacman.
            blinky_row: Current row of ghost Blinky (red).
            blinky_col: Current column of ghost Blinky (red).
            pacman_direction: The current direction Pacman is facing. 

        Returns:
            row, col: tuple
                Tuple of updated position for inky.
        """

        if pacman_direction == "left":
            calculation = int(2 * (math.sqrt((blinky_row - pacman_row)**2 + (blinky_col - (pacman_col - 2))**2)))
            
            if blinky_col == pacman_col - 2: 
                if blinky_row == pacman_row:
                    return blinky_col, blinky_row
                elif blinky_row > pacman_row: 
                    return blinky_col, blinky_row - calculation
                else: 
                    return blinky_col, blinky_row + calculation
                
            elif blinky_col > pacman_col - 2: 
                if blinky_row == pacman_row:
                    return blinky_col - calculation, blinky_row
                elif blinky_row > pacman_row: 
                    return blinky_col - calculation, blinky_row - calculation
                else: 
                    return blinky_col - calculation, blinky_row + calculation

            else: 
                if blinky_row == pacman_row:
                    return blinky_col + calculation, blinky_row
                elif blinky_row > pacman_row: 
                    return blinky_col + calculation, blinky_row - calculation
                else: 
                    return blinky_col + calculation, blinky_row + calculation
        
        if pacman_direction == "right":
            calculation = int(2 * (math.sqrt((blinky_row - pacman_row)**2 + (blinky_col - (pacman_col + 2))**2)))

            if blinky_col == pacman_col + 2: 
                if blinky_row == pacman_row:
                    return blinky_col, blinky_row
                elif blinky_row > pacman_row: 
                    return blinky_col, blinky_row - calculation
                else: 
                    return blinky_col, blinky_row + calculation
                
            elif blinky_col > pacman_col + 2: 
                if blinky_row == pacman_row:
                    return blinky_col - calculation, blinky_row
                elif blinky_row > pacman_row: 
                    return blinky_col - calculation, blinky_row - calculation
                else: 
                    return blinky_col - calculation, blinky_row + calculation

            else: 
                if blinky_row == pacman_row:
                    return blinky_col + calculation, blinky_row
                elif blinky_row > pacman_row: 
                    return blinky_col + calculation, blinky_row - calculation
                else: 
                    return blinky_col + calculation, blinky_row + calculation
        
        if pacman_direction == "up":
            calculation = int(2 * (math.sqrt((blinky_row - (pacman_row - 2))**2 + (blinky_col - (pacman_col - 2))**2)))
            
            if blinky_col == pacman_col - 2: 
                if blinky_row == pacman_row - 2:
                    return blinky_col, blinky_row
                elif blinky_row > pacman_row - 2: 
                    return blinky_col, blinky_row - calculation
                else: 
                    return blinky_col, blinky_row + calculation
                
            elif blinky_col > pacman_col - 2: 
                if blinky_row == pacman_row - 2:
                    return blinky_col - calculation, blinky_row
                elif blinky_row > pacman_row - 2: 
                    return blinky_col - calculation, blinky_row - calculation
                else: 
                    return blinky_col - calculation, blinky_row + calculation

            else: 
                if blinky_row == pacman_row - 2:
                    return blinky_col + calculation, blinky_row
                elif blinky_row > pacman_row - 2: 
                    return blinky_col + calculation, blinky_row - calculation
                else: 
                    return blinky_col + calculation, blinky_row + calculation
        
        if pacman_direction == "down":
            calculation = int(2 * (math.sqrt((blinky_row - (pacman_row + 2))**2 + (blinky_col - pacman_col)**2)))
            
            if blinky_col == pacman_col: 
                if blinky_row == pacman_row + 2:
                    return blinky_col, blinky_row
                elif blinky_row > pacman_row + 2: 
                    return blinky_col, blinky_row - calculation
                else: 
                    return blinky_col, blinky_row + calculation
                
            elif blinky_col > pacman_col: 
                if blinky_row == pacman_row + 2:
                    return blinky_col - calculation, blinky_row
                elif blinky_row > pacman_row + 2: 
                    return blinky_col - calculation, blinky_row - calculation
                else: 
                    return blinky_col - calculation, blinky_row + calculation

            else: 
                if blinky_row == pacman_row + 2:
                    return blinky_col + calculation, blinky_row
                elif blinky_row > pacman_row + 2: 
                    return blinky_col + calculation, blinky_row - calculation
                else: 
                    return blinky_col + calculation, blinky_row + calculation
                
    def move_scatter(self, canvas): 
        """
        This functions defines the appropriate target ghosts and movement for the 'scatter' mode.

        Args:
            canvas: Filled board (grid).
        """

        # Defines the target corner for each ghost, with red on top right, pink on the top left, blue on the bottom right and orange on bottom left
        scatter_targets = {
            'blinky': (0, len(cell[0]) - 1),  
            'pinky': (0, 0),                  
            'inky': (len(cell) - 1, len(cell[0]) - 1),  
            'clyde': (len(cell) - 1, 0)       
        }

        # Considers the adjusted targets and the best path to follow
        target_row, target_col = scatter_targets[self.id]
        target_row, target_col = adjust_target(target_row, target_col, cell)
        path = solvePacman(self.position, (target_row, target_col), cell, manhattan)

        # If the path exists, follow it by iteratively changing position
        if path:
            next_position = path[0]
            self.position = next_position
            canvas.coords(
                self.image_id,
                (self.position[1] * cols) + (cols // 2),
                (self.position[0] * rows) + (rows // 2)
            )

    def move_randomly(self, canvas):
        """
        This functions allows the ghosts to move randomly and it is defined as the default state for orange ghost.

        Args:
            canvas: Filled board (grid).
        """
    
        # Defines the possible directions and chooses a random new position
        direction = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])  # Left, right, up, down, 
        new_x = self.position[0] + direction[0]
        new_y = self.position[1] + direction[1]

        # Updates the ghost position
        if direction == (-1, 0):
            self.direction = "left"
        elif direction == (1, 0):
            self.direction = "right"
        elif direction == (0, -1):
            self.direction = "up"
        elif direction == (0, 1):
            self.direction = "down"

        # Ensures the new position is within the board and accessible cells
        if 0 <= new_x < len(cell[0]) and 0 <= new_y < len(cell):
            if cell[new_y][new_x] not in [3, 4, 5, 6, 7, 8, 9]: 

                # Updates the new position of the ghost on the board visualization
                self.position = (new_x, new_y)
                canvas.coords(self.image_id, new_x * cols, new_y * rows)

# PACMAN USER MOVEMENT -------------------------------------------------------
def move_pacman(cells, direction, canvas, height, width, pacman_image):
    """
    This function updates the board and consequences according to the user's movementation of Pacman.
    Uses the elements of images and drawings in canvas to update the board to the new state.

    Args:
        cells: Filled board (grid).
        direction: Direction of movement from user input.
        canvas: Tkinter object, visual board.
        height: Height of the board. 
        width: Width of the board. 
        pacman_image: Path to Pacman's image.
    """

    global score
    
    # Finds the current position of Pacman and stores as previous cell
    pacman_row, pacman_col = find_pacman(cells)
    leaving_row, leaving_col = pacman_row, pacman_col

    # Update Pacman's position based on the input movement from user (if movement does not hit a wall)
    if direction == "left" and cells[pacman_row][pacman_col - 1] not in [3, 4, 5, 6, 7, 8, 9]:
        cells[pacman_row][pacman_col] = 0 # Redefines the previously visited cell as empty space

        if cells[pacman_row][pacman_col - 1] == 1: # If the next cell is a small dot, score
            score += 1
            canvas.delete(f"cell_{pacman_row}_{pacman_col - 1}") # Delete the dot from canvas using its tag

        elif cells[pacman_row][pacman_col -1] == 2: # If the next cell contain a big dot, score differently
            score += 3
            canvas.delete(f"cell_{pacman_row}_{pacman_col - 1}")

        cells[pacman_row][pacman_col - 1] = 10 # Initialized Pacman's position in next cell
        pacman_col -= 1  

    if direction == "right" and cells[pacman_row][pacman_col + 1] not in [3, 4, 5, 6, 7, 8, 9]:
        cells[pacman_row][pacman_col] = 0

        if cells[pacman_row][pacman_col + 1] == 1:
            score += 1
            canvas.delete(f"cell_{pacman_row}_{pacman_col + 1}")

        elif cells[pacman_row][pacman_col + 1] == 2: 
            score += 3
            canvas.delete(f"cell_{pacman_row}_{pacman_col + 1}")

        cells[pacman_row][pacman_col + 1] = 10  
        pacman_col += 1  

    if direction == "up" and cells[pacman_row - 1][pacman_col] not in [3, 4, 5, 6, 7, 8, 9]:
        cells[pacman_row][pacman_col] = 0

        if cells[pacman_row - 1][pacman_col] == 1:
            score += 1
            canvas.delete(f"cell_{pacman_row - 1}_{pacman_col}")

        elif cells[pacman_row - 1][pacman_col] == 2: 
            score += 3
            canvas.delete(f"cell_{pacman_row - 1}_{pacman_col}")

        cells[pacman_row - 1][pacman_col] = 10 
        pacman_row -= 1  

    if direction == "down" and cells[pacman_row + 1][pacman_col] not in [3, 4, 5, 6, 7, 8, 9]:
        cells[pacman_row][pacman_col] = 0

        if cells[pacman_row + 1][pacman_col] == 1:
            score += 1
            canvas.delete(f"cell_{pacman_row + 1}_{pacman_col}")

        elif cells[pacman_row + 1][pacman_col] == 2: 
            score += 3
            canvas.delete(f"cell_{pacman_row + 1}_{pacman_col}")

        cells[pacman_row + 1][pacman_col] = 10  
        pacman_row += 1  

    # Update Pacman's image from the previous position to the next
    canvas.delete("pacman")
    draw_pacman(canvas, height, width, cell, pacman_row, pacman_col, False, pacman_image)

if __name__ == "__main__":
    main()