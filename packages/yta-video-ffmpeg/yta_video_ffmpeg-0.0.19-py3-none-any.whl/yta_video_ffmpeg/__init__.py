"""
Module to simplify the use of Ffmpeg and to make
awesome things with simple methods.

Nice help: https://www.bannerbear.com/blog/how-to-use-ffmpeg-in-python-with-examples/
Official doc: https://www.ffmpeg.org/ffmpeg-resampler.html
More help: https://kkroening.github.io/ffmpeg-python/
Nice guide: https://img.ly/blog/ultimate-guide-to-ffmpeg/
Available flags: https://gist.github.com/tayvano/6e2d456a9897f55025e25035478a3a50

Interesting usage: https://stackoverflow.com/a/20325676
Maybe avoid writting on disk?: https://github.com/kkroening/ffmpeg-python/issues/500#issuecomment-792281072

This module needs, of course, 'ffmpeg'
installed in the system to be able to run
it as a command.

TODO: I don't know right now (11/09/2025) 
if it is installed as 'ffmpeg-python' or
if it must be installed in other way. If I
remember it I will write it here.
"""
from yta_video_ffmpeg.handler import FfmpegHandler


__all__ = [
    'FfmpegHandler'
]