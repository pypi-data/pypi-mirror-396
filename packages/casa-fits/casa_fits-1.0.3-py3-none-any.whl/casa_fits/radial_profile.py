from math import sqrt, ceil, cos, radians, sin
import numpy as np
from .Image import Image
from .utilities import downsample_data

def radial_profile(
    img: Image,
    azimuth: tuple | None = None,
    sample_size: int = 5,
    inc: float = 0.0,         # inclination in degrees (0 = face-on)
    PA: float = 0.0,          # position angle in degrees (east of north)
    stokes: int = 0,         # Stokes parameter index
    chan: int = 0,           # Channel index
) -> tuple:
    """
    Extract a radial profile from an image.

    Args:
        img (Image): The Image object.
        azimuth (tuple): The azimuth range angle in degrees. If None, all azimuth angles are considered.
        sample_size (int, optional): The number of samples to take along the radial line. Defaults to 5.
        inc (float, optional): The inclination angle in degrees. Defaults to 0.0.
        PA (float, optional): The position angle in degrees. Defaults to 0.0.
        stokes (int, optional): Stokes parameter index. Defaults to 0.
        chan (int, optional): Channel index. Defaults to 0.

    Returns:
        tuple: A tuple of three numpy arrays:
            - The radial distance from the center.
            - The mean intensity.
            - The standard deviation of the intensity.
    """
    if img.width is None or img.height is None:
        raise ValueError("Image width or height is None.")
    # Calculate the center of the image
    center_x = img.width // 2
    center_y = img.height // 2
    
    if img.incr_x is None or img.incr_y is None:
        raise ValueError("Image increment x or y is None.")
    img.convert_axes_unit('arcsec')

    # Convert azimuth angle to radians
    # azimuth is measured from the north
    if azimuth is None:
        azimuth = (0, 359)
    azimuth = ((azimuth[0] + 90) % 360, (azimuth[1] + 90) % 360)

    def is_in_azimuth_range(angle, azimuth):
        if azimuth[0] < azimuth[1]:
            return azimuth[0] <= angle <= azimuth[1]
        else:
            return azimuth[0] <= angle or angle <= azimuth[1]

    # Initialize the line cut
    line_r = np.arange(0, min(center_x, center_y), sample_size, dtype=float)
    line_mean = []
    line_std = []
    sample = [[] for _ in range(len(line_r))]

    # Convert inclination and PA to radians
    inc_rad = radians(inc)
    PA_rad = radians(PA)

    # extract the 2D data
    # get the dimensions of the image
    data: np.ndarray = img.get_two_dim_data(stokes, chan)

    # Downsample the data
    data = downsample_data(data, sample_size)
    center_x_new = data.shape[1] // 2
    center_y_new = data.shape[0] // 2

    for i in range(len(data)):
        for j in range(len(data[0])):
            # Shift to new center
            dx = j - center_x_new
            dy = i - center_y_new

            # Rotate by -PA
            x_rot = dx * cos(-PA_rad) - dy * sin(-PA_rad)
            y_rot = dx * sin(-PA_rad) + dy * cos(-PA_rad)

            # Deproject y
            y_deproj = y_rot / cos(inc_rad)

            # Deprojected radius
            r = sqrt(x_rot**2 + y_deproj**2)

            rad = np.degrees(np.arctan2(y_deproj, x_rot) % (2 * np.pi))
            if is_in_azimuth_range(rad, azimuth):
                idx = int(r)
                if idx >= len(line_r):
                    continue
                sample[idx].append(data[i, j])

    for i, s in enumerate(sample):
        # print(f'Line {i}: {np.max(s)}')
        if not s:
            line_mean.append(0)
            line_std.append(0)
        else:
            line_mean.append(np.nanmean(s))
            line_std.append(np.nanstd(s))

    return np.array(line_r) * abs(img.incr_x), np.array(line_mean), np.array(line_std)
