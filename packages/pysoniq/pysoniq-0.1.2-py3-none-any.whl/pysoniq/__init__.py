# Copyright (c) 2025 laelume | Ashlae Blum'e 
# Licensed under the MIT License

"""pysoniq - Lightweight cross-platform audio library"""

from .play import play
from .stop import stop
from .pause import pause, resume, is_paused
from .io import load, save
from .loop import set_loop, is_looping

from .gain import (
    set_gain, get_gain, 
    set_volume_db, get_volume_db,
    adjust_gain_level, normalize, compress, limiter,
    db_to_linear, linear_to_db
)

from .fourier import stft, fft_frequencies, frames_to_time, amplitude_to_db
from .visualize import spectrog

__version__ = '0.1.2'
__author__ = "laelume"
__license__ = "MIT"
__all__ = [
    'play', 'stop', 
    'pause', 'resume', 'is_paused',
    'load', 'save', 
    'set_loop', 'is_looping',
    
    'set_gain', 'get_gain', 'set_volume_db', 'get_volume_db',
    'adjust_gain_level', 'normalize', 'compress', 'limiter',
    'db_to_linear', 'linear_to_db', 

    'stft', 'fft_frequencies', 'frames_to_time', 'amplitude_to_db', 

    'spectrog'
]

