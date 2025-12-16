#             ___  ___ ___________ _____
#             |  \/  |/  ___|  ___|_   _|
#  _ __  _   _| .  . |\ `--.| |_    | |
# | '_ \| | | | |\/| | `--. \  _|   | |
# | |_) | |_| | |  | |/\__/ / |     | |
# | .__/ \__, \_|  |_/\____/\_|     \_/
# | |     __/ |        python Multi-Slice
# |_|    |___/         Fourier-Transforms


__version__ = '1.0.0'
__all__ = ['shapes', 'simulation', 'utilities', 'GPU_USED', 'xp', 'multiprocessing']

import numpy as np
import os
import multiprocessing

CPU_FORCED = os.getenv("pyMSFT_FORCE_CPU", "False")

if CPU_FORCED == "True":
    GPU_USED = False
    xp = np
else:
    try:
        import cupy as xp
        multiprocessing.set_start_method('spawn', force=True)
        GPU_USED = True
        from cupyx.scipy.fft import get_fft_plan, fft2, ifft2
        xp.cupyx_get_fft_plan = get_fft_plan
        xp.cupyx_fft2 = fft2
        xp.cupyx_ifft2 = ifft2
    except ModuleNotFoundError:
        xp = np
        GPU_USED = False

from . import shapes
from . import simulation