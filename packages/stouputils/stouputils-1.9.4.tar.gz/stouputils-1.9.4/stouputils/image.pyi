import numpy as np
from .io import super_open as super_open
from .print import debug as debug, info as info
from PIL import Image
from collections.abc import Callable
from numpy.typing import NDArray
from typing import Any

def image_resize(image: Image.Image | NDArray[np.number], max_result_size: int, resampling: Image.Resampling | None = None, min_or_max: Callable[[int, int], int] = ..., return_type: type[Image.Image | NDArray[np.number]] | str = 'same', keep_aspect_ratio: bool = True) -> Any:
    ''' Resize an image while preserving its aspect ratio by default.
\tScales the image so that its largest dimension equals max_result_size.

\tArgs:
\t\timage             (Image.Image | np.ndarray): The image to resize.
\t\tmax_result_size   (int):                      Maximum size for the largest dimension.
\t\tresampling        (Image.Resampling | None):  PIL resampling filter to use (default: Image.Resampling.LANCZOS).
\t\tmin_or_max        (Callable):                 Function to use to get the minimum or maximum of the two ratios.
\t\treturn_type       (type | str):               Type of the return value (Image.Image, np.ndarray, or "same" to match input type).
\t\tkeep_aspect_ratio (bool):                     Whether to keep the aspect ratio.
\tReturns:
\t\tImage.Image | NDArray[np.number]: The resized image with preserved aspect ratio.
\tExamples:
\t\t>>> # Test with (height x width x channels) numpy array
\t\t>>> import numpy as np
\t\t>>> array = np.random.randint(0, 255, (100, 50, 3), dtype=np.uint8)
\t\t>>> image_resize(array, 100).shape
\t\t(100, 50, 3)
\t\t>>> image_resize(array, 100, min_or_max=max).shape
\t\t(100, 50, 3)
\t\t>>> image_resize(array, 100, min_or_max=min).shape
\t\t(200, 100, 3)

\t\t>>> # Test with PIL Image
\t\t>>> from PIL import Image
\t\t>>> pil_image: Image.Image = Image.new(\'RGB\', (200, 100))
\t\t>>> image_resize(pil_image, 50).size
\t\t(50, 25)
\t\t>>> # Test with different return types
\t\t>>> resized_array = image_resize(array, 50, return_type=np.ndarray)
\t\t>>> isinstance(resized_array, np.ndarray)
\t\tTrue
\t\t>>> resized_array.shape
\t\t(50, 25, 3)
\t\t>>> # Test with different resampling methods
\t\t>>> image_resize(pil_image, 50, resampling=Image.Resampling.NEAREST).size
\t\t(50, 25)
\t'''
def auto_crop(image: Image.Image | NDArray[np.number], mask: NDArray[np.bool_] | None = None, threshold: int | float | Callable[[NDArray[np.number]], int | float] | None = None, return_type: type[Image.Image | NDArray[np.number]] | str = 'same', contiguous: bool = True) -> Any:
    ''' Automatically crop an image to remove zero or uniform regions.

\tThis function crops the image to keep only the region where pixels are non-zero
\t(or above a threshold). It can work with a mask or directly analyze the image.

\tArgs:
\t\timage       (Image.Image | NDArray):\t  The image to crop.
\t\tmask        (NDArray[np.bool_] | None):   Optional binary mask indicating regions to keep.
\t\tthreshold   (int | float | Callable):     Threshold value or function (default: np.min).
\t\treturn_type (type | str):                 Type of the return value (Image.Image, NDArray[np.number], or "same" to match input type).
\t\tcontiguous  (bool):                       If True (default), crop to bounding box. If False, remove entire rows/columns with no content.
\tReturns:
\t\tImage.Image | NDArray[np.number]: The cropped image.

\tExamples:
\t\t>>> # Test with numpy array with zeros on edges
\t\t>>> import numpy as np
\t\t>>> array = np.zeros((100, 100, 3), dtype=np.uint8)
\t\t>>> array[20:80, 30:70] = 255  # White rectangle in center
\t\t>>> cropped = auto_crop(array, return_type=np.ndarray)
\t\t>>> cropped.shape
\t\t(60, 40, 3)

\t\t>>> # Test with custom mask
\t\t>>> mask = np.zeros((100, 100), dtype=bool)
\t\t>>> mask[10:90, 10:90] = True
\t\t>>> cropped_with_mask = auto_crop(array, mask=mask, return_type=np.ndarray)
\t\t>>> cropped_with_mask.shape
\t\t(80, 80, 3)

\t\t>>> # Test with PIL Image
\t\t>>> from PIL import Image
\t\t>>> pil_image = Image.new(\'RGB\', (100, 100), (0, 0, 0))
\t\t>>> from PIL import ImageDraw
\t\t>>> draw = ImageDraw.Draw(pil_image)
\t\t>>> draw.rectangle([25, 25, 75, 75], fill=(255, 255, 255))
\t\t>>> cropped_pil = auto_crop(pil_image)
\t\t>>> cropped_pil.size
\t\t(51, 51)

\t\t>>> # Test with threshold
\t\t>>> array_gray = np.ones((100, 100), dtype=np.uint8) * 10
\t\t>>> array_gray[20:80, 30:70] = 255
\t\t>>> cropped_threshold = auto_crop(array_gray, threshold=50, return_type=np.ndarray)
\t\t>>> cropped_threshold.shape
\t\t(60, 40)

\t\t>>> # Test with callable threshold (using lambda to avoid min value)
\t\t>>> array_gray2 = np.ones((100, 100), dtype=np.uint8) * 10
\t\t>>> array_gray2[20:80, 30:70] = 255
\t\t>>> cropped_max = auto_crop(array_gray2, threshold=lambda x: 50, return_type=np.ndarray)
\t\t>>> cropped_max.shape
\t\t(60, 40)

\t>>> # Test with non-contiguous crop
\t>>> array_sparse = np.zeros((100, 100, 3), dtype=np.uint8)
\t>>> array_sparse[10, 10] = 255
\t>>> array_sparse[50, 50] = 255
\t>>> array_sparse[90, 90] = 255
\t>>> cropped_contiguous = auto_crop(array_sparse, contiguous=True, return_type=np.ndarray)
\t>>> cropped_contiguous.shape  # Bounding box from (10,10) to (90,90)
\t(81, 81, 3)
\t>>> cropped_non_contiguous = auto_crop(array_sparse, contiguous=False, return_type=np.ndarray)
\t>>> cropped_non_contiguous.shape  # Only rows/cols 10, 50, 90
\t(3, 3, 3)

\t>>> # Test with 3D crop on depth dimension
\t>>> array_3d = np.zeros((50, 50, 10), dtype=np.uint8)
\t>>> array_3d[10:40, 10:40, 2:8] = 255  # Content only in depth slices 2-7
\t>>> cropped_3d = auto_crop(array_3d, contiguous=True, return_type=np.ndarray)
\t>>> cropped_3d.shape  # Should crop all 3 dimensions
\t(30, 30, 6)
\t'''
def numpy_to_gif(path: str, array: NDArray[np.integer | np.floating | np.bool_], duration: int = 100, loop: int = 0, mkdir: bool = True, **kwargs: Any) -> None:
    ''' Generate a \'.gif\' file from a numpy array for 3D visualization.

\tArgs:
\t\tpath     (str):     Path to the output .gif file.
\t\tarray    (NDArray): Numpy array to be dumped (must be 3D with depth as first axis, e.g. 64x1024x1024).
\t\tduration (int):     Duration between frames in milliseconds.
\t\tloop     (int):     Number of loops (0 = infinite).
\t\tmkdir    (bool):    Create the directory if it does not exist.
\t\t**kwargs (Any):     Additional keyword arguments for PIL.Image.save().

\tExamples:

\t\t.. code-block:: python

\t\t\t> array = np.random.randint(0, 256, (10, 100, 100), dtype=np.uint8)
\t\t\t> numpy_to_gif("output_10_frames_100x100.gif", array, duration=200, loop=0)

\t\t\t> total_duration = 1000  # 1 second
\t\t\t> numpy_to_gif("output_1s.gif", array, duration=total_duration // len(array))
\t'''
def numpy_to_obj(path: str, array: NDArray[np.integer | np.floating | np.bool_], threshold: float = 0.5, step_size: int = 1, pad_array: bool = True, verbose: int = 0) -> None:
    ''' Generate a \'.obj\' file from a numpy array for 3D visualization using marching cubes.

\tArgs:
\t\tpath      (str):     Path to the output .obj file.
\t\tarray     (NDArray): Numpy array to be dumped (must be 3D).
\t\tthreshold (float):   Threshold level for marching cubes (0.5 for binary data).
\t\tstep_size (int):     Step size for marching cubes (higher = simpler mesh, faster generation).
\t\tpad_array (bool):    If True, pad array with zeros to ensure closed volumes for border cells.
\t\tverbose   (int):     Verbosity level (0 = no output, 1 = some output, 2 = full output).

\tExamples:

\t\t.. code-block:: python

\t\t\t> array = np.random.rand(64, 64, 64) > 0.5  # Binary volume
\t\t\t> numpy_to_obj("output_mesh.obj", array, threshold=0.5, step_size=2, pad_array=True, verbose=1)

\t\t\t> array = my_3d_data  # Some 3D numpy array (e.g. human lung scan)
\t\t\t> numpy_to_obj("output_mesh.obj", array, threshold=0.3)
\t'''
