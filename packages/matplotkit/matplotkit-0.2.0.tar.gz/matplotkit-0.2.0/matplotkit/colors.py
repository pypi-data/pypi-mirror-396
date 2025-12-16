#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from typing import List

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import rgb2hex


def get_colors(n: int, cmap_name: str = "tab10") -> List[str]:
    """Generate discrete colors from a matplotlib colormap.

    Args:
        n: Number of colors to generate
        cmap_name: Name of the colormap to use (default: 'tab10')
            Some good options:
            - 'tab10', 'tab20': Qualitative colormaps
            - 'viridis', 'plasma': Sequential colormaps
            - 'RdYlBu': Diverging colormap

    Returns:
        List of hex color codes
    """
    cmap = plt.get_cmap(cmap_name)
    colors = [rgb2hex(cmap(i)) for i in np.linspace(0, 1, n)]
    return colors
