from ...installer import check_executable as check_executable
from ...io import clean_path as clean_path
from ...parallel import multithreading as multithreading
from ...print import colored_for_loop as colored_for_loop, debug as debug, error as error, info as info, warning as warning
from .config import Config as Config, FFMPEG_RELEASES as FFMPEG_RELEASES, YOUTUBE_BITRATE_RECOMMENDATIONS as YOUTUBE_BITRATE_RECOMMENDATIONS
from .image import convert_frame as convert_frame, get_all_files as get_all_files, upscale_folder as upscale_folder
from typing import Literal

def get_recommended_bitrate(resolution: tuple[int, int], frame_rate: int = 60, upload_type: Literal['SDR', 'HDR'] = 'SDR') -> int:
    ''' Get the recommended bitrate (in kbps) for the output video based on the video resolution.

\tArgs:
\t\tresolution  (tuple[int, int]):       Video resolution (width, height).
\t\tframe_rate  (int):                   Frame rate of the video, default is 60.
\t\tupload_type (Literal["SDR","HDR"]):  Upload type from which the recommendation is made, default is "SDR".

\tReturns:
\t\tint:     The recommended bitrate for the output video (in kbps)

\tSource: https://support.google.com/youtube/answer/1722171?hl=en#zippy=%2Cbitrate

\tExamples:
\t\t>>> # Valid examples
\t\t>>> get_recommended_bitrate((3840, 2160), 60, "SDR")
\t\t68000
\t\t>>> get_recommended_bitrate((1920, 1080), 60, "HDR")
\t\t15000
\t\t>>> get_recommended_bitrate((1920, 1080), 60, "SDR")
\t\t12000
\t\t>>> get_recommended_bitrate((1920, 1080), 30, "SDR")
\t\t8000

\t\t>>> # Invalid examples
\t\t>>> get_recommended_bitrate((1920, 1080), 60, "Ratio")
\t\tTraceback (most recent call last):
\t\t\t...
\t\tAssertionError: Invalid upload type: \'Ratio\'
\t\t>>> get_recommended_bitrate("1920x1080", 60, "SDR")
\t\tTraceback (most recent call last):
\t\t\t...
\t\tAssertionError: Invalid resolution: 1920x1080, must be a tuple of two integers
\t\t>>> get_recommended_bitrate((1920, 1080), -10, "SDR")
\t\tTraceback (most recent call last):
\t\t\t...
\t\tAssertionError: Invalid frame rate: -10, must be a positive integer
\t'''
def check_ffmpeg_executable() -> None: ...
def upscale_video(video_file: str, input_folder: str, progress_folder: str, output_folder: str) -> None:
    """ Handles a video file. """
def video_upscaler_cli(input_folder: str, progress_folder: str, output_folder: str) -> None:
    """ Upscales videos from an input folder and saves them to an output folder.

\tUses intermediate folders for extracted and upscaled frames within the progress folder.
\t**Handles resuming partially processed videos.**

\tArgs:
\t\tinput_folder    (str): Path to the folder containing input videos.
\t\tprogress_folder (str): Path to the folder for storing intermediate files (frames).
\t\toutput_folder   (str): Path to the folder where upscaled videos will be saved.
\t"""
