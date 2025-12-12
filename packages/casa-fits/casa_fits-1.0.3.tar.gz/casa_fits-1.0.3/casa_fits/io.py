import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy import units as u
from .Image import Image


def load_fits(
    fits_file: str,
    width: int | None = None,
    height: int | None = None,
    center_radec: tuple[float, float] | None = None,
) -> Image:
    """
    Create an Image object from a FITS file.

    Args:
        fits_file (str): Path to the FITS file.
        width (int, optional): Width of the cropped image. If None, uses the full width.
        height (int, optional): Height of the cropped image. If None, uses the full height.
        center_radec (tuple[float, float], optional): Center coordinates in RA, Dec format. If None, uses the center of the image.

    Returns:
        Image: An Image object.
    """
    image = Image()

    # remove the extension from the filename
    image.imagename = fits_file.rsplit(".", 1)[0]
    # Load the FITS file and extract the data and header information
    try:
        with fits.open(fits_file) as hdul:
            image.data = np.array(hdul[0].data)  # type: ignore
            header = hdul[0].header  # type: ignore
            image.width = header.get("NAXIS1", image.data.shape[1])
            image.height = header.get("NAXIS2", image.data.shape[0])
            image.nchan = header.get("NAXIS3", 1)
            image.center_radec = (header.get("CRVAL1", 0.0), header.get("CRVAL2", 0.0))
            image.center_pix = (header.get("CRPIX1", image.width // 2) - 1, header.get("CRPIX2", image.height // 2) - 1)
            image.freq0 = header.get("CRVAL3", 0.0)
            image.incr_x = header.get("CDELT1", 0.0)
            image.incr_y = header.get("CDELT2", 0.0)
            image.incr_hz = header.get("CDELT3", 0.0)
            image.unit_x = header.get("CUNIT1", "deg")
            image.unit_y = header.get("CUNIT2", "deg")
            image.unit_data = header.get("BUNIT", "Jy/beam")
            beam_major = (
                header.get("BMAJ", 0.0) * 3600
            )  # Convert from degrees to arcseconds
            beam_minor = (
                header.get("BMIN", 0.0) * 3600
            )  # Convert from degrees to arcseconds
            beam_angle = header.get("BPA", 0.0)
            if beam_major and beam_minor:
                image.beam = (beam_major, beam_minor, beam_angle)
            else:
                image.beam = None

            # Cropping
            if center_radec is not None:
                wcs = WCS(header)
                center_coord = SkyCoord(
                    center_radec[0],
                    center_radec[1],
                    unit=(u.hourangle, u.deg),
                    frame="icrs",
                )
                image.center_pix = wcs.world_to_pixel(center_coord)
                # Debug
                # print(
                #     f"New center pixel coordinates: {image.center_pix[0]}, {image.center_pix[1]}"
                # )
            # new width and height
            if width is None:
                width = image.width
            if height is None:
                height = image.height
            # Calculate new left, right, top, bottom based on the new center
            # print(image.center_pix, width, height)
            left = int(round(image.center_pix[0] - width / 2))
            right = int(round(image.center_pix[0] + width / 2))
            bottom = int(round(image.center_pix[1] - height / 2))
            top = int(round(image.center_pix[1] + height / 2))
            # Ensure the new dimensions are within bounds
            if left < 0:
                right += left
                left = 0
            if right > image.width:
                left += right - image.width
                right = image.width
            if bottom < 0:
                top += bottom
                bottom = 0
            if top > image.height:
                bottom += top - image.height
                top = image.height
            # Debugging output
            # print(
            #     f"Cropping to: left={left}, right={right}, bottom={bottom}, top={top}"
            # )
            # Crop the data
            image.data = image.data[bottom:top, left:right]

            # For debugging purposes, print all attributes
            # print(f"Loaded FITS file '{fits_file}':")
            # print(f"  Width: {image.width}, Height: {image.height}, Channels: {image.nchan}")
            # print(f"  Center (RA, Dec): {image.center_radec}")
            # print(f"  Center (X, Y): {image.center_pix}")
            # print(f"  Freq0: {image.freq0}")
            # print(f"  Incr X: {image.incr_x}, Incr Y: {image.incr_y}, Incr Hz: {image.incr_hz}")
            # print(f"  Units: X={image.unit_x}, Y={image.unit_y}, Data={image.unit_data}")
            # if image.beam:
            #     print(f"  Beam: Major={image.beam[0]}, Minor={image.beam[1]}, Angle={image.beam[2]}")
            # else:
            #     print("  No beam information available.")
    except Exception as e:
        raise ValueError(f"Failed to open FITS file '{fits_file}': {e}")

    return image


def load_image(
    imagename: str,
    width: int = None,
    height: int = None,
    center_radec: tuple[float, float] = None,
) -> Image:
    """
    Create an Image object from a CASA image file.

    Args:
        imagename (str): Path to the CASA image file.
        width (int, optional): Width of the cropped image. If None, uses the full width.
        height (int, optional): Height of the cropped image. If None, uses the full height.
        center_radec (tuple[float, float], optional): Center coordinates in RA, Dec format. If None, uses the center of the image.

    Returns:
        Image: An Image object.
    """
    from casatasks import imhead
    from casatools import image as casa_image, measures

    image = Image()

    # info (imhead)
    image.imagename = imagename
    inform = imhead(imagename=imagename)
    if inform is None or not isinstance(inform, dict):
        raise ValueError(f'Failed to retrieve image inform from "{imagename}".')

    image.width = inform["shape"][0]
    image.height = inform["shape"][1]
    image.nchan = inform["shape"][3]

    if image.width is None or image.height is None:
        raise ValueError(f'Invalid image shape for "{imagename}".')

    image.x0 = inform["refval"][0]
    image.y0 = inform["refval"][1]
    image.freq0 = inform["refval"][3]

    image.incr_x = inform["incr"][0]
    image.incr_y = inform["incr"][1]
    image.incr_hz = inform["incr"][3]
    try:
        if inform["restoringbeam"]["positionangle"]["unit"] == "rad":
            pa = np.rad2deg(
                inform["restoringbeam"]["positionangle"]["value"]
            )
        else:
            pa = inform["restoringbeam"]["positionangle"]["value"]
        image.beam = (
            inform["restoringbeam"]["major"]["value"],
            inform["restoringbeam"]["minor"]["value"],
            pa,
        )
    except KeyError:
        image.beam = None
    image.unit_data = inform["unit"]
    image.unit_x = inform["axisunits"][0]
    image.unit_y = inform["axisunits"][1]

    # figure size
    if width is None or width <= 0 or width > image.width:
        width = image.width
    if (
        height is None
        or height <= 0
        or height > image.height
    ):
        height = image.height

    # Load data
    ia = casa_image()
    ia.open(imagename)
    if center_radec is not None:
        me = measures()
        center_coord = me.direction("J2000", v0=center_radec[0], v1=center_radec[1])
        pix_center = ia.topixel(
            [center_coord["m0"]["value"], center_coord["m1"]["value"]]
        )
        x_center, y_center = int(pix_center["numeric"][0]), int(
            pix_center["numeric"][1]
        )
    else:
        x_center, y_center = image.width // 2, image.height // 2
    image.center_pix = (x_center, y_center)
    blc_x, blc_y = x_center - width // 2, y_center - height // 2
    trc_x, trc_y = x_center + width // 2, y_center + height // 2
    d_blc_x, d_blc_y = -blc_x, -blc_y
    d_trc_x, d_trc_y = trc_x - image.width, trc_y - image.height
    if d_blc_x > 0:
        blc_x = 0
        trc_x -= d_blc_x
    if d_trc_x > 0:
        trc_x = image.width
        blc_x += d_trc_x
    if d_blc_y > 0:
        blc_y = 0
        trc_y -= d_blc_y
    if d_trc_y > 0:
        trc_y = image.height
        blc_y += d_trc_y
    blc = [blc_x, blc_y]
    trc = [trc_x, trc_y]
    image.height = trc_y - blc_y
    image.width = trc_x - blc_x
    rawdata = ia.getchunk(blc=blc, trc=trc)
    ia.close()

    # Need to reconsider the shape of image.img
    rawdata = rawdata.transpose(2, 3, 1, 0)
    image.data = rawdata

    # Convert RA/DEC units to arcsec
    image.convert_axes_unit("arcsec")

    return image