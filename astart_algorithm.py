import yaml
from PIL import Image, ImageDraw
import numpy as np
from heapq import heappop, heappush

def load_yaml(yaml_path):
    with open(yaml_path, 'r') as file:
        data = yaml.safe_load(file)
    return data

def map_to_image_coords(map_coords, origin, resolution, image_height):
    mx, my = map_coords
    ox, oy, _ = origin
    ix = int((mx - ox) / resolution)
    iy = image_height - int((my - oy) / resolution)  # Flip y-axis for image coordinates
    return ix, iy

def is_valid(row, column, map_image, negate, occupied_thresh, free_thresh):
    width, height = map_image.size
    if row < 0 or row >= height or column < 0 or column >= width:
        return False
    pixel_value = map_image.getpixel((column, row))
    p = (255 - pixel_value) / 255.0 if not negate else pixel_value / 255.0

    if p > occupied_thresh:
        return False  # Cell is occupied
    if p < free_thresh:
        return True   # Cell is free
    return False      # Cell is unknown

def heuristic(a, b):
    return np.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

# Load map image and yaml file
map_image_path = 'map.pgm'
yaml_file_path = 'map.yaml'

map_data = load_yaml(yaml_file_path)
map_image = Image.open(map_image_path)

# Extract necessary data from yaml
origin = map_data['origin']
resolution = map_data['resolution']
negate = map_data['negate']
occupied_thresh = map_data['occupied_thresh']
free_thresh = map_data['free_thresh']
image_width, image_height = map_image.size

# Convert origin to image coordinates
origin_coords = map_to_image_coords((0, 0), origin, resolution, image_height)

# Directions for moving up, down, left, right and diagonals
directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (-1, 1), (1, -1), (-1, -1)]

# Find the destination point (example coordinates)
destination_coords = (17, 15)

# Convert the destination to image coordinates
target_image_coords = map_to_image_coords(destination_coords, origin, resolution, image_height)

# A* algorithm implementation
def a_star_search(start, goal, map_image, directions, negate, occupied_thresh, free_thresh):
    open_set = []
    heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    
    while open_set:
        _, current = heappop(open_set)
        
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path
        
        for direction in directions:
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            if not is_valid(neighbor[0], neighbor[1], map_image, negate, occupied_thresh, free_thresh):
                continue
            tentative_g_score = g_score[current] + heuristic(current, neighbor)
            
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heappush(open_set, (f_score[neighbor], neighbor))
    
    raise ValueError("No path found")

# Run A* to find a path
try:
    path = a_star_search(origin_coords, destination_coords, map_image, directions, negate, occupied_thresh, free_thresh)
    print("Path found!")
except ValueError as e:
    print(e)

# Print the path
print("Path:")
for row, col in path:
    print(f"({row}, {col})")

# Mark the path on the distance matrix and draw it on the image
draw = ImageDraw.Draw(map_image)
for row, col in path:
    map_image.putpixel((col, row), 88)  # Marking the path in red

# Save the modified image
map_image.save('map_with_a_star_path.png')
print("Map image with A* path saved as 'map_with_a_star_path.png'")
