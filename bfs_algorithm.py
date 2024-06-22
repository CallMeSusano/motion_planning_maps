import csv
import math
import yaml
from PIL import Image, ImageDraw
import numpy as np
from collections import deque
import requests
import subprocess

def load_yaml(yaml_path):
    with open(yaml_path, 'r') as file:
        data = yaml.safe_load(file)
    return data

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

def calculate_angle(from_direction, to_direction):
    angle = math.degrees(math.atan2(to_direction[1], to_direction[0]) - math.atan2(from_direction[1], from_direction[0]))
    if angle > 180:
        angle -= 360
    elif angle < -180:
        angle += 360
    return angle

def bfs_algorithm(target, map_origin, initial_angle, map_data, map_image):
    # Extract necessary data from yaml
    origin = map_data['origin']
    resolution = map_data['resolution']
    negate = map_data['negate']
    occupied_thresh = map_data['occupied_thresh']
    free_thresh = map_data['free_thresh']
    image_width, image_height = map_image.size

    # Create the matrix and BFS queue
    distance_matrix = np.full((image_height, image_width), -1, dtype=int)  # Initialize with -1 for unvisited cells
    queue = deque()

    # Initialize BFS
    queue.append((map_origin[1], map_origin[0]))  # Add origin to the queue
    distance_matrix[map_origin[1], map_origin[0]] = 0  # Distance to origin is 0

    # Directions for moving up, down, left, right and diagonals
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (-1, 1), (1, -1), (-1, -1)]

    # Perform BFS
    while queue:
        current_row, current_col = queue.popleft()
        current_distance = distance_matrix[current_row, current_col]

        for direction in directions:
            new_row, new_col = current_row + direction[0], current_col + direction[1]

            if (0 <= new_row < image_height and 0 <= new_col < image_width and 
                distance_matrix[new_row, new_col] == -1 and 
                is_valid(new_row, new_col, map_image, negate, occupied_thresh, free_thresh - 0.1)):
                
                queue.append((new_row, new_col))
                distance_matrix[new_row, new_col] = current_distance + 1

    # Find the destination point (example coordinates)
    destination_coords = target

    # Ensure the destination coordinates are within the bounds
    if destination_coords[1] < 0 or destination_coords[1] >= image_height or destination_coords[0] < 0 or destination_coords[0] >= image_width:
        raise ValueError("Destination coordinates are out of bounds")

    # Backtrack from the destination to the origin to find the path
    path = []
    directions_taken = []
    current_row, current_col = destination_coords

    while distance_matrix[current_row, current_col] != 0:
        path.append((current_row, current_col))
        found_next_step = False
        for direction in directions:
            new_row, new_col = current_row + direction[0], current_col + direction[1]
            if (0 <= new_row < image_height and 0 <= new_col < image_width and
                    distance_matrix[new_row, new_col] == distance_matrix[current_row, current_col] - 1):
                directions_taken.append(direction)
                current_row, current_col = new_row, new_col
                found_next_step = True
                break
        if not found_next_step:
            raise ValueError("Pathfinding failed; no valid path found.")

    path.append((map_origin[1], map_origin[0]))  # Add the origin to the path
    directions_taken.reverse()
    path.reverse()

    # Process directions to identify movement and rotation
    final_path = []
    if directions_taken:
        current_direction = directions_taken[0]
        count = 1
        for direction in directions_taken[1:]:
            if direction == current_direction:
                count += 1
            else:
                final_path.append((current_direction, count))
                current_direction = direction
                count = 1
        final_path.append((current_direction, count))

    # Create CSV data
    csv_data = []

    # Calculate the initial rotation to 0 degrees
    if initial_angle != 0:
        angle_to_zero = -initial_angle - 90  # Rotate by the negative of the initial angle to get to 0 degrees
        response = requests.post("http://127.0.0.1:5000/predictAngleTf", json={'Angle': angle_to_zero, 'Velocity': 0.5})
        direction = "Left" if angle_to_zero > 0 else "Right"
        csv_data.append(["rotation", response.json().get('predicted_time'), direction])

    # Starting direction after rotation to 0 degrees
    start_direction = (1, 0)  # 0 degrees corresponds to the (1, 0) vector

    for direction, steps in final_path:
        # Calculate rotation angle if there's a change in direction
        angle = calculate_angle(start_direction, direction)
        if angle != 0:
            # Predict angle time
            response = requests.post("http://127.0.0.1:5000/predictAngleTf", json={'Angle': angle, 'Velocity': 0.5})

            # Print the JSON response
            if angle < 0:
                csv_data.append(["rotation", response.json().get('predicted_time'), "Right"])
            else:
                csv_data.append(["rotation", response.json().get('predicted_time'), "Left"])

            start_direction = direction
        # Add forward movement & predict distance time        
        response = requests.post("http://127.0.0.1:5000/predictLinearTf", json={'Distance': steps * resolution, 'Velocity': 0.1})

        csv_data.append(["forward", response.json().get('predicted_time'), "NULL"])  # Distance in meters

    # Write to CSV
    csv_file_path = 'path_instructions.csv'
    with open(csv_file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["type", "time", "direction"])
        csv_writer.writerows(csv_data)

    # Mark the path on the distance matrix
    for row, col in path:
        distance_matrix[row, col] = 69

    # Draw the path on the map image
    draw = ImageDraw.Draw(map_image)
    path_coordinates = [(col, row) for row, col in path]
    draw.line(path_coordinates, fill=55, width=1)

    # Save the modified image
    map_image.save('map_with_path.png')
    print("Map image with path saved as 'map_with_path.png'")
    print(f"CSV with path instructions saved as '{csv_file_path}'")

    map_save_command = 'ros2 run motion_plan Motion'
    subprocess.run(map_save_command, shell=True)
