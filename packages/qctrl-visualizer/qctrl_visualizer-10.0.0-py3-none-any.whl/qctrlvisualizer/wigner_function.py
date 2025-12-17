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
Functions for plotting cost vs iterations.
"""

from __future__ import annotations

import numpy as np
from matplotlib.axes import Axes
from matplotlib.colors import TwoSlopeNorm
from matplotlib.figure import Figure

from .style import (
    QCTRL_DIVERGENT_COLORMAP,
    qctrl_style,
)
from .utils import (
    check_argument,
    create_figure,
)


@qctrl_style()
def plot_wigner_function(
    wigner_function: np.ndarray,
    position: np.ndarray,
    momentum: np.ndarray,
    contour_count: int = 100,
    *,
    figure: Figure | None = None,
):
    r"""
    Create a contour plot of the specified Wigner function.

    Parameters
    ----------
    wigner_function : np.ndarray
        The Wigner function values. Only the real part of this array will be plotted.
        Must be a 2D array of shape ``(L, K)``.
    position : np.ndarray
        The dimensionless position vector.
        Must be a strictly increasing 1D array of length `L`.
    momentum : np.ndarray
        The dimensionless momentum vector.
        Must be a strictly increasing 1D array of length `K`.
    contour_count : int, optional
        The number of contour lines, the larger the value the finer the contour plot will be.
        Defaults to 100.
    figure : matplotlib.figure.Figure or None, optional
        A matplotlib Figure in which to place the plots.
        If passed, its dimensions and axes will be overridden.

    Examples
    --------
    Plot the Wigner function associated to state
    :math:`(|0 \rangle + |5 \rangle) / \sqrt{2}`. ::

        import numpy as np
        import boulderopal as bo
        from qctrlvisualizer import plot_wigner_function

        position = np.linspace(-5, 5, 100)
        momentum = np.linspace(-5, 5, 100)

        graph = bo.Graph()

        state = (graph.fock_state(10, 0) + graph.fock_state(10, 5)) / np.sqrt(2)
        density_matrix = graph.outer_product(state, state)

        wigner_transform = graph.wigner_transform(
            density_matrix, position, momentum, name="wigner_transform"
        )

        wigner_function = bo.execute_graph(
            graph=graph, output_node_names=["wigner_transform"]
        )["output"]["wigner_transform"]["value"]

        plot_wigner_function(wigner_function, position, momentum)


    .. plot::

        import json
        import matplotlib.pyplot as plt
        import numpy as np
        from qctrlcommons.serializers import decode
        from qctrlvisualizer import plot_wigner_function

        position = np.linspace(-5, 5, 100)
        momentum = np.linspace(-5, 5, 100)

        with open("../docs/plot_data/wigner_function/plot_wigner_function.json") as file:
            wigner_function = decode(json.load(file))

        plot_wigner_function(wigner_function, position, momentum)
        plt.tight_layout()
        plt.show()
    """
    figure = create_figure(figure)

    check_argument(
        isinstance(wigner_function, np.ndarray) and wigner_function.ndim == 2,
        "The Wigner function must be in a 2D array.",
    )

    _check_axis_array(position, "position", wigner_function, 0)
    _check_axis_array(momentum, "momentum", wigner_function, 1)

    check_argument(
        isinstance(contour_count, (int, np.integer)) and contour_count > 0,
        "The number of contours must be a positive integer.",
        extras={"contour_count": contour_count},
    )

    axes = figure.subplots(nrows=1, ncols=1)
    assert isinstance(axes, Axes)
    axes.set_aspect("equal")

    # Fix divergent colormap with the central color at 0.
    wigner_max_abs = np.max(np.abs(wigner_function))
    norm = TwoSlopeNorm(vcenter=0.0, vmin=-wigner_max_abs, vmax=wigner_max_abs)

    # The Wigner function is a real function, but we only plot the real part
    # in case the user passes a complex array.
    # We also transpose the array so that position is on the x-axis.
    wigner_plot = axes.contourf(
        position,
        momentum,
        wigner_function.T.real,
        levels=contour_count,
        cmap=QCTRL_DIVERGENT_COLORMAP,
        norm=norm,
    )

    figure.colorbar(wigner_plot, ax=axes)

    axes.set_xlabel("Position")
    axes.set_ylabel("Momentum")


def _check_axis_array(array, name, wigner_function, axis):
    check_argument(
        isinstance(array, np.ndarray) and array.ndim == 1,
        f"The {name} must be in a 1D array.",
        extras={name: array},
    )

    check_argument(
        all(np.diff(array) > 0),
        f"The {name} must be a strictly increasing array.",
        extras={name: array},
    )

    rows_or_columns = ["rows", "columns"]

    check_argument(
        wigner_function.shape[axis] == len(array),
        f"The length of the {name} array must match the number of {rows_or_columns[axis]} in the"
        " Wigner function array.",
        extras={
            "wigner_function.shape": wigner_function.shape,
            f"len({name})": len(array),
        },
    )
