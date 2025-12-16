
"""
TODO: Check the 'yta_video_opengl' because 
I'm using pyav there, which is using ffmpeg
in the background, so this is maybe
unnecessary.
"""
from yta_video_ffmpeg.metadata import FfmpegVideoMetadata
import numpy as np
import subprocess


class FfmpegReader:
    """
    Class to wrap functionality related to
    reading videos.
    """

    @property
    def process(
        self
    ):
        """
        Get an instance of an ffmpeg process.

        The command:
        - `ffmpeg -i {filename} -f image2pipe -pix_fmt {pixel_format} -vcodec rawvideo -`
        """
        if not hasattr(self, '_process'):
            self._process = subprocess.Popen(
                [
                    'ffmpeg',
                    '-i',
                    self.filename,
                    '-f',
                    'image2pipe',
                    '-pix_fmt',
                    self.pixel_format,
                    '-vcodec',
                    'rawvideo',
                    '-'
                ],
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE
            )

        return self._process
    
    @property
    def width(
        self
    ) -> int:
        """
        The width of the video (in pixels).
        """
        return self.metadata.width
    
    @property
    def height(
        self
    ) -> int:
        """
        The height of the video (in pixels).
        """
        return self.metadata.height

    def __init__(
        self,
        filename: str,
        pixel_format: str = 'rgba'
    ):
        self.filename: str = filename
        """
        The filename of the video we are reading.
        """
        self.metadata: FfmpegVideoMetadata = FfmpegVideoMetadata.from_file(filename)
        """
        The information about the video.
        """

        # TODO: Why this 'pixel_format' (?)
        self.pixel_format = pixel_format
        self.process = None

    def read_frame(
        self
    ) -> np.ndarray:
        """
        Read a frame by using the `width`, `height` and the length
        of the `pixel_format` to read the info from the buffer and
        then reshape it into a numpy array.
        """
        frame_size = self.width * self.height * len(self.pixel_format)
        raw_frame = self.process.stdout.read(frame_size)

        if len(raw_frame) != frame_size:
            # End of the video
            return None

        frame = np.frombuffer(raw_frame, np.uint8).reshape((self.height, self.width, len(self.pixel_format)))

        return frame
    
    def close(self):
        """
        Force to close the process.
        """
        if self.process:
            self.process.stdout.close()
            self.process.terminate()
            self.process.wait()
            self.process = None
