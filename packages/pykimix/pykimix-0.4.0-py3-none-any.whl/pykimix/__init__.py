import os
from kivy import Config
os.environ["KIVY_NO_MTDEV"] = "1"
Config.set('kivy', 'window', 'sdl2')
Config.set('kivy', 'audio', 'dummy')

try:
    from .c import *
except ImportError:
    pass

from .integration_engine import IntegrationEngine
from .resources import load_image, load_sound, load_font
from .sprites import Sprite
from .audio import MusicPlayer
from .input import InputManager
from .gpu import GPU
from .utils import *

__all__ = [
    "IntegrationEngine",
    "load_image",
    "load_sound",
    "load_font",
    "Sprite",
    "MusicPlayer",
    "InputManager",
    "GPU"
]

__version__ = "0.4.0"