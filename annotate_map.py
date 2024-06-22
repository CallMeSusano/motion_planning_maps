import yaml
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
from bfs_algorithm import bfs_algorithm

def load_yaml(yaml_path):
    with open(yaml_path, 'r') as file:
        data = yaml.safe_load(file)
    return data

def draw_cross(draw, center, color, size=10):
    x, y = center
    draw.line((x - size, y - size, x + size, y + size), fill=color, width=2)
    draw.line((x + size, y - size, x - size, y + size), fill=color, width=2)

def map_to_image_coords(map_coords, origin, resolution, image_height):
    mx, my = map_coords
    ox, oy, _ = origin
    ix = int((mx - ox) / resolution)
    iy = int((my - oy) / resolution)  # Adjusted for correct y-axis flipping
    return ix, iy

def image_to_map_coords(image_coords, origin, resolution, image_height):
    ix, iy = image_coords
    ox, oy, _ = origin
    mx = ix * resolution + ox
    my = iy * resolution + oy  # Adjusted for correct y-axis flipping
    return mx, my

def is_valid(row, column, map_image, negate, occupied_thresh, free_thresh):
    width, height = map_image.size
    if row < 0 or row >= height:
        return False
    if column < 0 or column >= width:
        return False
    pixel_value = map_image.getpixel((column, row))
    p = (255 - pixel_value) / 255.0 if not negate else pixel_value / 255.0
    return free_thresh <= p <= occupied_thresh

def on_click(event):
    x = event.x
    y = event.y
    map_x, map_y = image_to_map_coords((x / 10, y / 10), origin, resolution, image_height)

    if is_valid(int(x/10), int(y/10), map_image, negate, occupied_thresh, free_thresh - 0.1):
        print(f"Valid point: ({map_x}, {map_y})")
        print("origin: ", origin_image_coords)
        print("target: ", (int(x / 10), int(y / 10)))
        #bfs_algorithm((int(x / 10), int(y / 10)), (14,20), 'map.pgm', 'map.yaml')
    else:
        print(f"Invalid point: ({map_x}, {map_y})")

# Load map image and yaml file
map_image_path = 'map.pgm'
yaml_file_path = 'map.yaml'

map_data = load_yaml(yaml_file_path)
map_image = Image.open(map_image_path)
draw = ImageDraw.Draw(map_image)

# Extract necessary data from yaml
origin = map_data['origin']
resolution = map_data['resolution']
negate = map_data['negate']
occupied_thresh = map_data['occupied_thresh']
free_thresh = map_data['free_thresh']
image_width, image_height = map_image.size

# Convert map coordinates to image coordinates for visualization
origin_image_coords = map_to_image_coords((origin[0], origin[1]), origin, resolution, image_height)
if is_valid(origin_image_coords[0], origin_image_coords[1],map_image, negate, occupied_thresh, free_thresh - 0.1):
    print("ORIGIN IS VALID", origin_image_coords)
# Create the Tkinter window
root = tk.Tk()
root.title("Map Viewer")

# Convert the image to Tkinter-compatible format
map_image_zoomed = map_image.resize((image_width * 10, image_height * 10), Image.NEAREST)
tk_image = ImageTk.PhotoImage(map_image_zoomed)

# Create a canvas to display the image
canvas = tk.Canvas(root, width=map_image_zoomed.width, height=map_image_zoomed.height)
canvas.pack()

# Display the image on the canvas
canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)

# Bind the click event to the on_click function
canvas.bind("<Button-1>", on_click)

# Start the Tkinter event loop
root.mainloop()
