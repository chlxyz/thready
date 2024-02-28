import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
import imageio

def interpolate_line(p1, p2):
    x0, y0 = p1
    x1, y1 = p2
    coordinates = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        coordinates.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    return coordinates

def generate_string_art(image_path, num_pins, output_gif_path):
    gif_reader = imageio.get_reader(image_path)
    height, width, _ = gif_reader.get_data(0).shape
    edge_pins = generate_edge_pins(num_pins, height, width)
    tri = Delaunay(edge_pins)
    gif_writer = imageio.get_writer(output_gif_path, duration=gif_reader.get_meta_data()['duration'])
    for frame_number in range(gif_reader.get_length()):
        string_art = np.zeros((height, width), dtype=np.uint8)
        frame = gif_reader.get_data(frame_number)
        for simplex in tri.simplices:
            for i in range(3):
                p1, p2 = edge_pins[simplex[i]], edge_pins[simplex[(i + 1) % 3]]
                interpolated_line = interpolate_line(p1, p2)
                for coord in interpolated_line:
                    x, y = int(coord[0]), int(coord[1])
                    if 0 <= x < width and 0 <= y < height:
                        string_art[y, x] = frame[y, x, 0]
        _, string_art = cv2.threshold(string_art, 128, 255, cv2.THRESH_BINARY)
        string_art = cv2.equalizeHist(string_art)
        string_art = cv2.GaussianBlur(string_art, (5, 5), 0)
        gif_writer.append_data(string_art)
    gif_writer.close()

def generate_edge_pins(num_pins, height, width):
    top_edge = [(int(x), 0) for x in np.linspace(0, width - 1, num_pins)]
    bottom_edge = [(int(x), height - 1) for x in np.linspace(0, width - 1, num_pins)]
    left_edge = [(0, int(y)) for y in np.linspace(0, height - 1, num_pins)]
    right_edge = [(width - 1, int(y)) for y in np.linspace(0, height - 1, num_pins)]
    edge_pins = top_edge + bottom_edge + left_edge + right_edge
    return edge_pins

gif_path = 'input.gif'
output_gif_path = 'output.gif'
#adjust as ur own
num_pins = 100
generate_string_art(gif_path, num_pins, output_gif_path)