import math
import os
import numpy as np

unitConvDict = {
    ('rad', 'rad'): 1,
    ('arcsec', 'arcsec'): 1,
    ('deg', 'deg'): 1,
    ('rad', 'arcsec'): (3600 * 180) / math.pi,
    ('arcsec', 'rad'): math.pi / (3600 * 180),
    ('deg', 'arcsec'): 3600,
    ('arcsec', 'deg'): 1 / 3600,
}

unitDict = {
    'rad': '',
    'arcsec': '"',
    'deg': '°',
}

siPrefixDict = {
    'peta': { 'symbol': 'P', 'base10': 1e-15 },
    'tera': { 'symbol': 'T', 'base10': 1e-12 },
    'giga': { 'symbol': 'G', 'base10': 1e-9 },
    'mega': { 'symbol': 'M', 'base10': 1e-6 },
    'kilo': { 'symbol': 'k', 'base10': 1e-3 },
    'hecto': { 'symbol': 'h', 'base10': 1e-2 },
    'deca': { 'symbol': 'da', 'base10': 1e-1 },
    'None': { 'symbol': '', 'base10': 1 },
    'deci': { 'symbol': 'd', 'base10': 1e1 },
    'centi': { 'symbol': 'c', 'base10': 1e2 },
    'milli': { 'symbol': 'm', 'base10': 1e3 },
    'micro': { 'symbol': 'μ', 'symbol_alt': 'u', 'base10': 1e6 },
    'nano': { 'symbol': 'n', 'base10': 1e9 },
    'pico': { 'symbol': 'p', 'base10': 1e12 },
}

def get_si_prefix_symbol(prefix: str) -> str:
    """
    Returns the SI prefix symbol for a given prefix string.

    Args:
        prefix (str): The SI prefix string.

    Returns:
        str: The symbol associated with the given prefix.
    """
    try :
        return siPrefixDict[prefix]['symbol']
    except KeyError:
        return siPrefixDict['None']['symbol']

def get_si_prefix_base10(prefix: str) -> float:
    """
    Returns the base 10 multiplier for a given SI prefix string.

    Args:
        prefix (str): The SI prefix string.

    Returns:
        float: The base 10 multiplier associated with the given prefix.
    """
    try :
        return siPrefixDict[prefix]['base10']
    except KeyError:
        return siPrefixDict['None']['base10']

def get_pret_dir_name(dir: str) -> str:
    """
    Returns the last component of a directory path without trailing slashes.

    Args:
        dir (str): The directory path.

    Returns:
        str: The last component of the directory path.
    """
    return os.path.split(dir.rstrip('/'))[1]

def downsample_data(data: np.ndarray, sample_size: int) -> np.ndarray:
    """
    Downsamples a 2D numpy array by averaging over blocks of size sample_size.

    Args:
        data (np.ndarray): The 2D numpy array to downsample.
        sample_size (int): The size of the blocks to average over.

    Returns:
        np.ndarray: The downsampled 2D numpy array.
    """
    if data.ndim != 2:
        raise ValueError("Input data must be a 2D numpy array.")
    if sample_size <= 0:
        raise ValueError("Sample size must be a positive integer.")
    
    height, width = data.shape
    
    # Crop the data to make sure dimensions are divisible by sample_size
    width_crop = width - (width % sample_size)
    height_crop = height - (height % sample_size)

    # Crop the data with keeping the center
    x_start = (width - width_crop) // 2
    y_start = (height - height_crop) // 2
    data = data[y_start:y_start + height_crop, x_start:x_start + width_crop]

    # New width and height
    width_new = width_crop // sample_size
    height_new = height_crop // sample_size

    return data.reshape(height_new, sample_size, width_new, sample_size).mean(axis=(1, 3))