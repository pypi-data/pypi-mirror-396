from yta_temp import Temp
from yta_logger import ConsolePrinter
from pathlib import Path

import av
import subprocess


CACHE_PREFIX: str = 'cache_yta'
"""
The prefix we use for the temporary files we create
by using the cache.
"""

class FramesCacheFactory:
    """
    Factory to simplify the access to our cached frames.

    Use its static methods to obtain the frames.
    """

    @staticmethod
    def black_video_frame(
        size: tuple[int, int],
        video_fps: float,
    ):
        """
        Get a black video frame by using the cache system.
        """
        return BlackFrameCache.get(
            size = size,
            video_fps = video_fps
        )

    @staticmethod
    def silent_audio_frame(
        audio_fps: float,
        audio_layout: str,
        audio_format: str,
        audio_samples_per_frame: float
    ):
        """
        Get a silent audio frame by using the cache system.
        """
        return SilentAudioFrameCache.get(
            audio_fps = audio_fps,
            audio_layout = audio_layout,
            audio_format = audio_format,
            audio_samples_per_frame = audio_samples_per_frame
        )

class BlackFrameCache:
    """
    A black video frames cached generator, useful when we
    need the same black frames again and again.

    This class will create temporary files (in the WIP folder)
    to load them directly with the pyav library.
    """

    _cache = {}
    """
    The cache that is able to store all the black frames that
    we create during the process. The frame specifications 
    will be the key to access it in the dict.
    """

    @staticmethod
    def get(
        size: tuple[int, int],
        video_fps: float,
        # TODO: Create 'transparency'
    ) -> 'VideoFrame':
        """
        Get a black video frame of the provided `size` and
        with the also given `video_fps` and `pixel_format`.

        The video frames will be cached so the access the
        next time is instantaneous.
        """
        # TODO: This has to be changed to 'rgba' if we want
        # to apply some transparency
        # TODO: But how do we generate it with a transparency?
        # and how do we manage the cache if 0.02 is not 0.03 (?)
        pixel_format = 'rgb24'

        key = (size[0], size[1], video_fps, pixel_format)

        if key in BlackFrameCache._cache:
            return BlackFrameCache._cache[key]

        width, height = size

        # Temporary specific file
        filename = f'{CACHE_PREFIX}_black_{width}x{height}_{video_fps}_{pixel_format}.mp4'
        filename = Temp.get_custom_wip_filename(filename)

        if not Path(filename).exists():
            cmd = [
                'ffmpeg',
                '-y',
                '-f', 'lavfi',
                '-i', f'color=size={width}x{height}:color=black',
                '-pix_fmt', pixel_format,
                '-frames:v', '1',
                '-r', str(video_fps),
                str(filename)
            ]
            # TODO: We should do this with a subprocess... it is
            # not a good thing when we want to create services
            subprocess.run(cmd, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

            ConsolePrinter().print(f'The black cached frame has been created as "{filename}"')

        # Load decoded frame
        container = av.open(str(filename))
        frame = next(container.decode(video = 0))

        # Store in cache
        BlackFrameCache._cache[key]: 'VideoFrame' = frame

        return frame

class SilentAudioFrameCache:
    """
    A silent audio frames cached generator, useful when we
    need the same silent frames again and again.

    This class will create temporary files (in the WIP folder)
    to load them directly with the pyav library.
    """

    _cache = {}
    """
    The cache that is able to store all the silent frames that
    we create during the process. The frame specifications 
    will be the key to access it in the dict.
    """

    @staticmethod
    def get(
        # TODO: Review the parameter types and that...
        audio_fps: float,
        audio_layout: str,
        audio_format: str,
        audio_samples_per_frame: float
    ):
        """
        Get a silent audio frame with the provided `audio_fps`,
        `audio_layout`, `audio_format` and `audio_samples_per_frame`.

        The audio frames will be cached so the access the
        next time is instantaneous.
        """
        key = (audio_fps, audio_layout, audio_format, audio_samples_per_frame)

        if key in SilentAudioFrameCache._cache:
            return SilentAudioFrameCache._cache[key]

        # Temporary specific file
        filename = f'{CACHE_PREFIX}_silence_{audio_fps}_{audio_layout}_{audio_format}_{audio_samples_per_frame}.wav'
        filename = Temp.get_custom_wip_filename(filename)

        if not Path(filename).exists():
            duration = audio_samples_per_frame / audio_fps

            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'anullsrc=channel_layout={audio_layout}:sample_rate={audio_fps}',
                '-t', str(duration),
                #'-c:a', audio_format,
                # TODO: What about this forced format (?)
                '-c:a', 'pcm_f32le',
                # Apparently this '-frames:a' is stupid and we need the '-t' instead
                #'-frames:a', '1',
                str(filename)
            ]
            # TODO: We should do this with a subprocess... it is
            # not a good thing when we want to create services
            subprocess.run(cmd, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

            ConsolePrinter().print(f'The silent audio cached frame has been created as "{filename}"')

        # Load decoded frame
        container = av.open(str(filename))
        frame = next(container.decode(audio = 0))

        # Store in cache
        SilentAudioFrameCache._cache[key]: 'AudioFrame' = frame

        return frame
