import json
import pathlib
import random
from os import mkdir
from os.path import exists

from PIL import Image

working_dir = pathlib.Path().resolve()
storage_dir = working_dir.joinpath("snake")
export_dir = working_dir.joinpath("snake_bmps")

if not exists(storage_dir):
    mkdir(storage_dir)

frame = -1
slot = 0
slots = [[]]

filename = input("Filename: ")

def setup_frame(initial=False):
    global frame, slot, slots
    if frame < 122:
        slots[slot].append([])
        frame += 1
        for i in range(44):
            slots[slot][frame].append([])
            for j in range(11):
                slots[slot][frame][i].append(initial)
    elif slot < 7:
        slots.append([])
        frame = -1
        slot += 1
        return setup_frame()
    else:
        return False
    return True

def render():
    for image_id, image in enumerate(slots):
        img = Image.new('RGB', (48 * len(image), 11), "black")  # Create a new black image
        pixels = img.load()  # Create the pixel map
        for frame in range(len(image)):
            for i in range(44):
                for j in range(11):
                    if image[frame][i][j]:
                        pixels[frame * 48 + i, j] = (255, 255, 255)
            for i in range(4):
                for j in range(11):
                    pixels[frame * 48 + 44 + i, j] = (255, 0, 0)

        if not exists(export_dir):
            mkdir(export_dir)

        # Create one image for each frame slot (might not be needed as we should be able to just use one large image)
        img.save(export_dir.joinpath(filename + f"_{image_id}.bmp"))

    with open(storage_dir.joinpath(filename + ".json"), "w") as f:
        json.dump(slots, f)

# actual game logic
snake = []
fruit = dict(x=-1, y=-1)

# Current maximum we were safely able to flash is 32kb which is roughly 4*123 frames worth of snake.
# The chip should be able to support more, but the flashing tool was originally locked down to 8kb
# In the future we hope to be able to move this stuff to a custom firmware so it runs in realtime on the actual display
frame_count = min(int(input("Length (in s): ")) * 15, 123*4)
print(f"Running for {frame_count} frames")

dead = False
done = False

def move_or_deviate(x, y, x_mov, y_mov, depth = 0):
    if depth < 3:
        if not would_snake_selfintersect(x_mov, y_mov):
            snake.insert(0, dict(x=wrap_to_width(x + x_mov), y=wrap_to_height(y + y_mov)))
        else:
            move_or_deviate(x, y, -y_mov, x_mov, depth + 1)

def do_logicstep():
    global dead, done
    if not dead:
        head = snake[0]

        if head["x"] < fruit["x"]:
            move_or_deviate(head["x"], head["y"], 1, 0)
        elif head["x"] > fruit["x"]:
            move_or_deviate(head["x"], head["y"], -1, 0)
        elif head["y"] < fruit["y"]:
            move_or_deviate(head["x"], head["y"], 0, 1)
        else:
            move_or_deviate(head["x"], head["y"], 0, -1)

        if not does_fruit_intersect():
            snake.pop()
        else:
            place_fruit()

        if does_snake_selfintersect():
            dead = True
            print(f"Snake dies on frame: {frame}")
    elif len(snake) > 0:
        snake.pop()
    else:
        done = True

def do_drawstep():
    global slots
    if not setup_frame():
        print("Ran out of frames, i break now lol")
        exit(-1)

    for piece in snake:
        slots[slot][frame][wrap_to_width(piece["x"])][wrap_to_height(piece["y"])] = True

    slots[slot][frame][fruit["x"]][fruit["y"]] = True

def wrap_to_width(x):
    x %= 44
    while x < 0:
        x += 44
    return x

def wrap_to_height(y):
    y %= 11
    while y < 0:
        y += 11
    return y

def place_fruit():
    global fruit

    while does_fruit_intersect() or fruit["x"] == -1 or fruit["y"] == -1:
        fruit["x"] = random.randint(0, 43)
        fruit["y"] = random.randint(0, 10)


def does_fruit_intersect():
    for piece in snake:
        if fruit["x"] == piece["x"] and fruit["y"] == piece["y"]:
            return True
    return False


def does_snake_selfintersect():
    for i, piece1 in enumerate(snake):
        for j, piece2 in enumerate(snake):
            if i != j and piece1["x"] == piece2["x"] and piece1["y"] == piece2["y"]:
                return True
    return False

def would_snake_selfintersect(x_mov, y_mov):
    for piece in snake[1:]:
        if snake[0]["x"] + x_mov == piece["x"] and snake[0]["y"] + y_mov == piece["y"]:
            return True
    return False

# Setup
# First snake element is the head, so we need to insert it this way
snake.append(dict(x=11, y=5))
snake.append(dict(x=10, y=5))
snake.append(dict(x=9, y=5))

place_fruit()

while frame*(slot + 1) < frame_count - len(snake) - 10 and not done:
    do_drawstep()
    do_logicstep()

# Kill the snake if we reach the max amount of frames we can currently flash
if not done:
    dead = True
    # Normally we would have a draw step here, but the snake hasn't actually realized it died
    # So we swap the order around to fix this
    do_logicstep()
    for i in range(len(snake) - 1):
        do_drawstep()
        do_logicstep()
    do_drawstep()

# Draw progress bar at the end of each loop to try to tie the loops together
# TODO: Find a better way to loop the game instead of this, looks like shit
for i in range(10):
    setup_frame()
    for j in range(36//10 * (i+1) if i != 9 else 36):
        for k in range(5):
            slots[slot][frame][j+4][k+3] = True

render()