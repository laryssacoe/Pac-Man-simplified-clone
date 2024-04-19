
# Pac-Man simplified clone
## Table of Contents

- [About the Project](#about-the-project)
- [Built With](#built-with)
- [Installation](#installation)
- [Usage/Examples](#usageexamples)
- [Functionality](#functionality)
- [Demonstration](#demonstration)
- [References](#references)


    
## About the Project

The objective of this project was to develop a simplified copy of the classic Pac-Man arcade game using Python and Tkinter as the primary package. 

The game includes visuals from the original Pac-Man game, such as the corresponding board, the colored ghosts, the ghost house, the yellow Pac-Man, the big and small dots, and the references to text elements. The project is playable and the Pac-Man can be commanded by user input using the arrow keys on the keyboard. The ghosts are programmed by AI behavior, and each has a different strategy for catching Pac-Man. A winning state occurs if Pac-Man eats all the dots before colliding with any ghost. A gameover occurs if any collision between Pac-Man and a ghost happens. 


## Built With

* [Python](https://www.python.org/)


## Installation

In order to run this project, you need to: 

* Install the latest version of Python in (https://www.python.org/downloads/)

* Create  a virtual environment: 
```bash
  python -m venv venv
```
* Download the Source code and run OR go to GitHub Repository, get the URL and input: 
```bash
  git clone <(https://github.com/laryssacoe/Flask-web-app-with-IoT-integration.git)>
```

### Libraries needed 

Some libraries used are built-in Python, while others require installation:

* Tkinter

```bash
  pip install tkinter
```

* PIL (Pillow) (Ensure that you install the correct version, if error occurs, try 'pillow')

```bash
  pip install Pillow
```
     
## Usage/Examples

Demonstration of code snippets and their purpose. 

* Update ghosts functionality: 
Initiates a function that checks if the ghosts are allowed to move and defines the movement of each ghost based on its mode, which calls upon the movement function that searches the best path using A* search algorithm.

```python
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
```


* Set up game function: 
This function defines the appropriate initialization of the attributes of the game, including Pac-Man's image and position, ghosts images, the board and more. 

```python
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
}
```


## Functionality

The user is able to control the Pac-Man using the arrow keys on the keyboard and each action has a corresponding consequence in the board and a visual matching.

![Imgur](https://i.imgur.com/d5ew9Fd.png)

This image exemplifies the initial state of the game.


## Demonstration

The following videos demonstrate the functionality of game states.

Link to the Google Drive: (https://drive.google.com/drive/folders/1pfUEgen30wV8ec6_VU-ikYC3GqENIn6S?usp=sharing)

## References

 - [Ghosts_Behavior](https://gameinternals.com/understanding-pac-man-ghost-behavior)
 - [Pacman_Images](https://pacman.live/play.html)
