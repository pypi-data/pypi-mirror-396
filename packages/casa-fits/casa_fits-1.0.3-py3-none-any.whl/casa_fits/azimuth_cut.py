from math import degrees, radians
import numpy as np
from .Image import Image

def azimuth_cut(
        img: Image,
        radius: float,
        inclination: float,
        pa: float,
        beam_factor: float = 0.5,
        stokes: int = 0,
        chan: int = 0
) -> tuple:
    """
    Extract an azimuthal cut from an image using a deprojected elliptical annulus.

    This implementation computes the deprojected radius for each pixel,
    given the inclination and position angle, and selects pixels that lie
    within an annulus defined by [radius_px - beam_size/2, radius_px + beam_size/2].
    The azimuthal angle is computed in the deprojected frame.

    Args:
        img (Image): The Image object.
        radius (float): The radius in arcsec.
        inclination (float): The inclination angle in degrees.
        pa (float): The position angle in degrees.
        beam_factor (float, optional): Sampling size based on the beam size. Defaults to 0.5.
        stokes (int, optional): Stokes parameter index. Defaults to 0.
        chan (int, optional): Channel index. Defaults to 0.

    Returns:
        tuple: A tuple of three numpy arrays:
            - The azimuthal angle (in degrees) bins.
            - The mean intensity in each bin.
            - The standard deviation of the intensity in each bin.
    """
    # Calculate the center of the image
    # center_x = img.width // 2
    # center_y = img.height // 2

    # Calculate the beam size in pixel units (assuming beam and increments are defined)
    if not img.beam:
        raise ValueError("The image does not have a beam size.")
    img.convert_axes_unit('arcsec')
    if img.incr_x is None or img.incr_y is None:
        raise ValueError("Image increments are not defined.")
    beam_x = img.beam[0] / np.abs(img.incr_x)
    beam_y = img.beam[1] / np.abs(img.incr_y)
    beam_size = max(beam_x, beam_y)

    # Convert the input radius from arcsec to pixels.
    radius_px = radius / np.abs(img.incr_x)

    # Define the radial range (annulus width) in deprojected pixel units.
    r_min = radius_px - beam_size / 2
    r_max = radius_px + beam_size / 2

    # Sampling step in the azimuthal direction.
    sampling_rad = beam_size * beam_factor / radius_px
    sampling_deg = degrees(sampling_rad)
    line_azm = np.arange(0, 360, sampling_deg)
    sample = [[] for _ in range(len(line_azm))]

    # Convert inclination and PA to radians
    incl_rad = radians(inclination)
    pa_rad = radians(pa)

    # Loop over image pixels
    # For each pixel, compute its deprojected radius and azimuth angle.
    if img.data is None:
        raise ValueError("Image data is not loaded.")
    data = img.get_two_dim_data(stokes=stokes, chan=chan)
    if img.height is None or img.width is None:
        raise ValueError("Image dimensions are not defined.")
    if img.center_pix is None:
        img.center_pix = (img.width // 2, img.height // 2)
    for i in range(img.height):
        for j in range(img.width):
            dx = j - img.center_pix[0]
            dy = i - img.center_pix[1]

            # Rotate coordinates by PA to align with the disk's axes.
            xp = dx * np.cos(pa_rad) + dy * np.sin(pa_rad)
            yp = -dx * np.sin(pa_rad) + dy * np.cos(pa_rad)

            # Compute deprojected radius:
            # y'-coordinate is corrected by 1/cos(inclination)
            r_deproj = np.sqrt(xp**2 + (yp / np.cos(incl_rad))**2)

            # Select pixels within the annulus.
            if r_deproj < r_min or r_deproj > r_max:
                continue

            # Compute the deprojected azimuth angle (in degrees).
            # Note: np.arctan2(y, x) yields the angle in radians.
            theta_deproj = (np.degrees(np.arctan2(yp / np.cos(incl_rad), xp)) - 90) % 360

            # Find the closest azimuthal bin.
            idx = np.argmin(np.abs(line_azm - theta_deproj))
            sample[idx].append(data[i, j])

    # Compute mean and standard deviation in each azimuthal bin.
    line_mean = np.array([np.mean(s) if s else np.nan for s in sample])
    line_std = np.array([np.std(s) if s else np.nan for s in sample])

    return line_azm, line_mean, line_std