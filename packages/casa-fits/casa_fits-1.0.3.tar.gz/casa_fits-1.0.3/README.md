# CASA FITS

<a href='https://akimasanishida.github.io/casa_fits/' target="_blank"><img alt='GitHub' src='https://img.shields.io/badge/Documentation-100000?style=flat&logo=GitHub&logoColor=white&labelColor=333333&color=007ec6'/></a>

**CASA FITS** is a Python package for working with astronomical images in both FITS and CASA image formats. It provides tools for loading, analyzing, and visualizing astronomical images, with a focus on ease of use and integration with the scientific Python ecosystem.

## Features

- Support for FITS and CASA image formats
- Image loading and conversion utilities
- Visualization: matplotlib-based image display, beam drawing, contour overlays
- Image analysis tools: radial and azimuthal cuts, radial profiles, peak detection, statistics

## Installation

Requires Python 3.11-3.12.

Install via pip (after cloning the repository):

```bash
pip install casa-fits
```

## Usage

Import the package and display the image:

```python
from casa_fits import load_fits, load_image, imshow
import matplotlib.pyplot as plt

# Load a FITS image
img = load_fits("example.fits")
# Or CASA format image with specifying size
img = load_image("./example.image.pbcor", width=128, height=128)

# Display the image
fig, ax = plt.subplots(figsize=(6, 4))
# with title
imshow(ax, img, title="TWHya Continuum")
fig.tight_layout()
plt.show()
```

![example image of imshow](https://raw.githubusercontent.com/akimasanishida/casa_fits/refs/heads/main/sample/0_imshow.png)

See more samples at `sample` directory (more sample codes will come soon...).

## Modules Overview

- `io`: Functions for loading FITS and CASA images (`load_fits`, `load_image`).
- `imshow`, `overlay_contour`: Visualization utilities for displaying images and contours.
- `radial_profile`: Compute radial profiles of images.
- `radial_cut`, `azimuth_cut`: Extract radial and azimuthal cuts from images.
- `detectpeak`: Peak detection in images.
- `imstat`: Compute image statistics.

## Documentation

Full documentation is available at [https://akimasanishida.github.io/casa_fits/](https://akimasanishida.github.io/casa_fits/).

## License

MIT License

## Repository

[https://github.com/akimasanishida/casa_fits](https://github.com/akimasanishida/casa_fits)
