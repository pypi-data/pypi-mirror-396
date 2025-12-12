from math import radians, cos, sin, ceil, sqrt
import numpy as np
from .Image import Image
from .utilities import downsample_data


def radial_cut(
    img: Image, azimuth: float, sample_size: int = 5, stokes: int = 0, chan: int = 0
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Radial line cut of the image along the specified azimuth angle from the center.

    Args:
        img (Image): The Image object.
        azimuth (float): The azimuth angle in degrees.
        sample_size (int, optional): The number of samples to take along the radial line. Defaults to 5.
        stokes (int, optional): Stokes parameter index. Defaults to 0.
        chan (int, optional): Channel index. Defaults to 0.

    Returns:
        tuple: A tuple of three numpy arrays:
            - The radial distance from the center.
            - The mean intensity.
            - The standard deviation of the intensity.
    """
    # Calculate the center of the image
    if img.width is None or img.height is None:
        raise ValueError("Image width or height is None.")
    center_x = img.width // 2
    center_y = img.height // 2

    # Calculate the beam size
    if img.beam is None:
        raise ValueError("The image does not have a beam size.")
    if img.incr_x is None or img.incr_y is None:
        raise ValueError("Image increment x or y is None.")
    img.convert_axes_unit("arcsec")
    beam_x = img.beam[0] / np.abs(img.incr_x)
    beam_y = img.beam[1] / np.abs(img.incr_y)

    # Determine the larger beam size (to define the sampling step and width)
    beam_size = max(beam_x, beam_y)
    # sampling_size = ceil(beam_size * beam_factor)

    # Convert azimuth angle to radians
    # azimuth is measured from the north
    azimuth_rad = radians(azimuth - 270)

    data: np.ndarray = img.get_two_dim_data(stokes=stokes, chan=chan)
    # data = downsample_data(data, sampling_size)

    # Initialize the line cut
    line_r = []
    line_mean = []
    line_std = []

    # Define the unit direction vector for the given azimuth
    direction_x = cos(azimuth_rad)
    direction_y = sin(azimuth_rad)

    # Loop over points along the line
    step = 0
    search_range = int(sqrt(sample_size**2 + sample_size**2) / 2 + 1)
    while True:
        # Calculate the current position
        x = int(center_x + step * direction_x)
        y = int(center_y + step * direction_y)
        rect_center = np.array([x, y])

        if x < 0 or x >= img.width or y < 0 or y >= img.height:
            break

        line_r.append(step * np.abs(img.incr_x))

        v_para = np.array([direction_x, direction_y]) * sample_size * 0.5
        v_perp = np.array([-direction_y, direction_x]) * beam_size * 0.5
        verts = [
            rect_center + v_para + v_perp,
            rect_center + v_para - v_perp,
            rect_center - v_para - v_perp,
            rect_center - v_para + v_perp,
        ]
        edges = [
            verts[1] - verts[0],
            verts[2] - verts[1],
            verts[3] - verts[2],
            verts[0] - verts[3],
        ]

        def cross(a, b):
            return a[0] * b[1] - a[1] * b[0]

        # Append the pixel value to the line
        sample = []
        # if step == 0: 0 else -search_range
        for i in range(-search_range, search_range + 1):
            for j in range(-search_range, search_range + 1):
                px = x + i
                py = y + j
                inside = True
                for k in range(4):
                    edge = edges[k]
                    vp = np.array([px, py]) - verts[k]
                    if cross(edge, vp) > 0:
                        inside = False
                        break
                if inside and 0 <= px < img.width and 0 <= py < img.height:
                    sample.append(data[py, px])

        if sample:
            line_mean.append(np.mean(sample))
            line_std.append(np.std(sample))
        else:
            line_mean.append(None)
            line_std.append(None)

        step += sample_size

    return np.array(line_r), np.array(line_mean), np.array(line_std)
