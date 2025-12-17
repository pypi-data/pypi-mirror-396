# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

"""
Functions for handling Q-CTRL styling.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any

from cycler import cycler
from matplotlib import rcParams
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.pyplot import isinteractive
from matplotlib.style import context

BORDER_COLOR = "#D4D4E3"
TEXT_COLOR = "#73739C"

DPI = 72
FIG_WIDTH = 10.0
FIG_HEIGHT = 5.0

#: A list of colors defined in the Q-CTRL style.
QCTRL_STYLE_COLORS = [
    "#680CE9",
    "#FF4242",
    "#0DBA9A",
    "#F3B435",
    "#E55285",
    "#2B95ED",
    "#DE6B08",
    "#32B84B",
]

QCTRL_SEQUENTIAL_COLORMAP = LinearSegmentedColormap.from_list(
    "QCTRL_SEQUENTIAL_COLORMAP",
    ["#FFFFFF", "#E5DBFF", "#AB8DFB", "#680CE9", "#44108E"],
    N=200,
)
QCTRL_SEQUENTIAL_COLORMAP.__doc__ = "A sequential color map in the Q-CTRL style."


QCTRL_DIVERGENT_COLORMAP = LinearSegmentedColormap.from_list(
    "QCTRL_DIVERGENT_COLORMAP",
    ["#D02323", "#FF8A8A", "#FFC2C2", "#FFFFFF", "#D0BFFF", "#AB8DFB", "#680CE9"],
    N=200,
)
QCTRL_DIVERGENT_COLORMAP.__doc__ = "A divergent color map in the Q-CTRL style."


def get_qctrl_style() -> dict[str, Any]:
    """
    Return a dictionary representing the Q-CTRL styling in Matplotlib format.

    The returned dictionary is suitable for passing to Matplotlib functions such as
    ``matplotlib.style.use`` or ``matplotlib.style.context``.

    Returns
    -------
    dict
        The dictionary representing the Q-CTRL style.
    """
    style: dict[str, Any] = {}

    # Set text color.
    style["text.color"] = TEXT_COLOR
    style["xtick.color"] = TEXT_COLOR
    style["ytick.color"] = TEXT_COLOR
    style["axes.labelcolor"] = TEXT_COLOR

    # Set font to Roboto.
    style["font.sans-serif"] = ["Roboto"] + rcParams["font.sans-serif"]

    # Set figure size and dpi.
    style["figure.figsize"] = [FIG_WIDTH, FIG_HEIGHT]
    style["figure.dpi"] = DPI

    # Set borders and their color.
    style["axes.spines.left"] = True
    style["axes.spines.right"] = True
    style["axes.spines.top"] = True
    style["axes.spines.bottom"] = True
    style["axes.edgecolor"] = BORDER_COLOR
    style["legend.edgecolor"] = BORDER_COLOR
    style["lines.color"] = BORDER_COLOR

    # Set font sizes.
    style["font.size"] = 14
    style["legend.title_fontsize"] = 14
    style["legend.fontsize"] = 14
    style["figure.titlesize"] = 16
    style["axes.titlesize"] = 14
    style["axes.labelsize"] = 14
    style["xtick.labelsize"] = 12
    style["ytick.labelsize"] = 12

    # Set padding around labels.
    style["axes.labelpad"] = 15.0

    # Set background color white.
    style["figure.facecolor"] = "white"

    # Set cycle of colors for lines.
    style["axes.prop_cycle"] = cycler(color=QCTRL_STYLE_COLORS)

    # Set line width.
    style["lines.linewidth"] = 2

    return style


@contextmanager
def qctrl_style():
    """
    A ``ContextDecorator`` that enables the Q-CTRL Matplotlib styling.

    The returned object can act as a decorator::

        @qctrl_style()
        def plot(*args):
            # Matplotlib calls made in this function will use Q-CTRL styling.
            pass

    The returned object can also act as a context manager::

        with qctrl_style():
            # Matplotlib calls made in this context will use Q-CTRL styling.
            pass

    The try-finally clause records the interactive mode inside the context manager from
    Matplotlib, which might be mutated in runtime, depending on which backend is used.
    The outer finally statement recovers this option, to be consistent with the behavior of
    Matplotlib.
    See https://github.com/qctrl/python-visualizer/pull/261 more details.
    """
    try:
        with context(get_qctrl_style()) as ctx:
            try:
                yield ctx
            finally:
                interactive_mode_state = isinteractive()
    finally:
        rcParams["interactive"] = interactive_mode_state
