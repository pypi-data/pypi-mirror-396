import logging
import math
from typing import Any, Dict, List, Optional, Tuple
from xml.dom import minidom

import numpy as np
import tifffile
from PIL import Image
from skimage.transform import resize
from tifffile.tifffile import svs_description_metadata

from .vectors import FloatVector, IntVector

logger = logging.getLogger(__name__)

Image.MAX_IMAGE_PIXELS = None
_PREFERRED_UNTILED_DIMENSIONS = 1e7
_MAX_UNTILED_DIMENSIONS = 1e9


class Property:
    NDPI_MAGNIFICATION: str = "Magnification"
    SVS_MAGNIFICATION: str = "AppMag"
    RESOLUTION_UNIT: str = "ResolutionUnit"
    IMAGE_WIDTH: str = "ImageWidth"
    IMAGE_LENGTH: str = "ImageLength"
    X_RESOLUTION: str = "XResolution"
    Y_RESOLUTION: str = "YResolution"
    MPP: str = "MPP"


class ResolutionUnit:
    CENTIMETER: str = "CENTIMETER"
    MILLIMETER: str = "MILLIMETER"
    MICROMETER: str = "MICROMETER"
    INCH: str = "INCH"


class AssociatedImages:
    THUMBNAIL: str = "Thumbnail"
    MACRO: str = "Macro"
    LABEL: str = "Label"

    @classmethod
    def as_list(cls):
        return [cls.THUMBNAIL, cls.MACRO, cls.LABEL]


def standard_resolution_from_magnification(magnification: float) -> float:
    return 10 / magnification


def standard_magnification_from_resolution(resolution: float) -> float:
    expected_mag = 10 / resolution

    if int(expected_mag) == expected_mag:
        return expected_mag

    common_magnifications = (40.0, 20.0, 10.0, 5.0, 2.0, 1.0)
    nearest_idx = np.argmin(
        [abs(resolution - standard_resolution_from_magnification(mag)) for mag in common_magnifications]
    )
    nearest_common_magnification = common_magnifications[nearest_idx]

    return nearest_common_magnification


def get_dimensions_yx(dimensions: tuple[int, ...], axes: str = "YXS") -> IntVector:
    if axes == "YXS":
        return IntVector.from_yx(dimensions[:2])
    elif axes == "YX":
        return IntVector.from_yx(dimensions)
    elif axes == "CYX":
        return IntVector.from_yx(dimensions[1:])
    else:
        raise NotImplementedError(f"The supplied axes schema, {axes}, is not supported yet.")


class TiffWSI:
    """Reader class to handle pyramidal WSI format."""

    def __init__(self, path: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """TiffWSI constructor.

        :param path: The path to the WSI image.
        :type path: str
        :param metadata: The metadata that should be overwritten, defaults to None.
        :type metadata: Dict[str, Any], optional
        """

        self.path = path
        self.tiff_file = tifffile.TiffFile(path)
        if len(self.tiff_file.pages) == 0:
            self.tiff_file.close()
            raise IOError(f"WSI file at {path} cannot be opened as it contains no pages.")
        self.description = self.tiff_file.pages[0].description

        self.stains: Optional[list[str]] = (
            [
                i.attributes["Name"].value
                for i in minidom.parseString(self.tiff_file.pages[0].description).getElementsByTagName("Channel")
                if i.attributes.get("Name")
            ]
            if self.tiff_file.is_ome
            else None
        )

        self._properties = {}
        if self.tiff_file.is_ndpi:
            self.mag = self.tiff_file.pages[0].ndpi_tags.get(Property.NDPI_MAGNIFICATION, None)
            for key, val in self.tiff_file.pages[0].ndpi_tags.items():
                self._properties[key] = val
        elif self.tiff_file.is_svs or self.description.startswith("Aperio"):
            _metadata = svs_description_metadata(self.tiff_file.pages[0].description)
            self.mag = _metadata.get(Property.SVS_MAGNIFICATION, None)
            for key, val in _metadata.items():
                self._properties[key] = val
        else:
            self.mag = None

        for key, val in self.tiff_file.pages[0].tags.items():
            self._properties[key] = val.value

        # Get resolution scale and mpp
        unit_: tifffile.TiffTag = self.tiff_file.pages[0].tags.get(Property.RESOLUTION_UNIT, None)
        if unit_ is not None:
            unit = unit_.value.name
        else:
            unit = ResolutionUnit.CENTIMETER

        self.resolution_scale = 1e4  # default = CENTIMETER
        if unit.upper() == ResolutionUnit.MILLIMETER:
            self.resolution_scale = 1e3
        elif unit.upper() == ResolutionUnit.MICROMETER:
            self.resolution_scale = 1
        elif unit.upper() == ResolutionUnit.INCH:
            self.resolution_scale = 2.54 * 1e4

        self.mpp = FloatVector(x=1.0, y=1.0)
        if Property.X_RESOLUTION in self.tiff_file.pages[0].tags:
            d, n = self.tiff_file.pages[0].tags[Property.X_RESOLUTION].value
            self.mpp.x = self.resolution_scale * n / d
        elif Property.MPP in self._properties:
            self.mpp.x = self._properties[Property.MPP]
        if Property.Y_RESOLUTION in self.tiff_file.pages[0].tags:
            d, n = self.tiff_file.pages[0].tags[Property.Y_RESOLUTION].value
            self.mpp.y = self.resolution_scale * n / d
        elif Property.MPP in self._properties:
            self.mpp.y = self._properties[Property.MPP]

        self.axes = self.tiff_file.series[0].axes
        self.maxdimensions = get_dimensions_yx(self.tiff_file.series[0].levels[0].shape, self.axes)

        # Overwrite the properties provided with the metadata
        if metadata is None:
            metadata = {}
        for key, val in metadata.items():
            setattr(self, key, val)

        expected_magnification = (
            standard_magnification_from_resolution(min(self.mpp.x, self.mpp.y))
            if not metadata.get("mag", None)
            else self.mag
        )
        if self.mag:
            assert self.mag == expected_magnification, (
                f"The extracted magnification from the file metadata, {self.mag}, does not correspond to "
                "the expected closest common magnification derived from the extracted pixel resolution, "
                f"{expected_magnification}."
            )
        else:
            self.mag = expected_magnification

    @property
    def mpp_x(self) -> float:
        return self.mpp.x

    @property
    def mpp_y(self) -> float:
        return self.mpp.y

    @property
    def level_count(self):
        return len(self.tiff_file.series[0].levels)

    @property
    def dimensions(self):
        return self.maxdimensions.xy

    @property
    def level_downsamples(self) -> List[int]:
        level_downsamples = []
        for level in range(len(self.tiff_file.series[0].levels)):
            y, x = get_dimensions_yx(self.tiff_file.series[0].levels[level].shape, self.axes).yx
            dsx = self.maxdimensions.x / x
            dsy = self.maxdimensions.y / y
            # if dsx & dsy are different, it means we are not just at a downsample but at another acquisition
            # (e.g. the macro image)
            if not math.isclose(dsx, dsy, rel_tol=1e-2):
                break
            level_downsamples.append(dsy)
        return list(np.round(level_downsamples).astype("int"))

    @property
    def level_dimensions(self) -> List[Tuple[int, int]]:
        level_dimensions = []
        for level in range(len(self.tiff_file.series[0].levels)):
            y, x = get_dimensions_yx(self.tiff_file.series[0].levels[level].shape, self.axes).yx
            dsx = self.maxdimensions.x / x
            dsy = self.maxdimensions.y / y
            if not math.isclose(dsx, dsy, rel_tol=1e-2):
                break
            level_dimensions.append((x, y))
        return level_dimensions

    def read_region(
        self, loc: Tuple[int, int], level: int, dimensions: Tuple[int, int], stain: Optional[str] = None
    ) -> np.ndarray:
        """Openslide-like interface to read a region from a large TIFF without loading the whole image in-memory.

        Based on https://gist.github.com/rfezzani/b4b8852c5a48a901c1e94e09feb34743 by Riadh Fezzani.

        :param loc: Top-left of region in level-O px coordinates (x, y).
        :type loc: Tuple[int, int]
        :param level: Level of the pyramid to use.
        :type level: int
        :param dimensions: Size in level-coordinates (width, height).
        :type dimensions: Tuple[int, int]
        :param stain: The stain that should be loaded, if None this means the RGB mixed stains. It defaults to None.
        :type stain: Optional[str], optional
        :raises ValueError: Triggers when the provided level is bigger than the maximum available level.
        :return: The image
        :rtype: np.ndarray
        """

        if level >= len(self.level_dimensions):
            raise ValueError(f"Level not in pyramid. Maximum level = {len(self.level_dimensions) - 1}")

        if stain:
            return self._read_unmixed_region(loc=loc, level=level, dimensions=dimensions, stain=stain)

        return self._read_mixed_region(loc=loc, level=level, dimensions=dimensions)

    def _read_mixed_region(self, loc: Tuple[int, int], level: int, dimensions: Tuple[int, int]) -> np.ndarray:
        page = self.tiff_file.series[0].levels[level].pages[0]
        assert isinstance(page, tifffile.TiffPage)

        if len(page.shape) < 2:
            raise ValueError("Cannot access the mixed RGB version from an unmixed whole-slide image.")

        return self._read_region_from_page(loc=loc, page=page, frame=page, dimensions=dimensions)

    def _read_unmixed_region(
        self, loc: Tuple[int, int], level: int, dimensions: Tuple[int, int], stain: str
    ) -> np.ndarray:
        try:
            assert self.stains is not None, "No stains detected."
            stain_idx = self.stains.index(stain)
        except ValueError as e:
            raise ValueError(f"The stain '{stain}' is not recognized. Available stains are: {self.stains}.") from e

        page = self.tiff_file.series[0].levels[level].pages[0]
        assert isinstance(
            page, tifffile.TiffPage
        ), f"There seems to be an issue with the structure of the file as the first element is not a page, but a {type(page)}."

        # Handle the case where the channels are written in a single image
        if len(self.tiff_file.series[0].levels[level].pages) == 1:
            region = self._read_region_from_page(loc=loc, page=page, frame=page, dimensions=dimensions)
            return region[..., stain_idx]

        # Handle the case where the channels are written in separate images
        frame = self.tiff_file.series[0].levels[level].pages[stain_idx]
        assert frame is not None

        region = self._read_region_from_page(loc=loc, page=page, frame=frame, dimensions=dimensions)
        return region[..., 0] if len(region.shape) > 2 else region

    def _read_region_from_page(
        self,
        loc: Tuple[int, int],
        page: tifffile.TiffPage,
        frame: tifffile.TiffFrame | tifffile.TiffPage,
        dimensions: Tuple[int, int],
    ) -> np.ndarray:
        if not page.is_tiled or dimensions[0] * dimensions[1] < _PREFERRED_UNTILED_DIMENSIONS:
            # if not tiled or small: try to read everything at once...
            return self._read_region_untiled(page, frame, loc, dimensions)

        try:
            return self._read_region_tiled(page, frame, loc, dimensions)
        except RuntimeError as e:
            if dimensions[0] * dimensions[1] < _MAX_UNTILED_DIMENSIONS:
                logger.debug("Couldn't load tiled. Reverting to untiled.")
                return self._read_region_untiled(page, frame, loc, dimensions)
            else:
                logger.error("Couldn't load tiled and image too big. Failed to load.")
                raise e

    def _read_region_tiled(
        self,
        page: tifffile.TiffPage,
        frame: tifffile.TiffFrame | tifffile.TiffPage,
        loc: Tuple[int, int],
        dimensions: Tuple[int, int],
    ) -> np.ndarray:

        im_width = page.imagewidth
        im_height = page.imagelength

        startx = int(loc[0] * im_width / self.maxdimensions.x)
        starty = int(loc[1] * im_height / self.maxdimensions.y)
        w, h = dimensions
        endx = startx + w
        endy = starty + h

        if h < 1 or w < 1:
            raise ValueError("h and w must be strictly positive.")

        if endx > im_width:
            logger.info(
                "Dimensions out of the image bounds following the x-axis. The end of region has been set to the "
                "edge of the image."
            )
            endx = im_width
            w = endx - startx

        if endy > im_height:
            logger.info(
                "Dimensions out of the image bounds following the y-axis. The end of region has been set to the "
                "edge of the image."
            )
            endy = im_height
            h = endy - starty

        if startx < 0 or starty < 0:
            raise ValueError(
                f"Requested crop area (({startx},{starty}), ({startx + w}, {starty + h})) is out of image bounds."
            )

        tile_width, tile_height = page.tilewidth, page.tilelength

        start_tile_x = startx // tile_width
        start_tile_y = starty // tile_height
        end_tile_x = int(math.ceil(endx / tile_width))
        end_tile_y = int(math.ceil(endy / tile_height))

        tile_per_line = int(np.ceil(im_width / tile_width))

        out = np.empty(
            (
                page.imagedepth,
                (end_tile_y - start_tile_y) * tile_height,
                (end_tile_x - start_tile_x) * tile_width,
                page.samplesperpixel,
            ),
            dtype=page.dtype,
        )

        fh = page.parent.filehandle

        jpegtables = page.tags.get("JPEGTables", None)
        if jpegtables is not None:
            jpegtables = jpegtables.value

        for tile_y in range(start_tile_y, end_tile_y):
            for tile_x in range(start_tile_x, end_tile_x):
                index = int(tile_y * tile_per_line + tile_x)

                offset = frame.dataoffsets[index]
                bytecount = frame.databytecounts[index]

                fh.seek(offset)
                data = fh.read(bytecount)
                jpegheader = getattr(page, "jpegheader", None)
                if jpegheader is not None:
                    data = jpegheader + data
                tile, _, _ = frame.decode(data, index, jpegtables=jpegtables)

                im_x = (tile_x - start_tile_x) * tile_width
                im_y = (tile_y - start_tile_y) * tile_height
                out[:, im_y : im_y + tile_height, im_x : im_x + tile_width, :] = tile

        im_x0 = startx - start_tile_x * tile_width
        im_y0 = starty - start_tile_y * tile_height

        if page.imagedepth == 1:
            return out[0, im_y0 : im_y0 + h, im_x0 : im_x0 + w, :]
        return out[:, im_y0 : im_y0 + h, im_x0 : im_x0 + w, :]

    def _read_region_untiled(
        self,
        page: tifffile.TiffPage,
        frame: tifffile.TiffFrame | tifffile.TiffPage,
        loc: Tuple[int, int],
        dimensions: Tuple[int, int],
    ) -> np.ndarray:
        logger.debug("Untiled image - requires loading whole image")

        im_width = page.imagewidth
        im_height = page.imagelength

        startx = int(loc[0] * im_width / self.maxdimensions.x)
        starty = int(loc[1] * im_height / self.maxdimensions.y)
        w, h = dimensions
        endx = startx + w
        endy = starty + h

        if h < 1 or w < 1:
            raise ValueError("h and w must be strictly positive.")

        if startx < 0 or starty < 0 or endx > im_width or endy > im_height:
            raise ValueError(
                f"Requested crop area is out of image bounds.{startx}_{endx}_{im_height}, {starty}_{endy}_{im_width}"
            )

        return a[starty:endy, startx:endx, :] if len((a := frame.asarray()).shape) > 2 else a

    def get_best_level_for_downsample(self, downsample: float):
        for level, ds in enumerate(self.level_downsamples):
            if ds > downsample:
                return max(0, level - 1)
        return len(self.level_downsamples) - 1

    @property
    def properties(self) -> Dict:
        return self._properties

    @property
    def associated_images(self) -> Dict[str, np.ndarray]:
        _images = {}
        for serie in self.tiff_file.series:
            if serie.name in AssociatedImages.as_list():
                page = serie.pages[0]
                assert page is not None
                _images[serie.name] = page.asarray()
        return _images

    def get_thumbnail(self, size: Tuple[int, int]) -> Optional[np.ndarray]:
        _images = self.associated_images
        if AssociatedImages.THUMBNAIL in _images:
            im = _images[AssociatedImages.THUMBNAIL]
            ratio = 1
            if im.shape[0] > size[1]:
                ratio = size[1] / im.shape[0]
            if im.shape[1] > size[0]:
                ratio = min(ratio, size[0] / im.shape[1])
            if ratio != 1:
                newsize = (im.shape[0] * ratio, im.shape[1] * ratio)
                im = resize(im, newsize)
            return im

        # Use lowest available resolution if no thumbnail found
        page = self.tiff_file.series[0].levels[self.level_count - 1].pages[0]
        assert page is not None
        im = page.asarray()
        ratio = min(size[1] / im.shape[0], size[0] / im.shape[1])
        newsize = (im.shape[0] * ratio, im.shape[1] * ratio)
        return resize(im, newsize)

    def close(self):
        self.tiff_file.close()


class ImageWSI:
    """Reader class to handle non-pyramidal WSI format."""

    def __init__(self, path: str, metadata: Dict[str, Any]) -> None:
        """ImageWSI constructor.

        :param path: The path to the WSI image.
        :type path: str
        :param metadata: The metadata that complement this image. Should be provided: (i) the magnification
        level of the image (float) with the key ``mag`` and (ii) the pixel size in x and y directions (float)
        with the respective keys ``mpp_x`` and ``mpp_y``. The properties of the slide (Dict, optional) can
        also be provided with the key ``properties``, but it is not required.
        :type metadata: Dict[str, Any]
        """

        self.path = path

        self.maxdimensions = IntVector.from_xy(Image.open(path).size)

        self.mpp_x = metadata.get("mpp_x", 10)
        self.mpp_y = metadata.get("mpp_y", 10)
        self.mag = (
            mag
            if (mag := metadata.get("mag", None)) is not None
            else standard_magnification_from_resolution(min(self.mpp_x, self.mpp_y))
        )
        self.mpp = FloatVector(x=self.mpp_x, y=self.mpp_y)
        self.stains: Optional[list[str]] = metadata.get("stains", None)
        self._properties = metadata.get("properties", {})
        self.level_count = 1

    @property
    def dimensions(self) -> tuple[int, int]:
        return self.maxdimensions.xy

    @property
    def level_downsamples(self) -> List[int]:
        return [1]

    @property
    def level_dimensions(self) -> List[Tuple[int, int]]:
        return [self.maxdimensions.xy]

    @property
    def properties(self) -> Dict[str, Any]:
        return self._properties

    def read_region(
        self, loc: Tuple[int, int], level: int, dimensions: Tuple[int, int], stain: Optional[str] = None
    ) -> np.ndarray:
        """Openslide-like interface to read a region from a large TIFF without loading the whole image in-memory.

        :param loc: Top-left of region in level-O px coordinates (x, y).
        :type loc: Tuple[int, int]
        :param level: Level of the pyramid to use.
        :type level: int
        :param dimensions: Size in level-coordinates (width, height).
        :type dimensions: Tuple[int, int]
        :param stain: The stain that should be loaded, if None this means the RGB mixed stains. It defaults to None.
        :type stain: Optional[str], optional
        :raises ValueError: Triggers when the provided level is bigger than the maximum available level.
        :return: The image
        :rtype: np.ndarray
        """

        if stain is not None:
            raise NotImplementedError("Unmixing of RGB whole slide images is not yet supported.")

        if level >= len(self.level_dimensions):
            raise ValueError(f"Level not in pyramid. Maximum level = {len(self.level_dimensions)-1}")

        out = np.array(Image.open(self.path))

        w, h = dimensions

        return out[loc[1] : loc[1] + h, loc[0] : loc[0] + w, :]

    def get_best_level_for_downsample(self, downsample: float) -> int:
        for level, ds in enumerate(self.level_downsamples):
            if ds > downsample:
                return max(0, level - 1)
        return len(self.level_downsamples) - 1

    def close(self):
        pass
