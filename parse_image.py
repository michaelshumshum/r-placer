import numpy as np
from PIL import Image

_COLORS = [
    (('BE', '00', '39'), 1),  # dark red
    (('FF', '45', '00'), 2),  # red
    (('FF', 'A8', '00'), 3),  # orange
    (('FF', 'D6', '35'), 4),  # yellow
    (('00', 'A3', '68'), 6),  # dark green
    (('00', 'CC', '78'), 7),  # green
    (('7E', 'ED', '56'), 8),  # light green
    (('00', '75', '6F'), 9),  # dark teal
    (('00', '9E', 'AA'), 10),  # teal
    (('24', '50', 'A4'), 12),  # dark blue
    (('36', '90', 'EA'), 13),  # blue
    (('51', 'E9', 'F4'), 14),  # light blue
    (('49', '3A', 'C1'), 15),  # indigo
    (('6A', '5C', 'FF'), 16),  # periwinkle
    (('81', '1E', '9F'), 18),  # dark purple
    (('B4', '4A', 'C0'), 19),  # purple
    (('FF', '38', '81'), 22),  # pink
    (('FF', '99', 'AA'), 23),  # light pink
    (('6D', '48', '2F'), 24),  # dark brown
    (('9C', '69', '26'), 25),  # brown
    (('00', '00', '00'), 27),  # black
    (('89', '8D', '90'), 29),  # gray
    (('D4', 'D7', 'D9'), 30),  # light gray
    (('FF', 'FF', 'FF'), 31),  # white
]


def _closet_color_index(rgb):
    r, g, b = rgb[:3]
    distances = []
    for color, index in _COLORS:
        r1, g1, b1 = color
        distances.append((
            (((int(r1, 16) - r)**2) + ((int(g1, 16) - g)**2) + ((int(b1, 16) - b)**2))**0.5,
            index
        ))
    return sorted(distances)[0][1]


def get_image_size(image_dir):
    return np.array(Image.open(image_dir)).shape[0:2]


def parse_image(image_dir, image_location=None):  # x and y argument for location of the image on the canvas
    l = {}
    if not image_location:
        image_location = (0, 0)
    if isinstance(image_dir, str):
        pixel_array = np.array(Image.open(image_dir))
    else:
        pixel_array = np.array(image_dir)
    for iy, y in enumerate(pixel_array):
        for ix, x in enumerate(y):
            l[(ix + image_location[0], iy + image_location[1])] = _closet_color_index(x)
    return l
