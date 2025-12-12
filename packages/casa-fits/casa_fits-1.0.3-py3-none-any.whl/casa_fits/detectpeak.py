import numpy as np
from .Image import Image


def detectpeak(
    img: Image, rms: float, threshold_rms: int = 5, find_max: bool = True
) -> list[tuple[int, int, float]]:
    """
    Detects peaks in an image.

    Args:
        img (Image): The image object.
        rms (float): The RMS noise level for peak detection. Only pixels with intensity greater than threshold_rms * rms will be considered.
        threshold_rms (int): The threshold in terms of RMS to consider a pixel as a peak. Default is 5.
        find_max (bool): If True, the function will find the maximum peaks. Otherwise, it will find the minimum peaks.

    Returns:
        list[tuple[int, int, float]]: The list of detected peaks. Each peak is represented as a tuple (x, y, value).
    """
    # beam and search cell size
    img.convert_axes_unit("arcsec")
    if img.beam is None:
        raise ValueError("The image does not have a beam size.")
    if img.incr_x is None or img.incr_y is None:
        raise ValueError("Image increment x or y is None.")
    beam_x = img.beam[0] / abs(img.incr_x)
    beam_y = img.beam[1] / abs(img.incr_y)
    beam_ang = (90 + img.beam[2]) * np.pi / 180
    cell_width = int(
        np.sqrt((beam_x * np.cos(beam_ang)) ** 2 + (beam_x * np.sin(beam_ang)) ** 2) + 1
    )
    cell_height = int(
        np.sqrt((beam_x * np.sin(beam_ang)) ** 2 + (beam_y * np.cos(beam_ang)) ** 2) + 1
    )

    # detect peaks
    peak: list[tuple[int, int, float]] = []

    if img.height is None or img.width is None:
        raise ValueError("Image height or width is None.")
    if img.data is None:
        raise ValueError("Image data is None.")

    threshold = threshold_rms * rms
    data = img.get_two_dim_data()

    for i in range(cell_height // 2, img.height - cell_height // 2, 1):
        for j in range(cell_width // 2, img.width - cell_width // 2, 1):
            if data[i][j] > threshold:
                region = data[
                    i - cell_height // 2 : i + cell_height // 2 + 1,
                    j - cell_width // 2 : j + cell_width // 2 + 1,
                ]
                if find_max:
                    if data[i][j] == np.max(region):
                        peak.append((j, i, data[i][j]))
                else:
                    if data[i][j] == np.min(region):
                        peak.append((j, i, data[i][j]))

    return peak
