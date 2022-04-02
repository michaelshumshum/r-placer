import numpy as np
from PIL import Image

_COLORS = [
    (('ff', '45', '00'), 2),
    (('ff', 'a8', '00'), 3),
    (('ff', 'd6', '35'), 4),
    (('00', 'a3', '68'), 6),
    (('7e', 'ed', '56'), 8),
    (('24', '50', 'a4'), 12),
    (('36', '90', 'ea'), 13),
    (('51', 'e9', 'f4'), 14),
    (('81', '1e', '9f'), 25),
    (('b4', '4a', 'c0'), 27),
    (('ff', '99', 'aa'), 29),
    (('9c', '69', '26'), 30),
    (('00', '00', '00'), 31),
]


def _closet_color_index(rgb):
    r, g, b, a = rgb
    distances = []
    for color, index in _COLORS:
        r1, g1, b1 = color
        distances.append((
            ((int(r1, 16) - r)**2 + (int(g1, 16) - g)**2 + (int(b1, 16) - b)**2)**0.5,
            index
        ))
    return sorted(distances)[0][1]


def parse_image(image_dir, x, y):  # x and y argument for location of the image on the canvas
    l = []
    pixel_array = np.array(Image.open(image_dir))
    for iy, y in enumerate(np.array(Image.open(image_dir))):
        for ix, x in enumerate(y):
            l.append((ix + x, iy + y, _closet_color_index(x)))
    return l
