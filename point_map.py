import yaml
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
from bfs_algorithm import bfs_algorithm


def load_yaml(yaml_path):
    with open(yaml_path, 'r') as file:
        data = yaml.safe_load(file)
    return data

def map_to_image_coords(map_coords, origin, resolution, image_height):
    mx, my = map_coords
    ox, oy, _ = origin
    print(ox,oy)
    ix = int((ox) / resolution)
    iy = int((oy) / resolution)  # Adjusted for correct y-axis flipping
    print(ix,iy)
    ix = -ix
    iy = image_height + iy
    print(ix,iy, image_height)
    return ix, iy

def calculate_point_offset(origin, distance, resolution):
    dx, dy = distance
    ox, oy = origin
    print(dx, dy, ox, oy)
    ix = int(dx / resolution)
    iy = int(dy / resolution)
    print(ix, iy)
    ix = ox + ix
    iy = oy + iy
    print(ix, iy)
    return iy, ix

def is_valid(row, column, map_image, negate, occupied_thresh, free_thresh):
    width, height = map_image.size
    print(width, height)
    print(row, column)
    if row < 0 or row >= width or column < 0 or column >= height:
        print("not cool")
        return False
    pixel_value = map_image.getpixel((column, row))
    p = (255 - pixel_value) / 255.0 if not negate else pixel_value / 255.0

    if p > occupied_thresh:
        print("occupied")
        return False  # Cell is occupied
    if p < free_thresh:
        print("free")
        return True   # Cell is free
    print("occupied")
    return False      # Cell is unknown

def on_click(event):
    y = event.x
    x = event.y
    if is_valid(int(x/10), int(y/10), map_image, negate, occupied_thresh, free_thresh - 0.1):
        bfs_algorithm((int(x / 10), int(y / 10)), origin_image_coords, 'map.pgm', 'map.yaml', 0)

def point_image():
    # Load map image and yaml file
    map_image_path = 'map.pgm'
    yaml_file_path = 'map.yaml'
    map_image = Image.open(map_image_path)

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

    origin_image_coords = map_to_image_coords((0, 0), origin, resolution, image_height)
    print("origin: ", origin_image_coords)

    # Draw the path on the map image
    #draw = ImageDraw.Draw(map_image)
    #path_coordinates = origin_image_coords
    #draw.point(origin_image_coords, 88)

    # Save the modified image
    #map_image.save('maporigin.png')
    #print("Map image with path saved as 'maporigin.png'")

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

def go_home(distance, angle):
    # Load map image and yaml file
    map_image_path = '/home/miguel/maps.pgm'
    yaml_file_path = '/home/miguel/maps.yaml'
    map_image = Image.open(map_image_path)

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

    origin_image_coords = map_to_image_coords((0, 0), origin, resolution, image_height)
    print("origin: ", origin_image_coords)
    target_image_coords = calculate_point_offset(origin_image_coords, distance, resolution)
    print("target: ", target_image_coords)

    drawpoint = (target_image_coords[1], target_image_coords[0])
    print("drawpoint", drawpoint, target_image_coords)
    # Draw the path on the map image
    draw = ImageDraw.Draw(map_image)
    draw.point(origin_image_coords, 88)
    draw.point(target_image_coords, 200)

    # Save the modified image
    map_image.save('AAAAmaporigin.png')
    print("Map image with path saved as 'maporigin.png'")

    bfs_algorithm(target_image_coords, origin_image_coords, angle, map_data, map_image)