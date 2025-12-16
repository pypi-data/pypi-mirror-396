WAIFU2X_NCNN_VULKAN_RELEASES: dict[str, str]
FFMPEG_RELEASES: dict[str, str]
YOUTUBE_BITRATE_RECOMMENDATIONS: dict[str, dict[str, dict[int, int]]]

class Config:
    """ Configuration class for the upscaler. """
    JPG_QUALITY: int
    VIDEO_FINAL_BITRATE: int
    FFMPEG_EXECUTABLE: str
    FFMPEG_ARGS: tuple[str, ...]
    FFPROBE_EXECUTABLE: str
    FFMPEG_CHECK_HELP_TEXT: str
    UPSCALER_EXECUTABLE: str
    UPSCALER_ARGS: tuple[str, ...]
    UPSCALER_EXECUTABLE_HELP_TEXT: str
    SLIGHTLY_FASTER_MODE: bool
    upscaler_executable_checked: bool
    ffmpeg_executable_checked: bool
