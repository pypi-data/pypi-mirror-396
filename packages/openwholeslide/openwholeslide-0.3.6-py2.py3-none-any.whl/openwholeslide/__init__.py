# read version from installed package
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("openwholeslide")
except PackageNotFoundError:
    __version__ = "dev"


from ._slide import ImageWSI, TiffWSI
from .vectors import FloatVector, IntVector, VectorType
from .wsi import PaddingParameters, Reader, SlideRegion, SlideStack, WholeSlide
