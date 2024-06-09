import yaml
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk

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
    iy = image_height - int((my - oy) / resolution)  # Flip y-axis for image coordinates
    return ix, iy

def is_valid(row, column, map_image, negate, occupied_thresh, free_thresh):
    width, height = map_image.size
    if row < 0 or row >= height:
        return False
    if column < 0 or column >= width:
        return False
    pixel_value = map_image.getpixel((column, row))
    p = (255 - pixel_value) / 255.0 if not negate else pixel_value / 255.0
    print("pixel value", p)

    if p > occupied_thresh:
        return False  # Cell is occupied
    if p < free_thresh:
        return True   # Cell is free
    return False      # Cell is unknown

def on_click(event):
    x = event.x
    y = event.y
    print(f"Clicked at image coordinates: ({x / 10}, {y / 10})")
    if is_valid(y / 10, x / 10, map_image, negate, occupied_thresh, free_thresh - 0.1):
        print(f"The point ({x}, {y}) is valid.")
    else:
        print(f"The point ({x}, {y}) is not valid.", occupied_thresh, free_thresh)

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

# Define the locations to mark
origin_coords = (0, 0)  # Coordinates to mark with red cross
target_coords = (0, 0)  # Coordinates to mark with blue cross

# Convert map coordinates to image coordinates
origin_image_coords = map_to_image_coords(origin_coords, origin, resolution, image_height)
target_image_coords = map_to_image_coords(target_coords, origin, resolution, image_height)

# Create the Tkinter window
root = tk.Tk()
root.title("Map Viewer")

# Convert the image to Tkinter-compatible format
map_image_zoomed = map_image.resize((image_width * 10, image_height * 10), Image.NEAREST)  # Zoom the image by 4x
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
