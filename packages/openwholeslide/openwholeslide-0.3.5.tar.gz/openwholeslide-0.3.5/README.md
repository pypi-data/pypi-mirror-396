# openwholeslide

Wrapper around tifffile library to have the same API as OpenSlide.

## Installation

```bash
$ pip install openwholeslide
```

## Usage

- Similarly to OpenSlide, the openwholeslide package allows to load a WSI as follows:
```
import openwholeslide as ows

wsi = ows.WholeSlide(path="/path/to/wsi")
```
- Regions can be extracted from this WholeSlide object. For example, a lower resolution of the full scale WSI can be extracted as follows:
```
region = wsi.read_full(magnification=1.0)
```
- This actually performs a lazy loading which does not load the data information. In order to get access to the region's pixels (as an numpy.ndarray), the following property should be called:
```
img = region.as_ndarray
```

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`openwholeslide` was created by Arthur Elskens and Adrien Foucart. It is licensed under the terms of the MIT license.
