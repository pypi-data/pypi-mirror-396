import numpy as np
from .Image import Image


def imstat(
    image: Image,
    uncertainty: float,
    unit: str = "beam",
    mask: np.ndarray | None = None,
    inverse_mask: bool = False,
):
    """
    Alternative version of imstat.

    Args:
        image (Image): Image object.
        uncertainty (float): Flux uncertainty.
        unit (str, optional): Unit of area. Choices are 'beam' or 'arcsec'. Defaults to 'beam'.
        mask (np.ndarray, optional): If specified, statistics are calculated using only the data within the mask. Defaults to None.
        inverse_mask (bool, optional): If True, the specified mask region is inverted. Defaults to False.
    """
    data = image.data
    image.convert_axes_unit("arcsec")
    if unit == "beam":
        unit_area = 1
    elif unit == "arcsec":
        unit_area = np.pi * image.beam[0] * image.beam[1]
    else:
        raise ValueError("Arg `unit` must be `'beam'` or `'arcsec'`.")
    data /= unit_area
    ret = {}
    ret["unit"] = image.unit_data
    ret["restoring beam"] = {}
    ret["restoring beam"]["x"] = image.beam[0]
    ret["restoring beam"]["y"] = image.beam[1]
    ret["restoring beam"]["ang"] = image.beam[2]
    ret["all"] = {}
    ret["all"]["max"] = np.max(data)
    ret["all"]["max_sigma"] = ret["all"]["max"] * uncertainty
    ret["all"]["min"] = np.min(data)
    ret["all"]["sum"] = np.sum(data)
    ret["all"]["sumsq"] = np.sum(np.square(data))
    ret["all"]["mean"] = np.mean(data)
    ret["all"]["sigma"] = np.var(data, ddof=1)
    ret["all"]["rms"] = np.sqrt(ret["all"]["sumsq"] / data.size)
    # process mask
    if mask is not None:
        # Normalize the mask to True/False
        if mask.dtype != bool:
            mask = mask.astype(bool)
        if inverse_mask:
            mask = ~mask
        # Mask the data as np.nan
        data = np.where(mask, data, np.nan)
        # count the number of unmasked pixels
        num_unmasked = np.sum(mask)
        ret["masked"] = {}
        ret["masked"]["max"] = np.nanmax(data)
        ret["masked"]["min"] = np.nanmin(data)
        ret["masked"]["sum"] = np.nansum(data)
        ret["masked"]["sumsq"] = np.nansum(np.square(data))
        ret["masked"]["mean"] = np.nanmean(data)
        ret["masked"]["sigma"] = np.nanvar(data, ddof=1)
        ret["masked"]["rms"] = np.sqrt(ret["masked"]["sumsq"] / num_unmasked)
        ret["psnr"] = ret["all"]["max"] / ret["masked"]["rms"]
        ret["psnr_sigma"] = ret["all"]["max_sigma"] / ret["masked"]["rms"]
    return ret
