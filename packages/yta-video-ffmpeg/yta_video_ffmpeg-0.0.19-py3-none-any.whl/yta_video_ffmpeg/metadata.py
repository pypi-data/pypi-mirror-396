
"""
TODO: Check the 'yta_video_opengl' because 
I'm using pyav there, which is using ffmpeg
in the background, so this is maybe
unnecessary.
"""
from dataclasses import dataclass

import subprocess
import json


@dataclass
class FfmpegVideoMetadata:
    """
    Dataclass to hold the information about
    a video read with Ffmpeg.
    """

    @property
    def width(
        self
    ) -> int:
        """
        The width of the video (in pixels).
        """
        return self.size[0]
    
    @property
    def height(
        self
    ) -> int:
        """
        The height of the video (in pixels).
        """
        return self.size[1]

    def __init__(
        self,
        filename: str,
        json_data: any
    ):
        self.filename: str = filename
        """
        The video file name.
        """

        format_data = json_data.get('format', {})
        self.duration = float(format_data.get('duration', 0))
        """
        The duration of the video in seconds.
        """
        self.size: tuple[int, int] = format_data.get('size', (0, 0))
        """
        The size (width, height) of the video in
        pixels.
        """
        self.bit_rate = int(format_data.get('bit_rate', 0))
        self.video = {
            'codec': None,
            'size': None,
            'fps': None,
            'pix_fmt': None
        }
        self.audio = {}

        for stream in json_data.get('streams', []):
            if stream.get('codec_type') == 'video':
                # FPS se calcula a partir de r_frame_rate
                fps_str = stream.get("r_frame_rate", "0/0")
                try:
                    num, den = map(int, fps_str.split("/"))
                    fps = num / den if den != 0 else 0
                except ValueError:
                    fps = 0

                self.video_codec: str = stream.get('codec_name', None)
                self.size: tuple[int, int] = (
                    int(stream.get('width', 0)),
                    int(stream.get('height', 0))
                )
                self.fps = fps
                self.pixel_format = stream.get('pix_fmt')

                self.has_alpha = False
                if (
                    self.pixel_format and
                    any(
                        a in self.pixel_format
                        for a in ['a', 'alpha']
                    )
                ):
                    # Ej: yuva420p, rgba, bgra...
                    if self.pixel_format.startswith(('yuva', 'rgba', 'bgra', 'argb', 'ya')):
                        self.has_alpha = True

                # Rotation
                # TODO: None or 0 (?)
                rotation = None
                if 'tags' in stream and 'rotate' in stream['tags']:
                    try:
                        rotation = int(stream['tags']['rotate'])
                    except ValueError:
                        pass

                # Caso 2: side_data_list con "rotation"
                for side_data in stream.get('side_data_list', []):
                    if 'rotation' in side_data:
                        try:
                            rotation = int(side_data['rotation'])
                        except ValueError:
                            pass

                self.rotation = rotation
            elif stream.get('codec_type') == 'audio':
                self.audio_codec: str = stream.get('codec_name', None)
                self.number_of_channels = int(stream.get('channels', 0))
                self.sample_rate = int(stream.get('sample_rate', 0))

    @staticmethod
    def from_file(
        filename: str
    ) -> 'FfmpegVideoMetadata':
        """
        Create a FfmpegVideoMetadata instance with the
        information of the video with the 'filename'
        provided.
        """
        cmd = [
            'ffprobe',
            # Errors only
            '-v',
            'error',
            # General data (duration, bitrate, etc.)
            '-show_format',
            # Stream info (video, audio, etc.)
            '-show_streams',
            '-print_format',
            # Format as json
            'json',
            filename
        ]
        
        result = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, text = True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Error ejecutando ffprobe: {result.stderr}")
        
        json_data = json.loads(result.stdout)

        return FfmpegVideoMetadata(filename, json_data)