from ...installer import check_executable as check_executable
from ...io import clean_path as clean_path
from ...parallel import multithreading as multithreading
from ...print import colored_for_loop as colored_for_loop, debug as debug, info as info
from .config import Config as Config, WAIFU2X_NCNN_VULKAN_RELEASES as WAIFU2X_NCNN_VULKAN_RELEASES
from tempfile import TemporaryDirectory

def convert_frame(frame_path: str, delete_png: bool = True) -> None:
    ''' Convert a PNG frame to JPG format to take less space.

\tArgs:
\t\tframe_path  (str):   Path to the PNG frame to convert.
\t\tdelete_png  (bool):  Whether to delete the original PNG file after conversion.

\tReturns:
\t\tNone: This function doesn\'t return anything.

\tExample:
\t\t.. code-block:: python

\t\t\t> convert_frame("input.png", delete_png=True)
\t\t\t> # input.png will be converted to input.jpg and the original file will be deleted

\t\t\t> convert_frame("input.png", delete_png=False)
\t\t\t> # input.png will be converted to input.jpg and the original file will be kept
\t'''
def get_all_files(folder: str, suffix: str | tuple[str, ...] = '') -> list[str]:
    ''' Get all files paths in a folder, with a specific suffix if provided.

\tArgs:
\t\tfolder     (str):                    Path to the folder containing the files.
\t\tsuffix     (str | tuple[str, ...]):  Suffix of the files to get (e.g. ".png", ".jpg", etc.).

\tReturns:
\t\tlist[str]: List of all files paths in the folder.

\tExample:
\t\t>>> files: list[str] = get_all_files("some_folder", ".png")
\t\t>>> len(files)
\t\t0
\t'''
def create_temp_dir_for_not_upscaled(input_path: str, output_path: str) -> TemporaryDirectory[str] | None:
    """ Creates a temporary directory containing only images that haven't been upscaled yet.

    Args:
        input_path  (str):  Path to the folder containing input images.
        output_path (str):  Path to the folder where upscaled images are saved.

    Returns:
        TemporaryDirectory[str] | None: A temporary directory object if there are images to process,
                                        None if all images are already upscaled.
    """
def check_upscaler_executable() -> None: ...
def upscale(input_path: str, output_path: str, upscale_ratio: int) -> None:
    ''' Upscale an input image (or a directory of images) with the upscaler executable.

\tArgs:
\t\tinput_path     (str):  Path to the image to upscale (or a directory).
\t\toutput_path    (str):  Path to the output image (or a directory).
\t\tupscale_ratio  (int):  Upscaling ratio.

\tExample:
\t\t.. code-block:: python

\t\t\t> upscale("folder", "folder", 2)
\t\t\tTraceback (most recent call last):
\t\t\t\t...
\t\t\tAssertionError: Input and output paths cannot be the same, got \'folder\'

\t\t\t> upscale("stouputils", "stouputils/output.jpg", 2)
\t\t\tTraceback (most recent call last):
\t\t\t\t...
\t\t\tAssertionError: If input is a directory, output must be a directory too, got \'stouputils/output.jpg\'


\t\t\t> upscale("input.jpg", "output.jpg", 2)
\t\t\t> # The input.jpg will be upscaled to output.jpg with a ratio of 2

\t\t\t> upscale("input_folder", "output_folder", 2)
\t\t\t> # The input_folder will be upscaled to output_folder with a ratio of 2
\t'''
def upscale_images(images: list[str], output_folder: str, upscale_ratio: int, desc: str = 'Upscaling images') -> None:
    """ Upscale multiple images from a list.

\tArgs:
\t\timages        (list[str]): List of paths to the images to upscale.
\t\toutput_folder (str):       Path to the output folder where the upscaled images will be saved.
\t\tupscale_ratio (int):       Upscaling ratio.
\t\tdesc          (str):       Description of the function execution displayed in the progress bar.
\t\t\tNo progress bar will be displayed if desc is empty.

\tReturns:
\t\tNone: This function doesn't return anything.
\t"""
def upscale_folder(input_folder: str, output_folder: str, upscale_ratio: int, slightly_faster_mode: bool = True, desc: str = 'Upscaling folder') -> None:
    """ Upscale all images in a folder.

\tArgs:
\t\tinput_folder          (str):   Path to the input folder containing the images to upscale.
\t\toutput_folder         (str):   Path to the output folder where the upscaled images will be saved.
\t\tupscale_ratio         (int):   Upscaling ratio.
\t\tslightly_faster_mode  (bool):  Whether to use the slightly faster mode (no progress bar),
\t\t\tone call to the upscaler executable.
\t\tdesc                  (str):   Description of the function execution displayed in the progress bar.
\t\t\tNo progress bar will be displayed if desc is empty.

\tReturns:
\t\tNone: This function doesn't return anything.
\t"""
