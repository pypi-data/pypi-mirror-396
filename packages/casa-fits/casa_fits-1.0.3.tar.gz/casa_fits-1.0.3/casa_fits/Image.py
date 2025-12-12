import numpy as np
from .utilities import unitConvDict


class Image:
    def __init__(self):
        self.imagename: str | None = None
        self.data: np.ndarray | None = None
        self.width: int | None = None
        self.height: int | None = None
        self.nchan: int | None = None
        self.center_radec: tuple[float, float] | None = None  # (RA, Dec)
        self.center_pix: tuple[float, float] | None = None  # (X, Y)
        self.freq0: float | None = None
        self.incr_x: float | None = None
        self.incr_y: float | None = None
        self.incr_hz: float | None = None
        self.unit_x: str | None = None
        self.unit_y: str | None = None
        self.unit_data: str | None = None
        self.beam: tuple[float, float, float] | None = None  # (major, minor, angle)

    def convert_axes_unit(self, unit: str):
        """
        Convert the axes units of the image to the specified unit.

        Args:
            unit (str): The unit to convert to (e.g., 'arcsec').
        """
        try:
            if self.unit_x is not None:
                self.incr_x *= unitConvDict[(self.unit_x, unit)]
            else:
                raise ValueError("Unit of x-axis is None.")
        except KeyError:
            raise ValueError(
                f"Unsupported unit conversion from {self.unit_x} to {unit}."
            )
        try:
            if self.unit_y is not None:
                self.incr_y *= unitConvDict[(self.unit_y, unit)]
            else:
                raise ValueError("Unit of y-axis is None.")
        except KeyError:
            raise ValueError(
                f"Unsupported unit conversion from {self.unit_y} to {unit}."
            )
        self.unit_x = unit
        self.unit_y = unit

    def get_ticks(
        self, xtickspan: int, ytickspan: int, relative: bool, fmt: str, width: int | None = None, height: int | None = None
    ) -> tuple[list[float], list[str], list[float], list[str]]:
        """
        Returns x and y ticks and tick labels.

        Args:
            xtickspan (int): Span of ticks of x-axis.
            ytickspan (int): Span of ticks of y-axis.
            relative (bool): If True, ticks are relative coordinates. If False, ticks are global coordinates (NOT IMPLEMENTED YET!).
            fmt (str): Format of tick labels.
            width (int | None): Width of the image. If None, use the width of the image.
            height (int | None): Height of the image. If None, use the height of the image.

        Returns:
            xticks, xticks_label, yticks, yticks_label
        """
        _fmt = "{" + fmt + "}"
        if self.width is None or self.height is None:
            raise ValueError("Image width and height is None.")
        if self.incr_x is None or self.incr_y is None:
            raise ValueError("Image increment x and y is None.")
        if width is None:
            width = self.width
        if height is None:
            height = self.height
        xini = (self.width - width) / 2
        yini = (self.height - height) / 2
        xmid = self.width / 2
        ymid = self.height / 2
        xfin = (self.width + width) / 2
        yfin = (self.height + height) / 2
        xlini = -width / 2 * self.incr_x
        ylini = -height / 2 * self.incr_y
        xlmid = 0
        ylmid = 0
        xlfin = width / 2 * self.incr_x
        ylfin = height / 2 * self.incr_y
        if relative:
            xticks_label_num: list[float] = [xlini, 0.0]
            yticks_label_num: list[float] = [ylini, 0.0]
        else:
            raise NotImplementedError(
                "Global coordinates are not implemented yet. Use relative coordinates."
            )
        xticks = [xini, xmid]
        yticks = [yini, ymid]
        for i in range(1, xtickspan + 1):
            xticks.append((xmid - xini) * i / (xtickspan + 1) + xini)
            xticks_label_num.append((xlmid - xlini) * i / (xtickspan + 1) + xlini)
            xticks.append((xmid - xfin) * i / (xtickspan + 1) + xfin)
            xticks_label_num.append((xlmid - xlfin) * i / (xtickspan + 1) + xlfin)
        for i in range(1, ytickspan + 1):
            yticks.append((ymid - yini) * i / (ytickspan + 1) + yini)
            yticks_label_num.append((ylmid - ylini) * i / (ytickspan + 1) + ylini)
            yticks.append((ymid - yfin) * i / (ytickspan + 1) + yfin)
            yticks_label_num.append((ylmid - ylfin) * i / (ytickspan + 1) + ylfin)
        xticks_label: list[str] = [""] * len(xticks)
        yticks_label: list[str] = [""] * len(yticks)
        for i, s in enumerate(xticks_label_num):
            xticks_label[i] = _fmt.format(s)
        for i, s in enumerate(yticks_label_num):
            yticks_label[i] = _fmt.format(s)
        return xticks, xticks_label, yticks, yticks_label

    def get_two_dim_data(self, stokes: int = 0, chan: int = 0) -> np.ndarray:
        """
        Extracts the 2D data based on the specified Stokes and channel indices.

        Args:
            stokes (int, optional): Stokes parameter index. Defaults to 0.
            chan (int, optional): Channel index. Defaults to 0.

        Returns:
            np.ndarray: The extracted 2D data.
        """
        if self.data is None:
            raise ValueError("Image data is None.")
        if stokes < 0 or stokes >= self.data.shape[0]:
            raise IndexError(
                f"Stokes index {stokes} is out of bounds for the image data."
            )
        if chan < 0 or chan >= self.data.shape[1]:
            raise IndexError(
                f"Channel index {chan} is out of bounds for the image data."
            )

        if self.data.ndim == 4:
            return self.data[stokes, chan]
        elif self.data.ndim == 3:
            return self.data[chan]
        elif self.data.ndim == 2:
            return self.data
        else:
            raise ValueError("Unsupported image data dimensions.")

    def keep_stokes_chan(self, stokes: int, chan: int):
        """
        Keep only specific stokes and channel from the image data.
        This is useful for the image that has only one stokes and channel.

        Args:
            stokes (int): The Stokes parameter to keep.
            chan (int): The channel to keep.
        """
        if self.data is None:
            raise ValueError("Image data is None.")
        # Check if the data has four dimensions (Stokes, Channel, Y, X)
        if not self.data.ndim == 4:
            raise ValueError(
                f"Data must be 4D (Stokes, Channel, Y, X), but got {self.data.ndim}D."
            )
        # Check if the specified stokes and channel are valid
        if stokes < 0 or chan < 0:
            raise ValueError("Stokes and channel indices must be non-negative.")
        if stokes >= self.data.shape[0]:
            raise ValueError(
                f"Stokes index {stokes} is out of bounds for data with shape {self.data.shape}."
            )
        if chan >= self.data.shape[1]:
            raise ValueError(
                f"Channel index {chan} is out of bounds for data with shape {self.data.shape}."
            )
        if self.data.ndim == 4:
            self.data = self.data[stokes, chan]
        elif self.data.ndim == 3:
            self.data = self.data[chan]
        else:
            raise ValueError(
                f"Unsupported data dimension: {self.data.ndim}. Expected 3D or 4D data."
            )