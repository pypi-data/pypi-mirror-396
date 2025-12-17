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
Function for plotting the the absolute value of each matrix element in a density matrix.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .style import (
    BORDER_COLOR,
    QCTRL_SEQUENTIAL_COLORMAP,
    qctrl_style,
)
from .utils import (
    check_argument,
    create_figure,
    safe_greater_than,
    safe_less_than,
)


@qctrl_style()
def plot_density_matrix(
    density_matrix: np.ndarray,
    basis_labels: list[str] | None = None,
    rotate_column_labels: bool = False,
    *,
    figure: Figure | None = None,
):
    """
    Create a heatmap with the absolute values of a density matrix's elements.

    Parameters
    ----------
    density_matrix : np.ndarray
        The density matrix ρ to plot.
    basis_labels : list(str) or None, optional
        A list of strings representing the labels of the basis in which ρ is represented.
        The elements of this list will be decorated with bras/kets and then used as the labels for
        the axes. Its length must match the dimension of `density_matrix`.
        Defaults to `["0", "1", ...]`.
    rotate_column_labels : bool, optional
        Whether to rotate the column labels by 90 degrees. Defaults to False.
    figure : matplotlib.figure.Figure or None, optional
        A matplotlib Figure in which to place the plots.
        If passed, its dimensions and axes will be overridden.

    Examples
    --------
    Plot the density matrix of a five-level system. ::

        import numpy as np
        from qctrlvisualizer import plot_density_matrix

        density_matrix = np.array(
            [
                [0.07554607, 0.03935068, 0.16941076, 0.09644551, 0.17403635],
                [0.03935068, 0.02049711, 0.08824322, 0.05023684, 0.09065261],
                [0.16941076, 0.08824322, 0.37990067, 0.21627735, 0.39027348],
                [0.09644551, 0.05023684, 0.21627735, 0.12312664, 0.22218259],
                [0.17403635, 0.09065261, 0.39027348, 0.22218259, 0.40092951],
            ]
        )

        plot_density_matrix(density_matrix)

    .. plot::

        import numpy as np
        from qctrlvisualizer import plot_density_matrix

        density_matrix = np.array(
            [
                [0.07554607, 0.03935068, 0.16941076, 0.09644551, 0.17403635],
                [0.03935068, 0.02049711, 0.08824322, 0.05023684, 0.09065261],
                [0.16941076, 0.08824322, 0.37990067, 0.21627735, 0.39027348],
                [0.09644551, 0.05023684, 0.21627735, 0.12312664, 0.22218259],
                [0.17403635, 0.09065261, 0.39027348, 0.22218259, 0.40092951],
            ]
        )

        plot_density_matrix(density_matrix)
    """
    figure = create_figure(figure)
    absolute_density_matrix = _validate_density_matrix(density_matrix)
    dimension = len(absolute_density_matrix)
    row_labels, col_labels = _validate_basis_labels(basis_labels, dimension)

    axes = figure.subplots(nrows=1, ncols=1)
    assert isinstance(axes, Axes)

    if rotate_column_labels:
        rotation = 90
    else:
        rotation = 0
    axes.set_yticks(np.arange(dimension), labels=row_labels)
    axes.set_xticks(np.arange(dimension), labels=col_labels, rotation=rotation)
    axes.tick_params(axis="both", which="major", left=False, bottom=False, pad=8)

    density_plot = axes.imshow(
        absolute_density_matrix,
        cmap=QCTRL_SEQUENTIAL_COLORMAP,
        vmin=0,
    )

    pixels = 1 / plt.rcParams["figure.dpi"]
    bbox = axes.get_window_extent().transformed(figure.dpi_scale_trans.inverted())
    width = bbox.width
    legend_distance = 16 * pixels / width

    color_bar = axes.figure.colorbar(density_plot, ax=axes, pad=legend_distance)  # type: ignore[union-attr]
    color_bar.ax.set_ylabel(
        "Absolute values of matrix elements",
        rotation=-90,
        labelpad=16,
        va="bottom",
    )
    color_bar.ax.yaxis.set_tick_params(pad=8)

    plt.hlines(
        y=np.arange(0, dimension) + 0.5,
        xmin=-0.5,
        xmax=dimension - 0.5,
        lw=1.5,
        color=BORDER_COLOR,
    )
    plt.vlines(
        x=np.arange(0, dimension) + 0.5,
        ymin=-0.5,
        ymax=dimension - 0.5,
        lw=1.5,
        color=BORDER_COLOR,
    )


def _validate_density_matrix(density_matrix: np.ndarray) -> np.ndarray:
    """
    Validate the input density matrix and compute its element-wise absolute values.
    """
    check_argument(
        isinstance(density_matrix, np.ndarray) and density_matrix.dtype.kind in "iufc",
        "The density matrix must be a numeric NumPy array.",
        extras={"type(density_matrix)": type(density_matrix)},
    )
    check_argument(
        density_matrix.ndim == 2 and density_matrix.shape[0] == density_matrix.shape[1],
        "The density matrix must be square.",
        extras={"density_matrix.shape": density_matrix.shape},
    )
    check_argument(
        np.allclose(density_matrix, density_matrix.T.conj()),
        "The density matrix must be Hermitian, but does not equal its Hermitian conjugate.",
    )

    diagonal_elements = np.diagonal(density_matrix)
    check_argument(
        all(np.isreal(diagonal_elements)),
        "The diagonal elements of the density matrix must be real.",
        extras={"diag(density_matrix)": diagonal_elements},
    )

    check_argument(
        not safe_less_than(diagonal_elements, 0) and (not safe_greater_than(diagonal_elements, 1)),
        "The diagonal elements of the density matrix have to be between 0 and 1.",
        extras={"diag(density_matrix)": diagonal_elements},
    )

    check_argument(
        np.isclose(sum(diagonal_elements), 1),
        "The trace of the density matrix must be 1.",
        extras={"trace(density_matrix)": sum(diagonal_elements)},
    )

    return np.absolute(density_matrix)


def _validate_basis_labels(
    basis_labels: list[str] | None,
    dimension,
) -> tuple[list[str], list[str]]:
    """
    Validate the input `basis_labels` if passed and set to default if not.
    """
    if basis_labels is None:
        row_labels = [rf"$|{i}\rangle$" for i in range(dimension)]
        col_labels = [rf"$\langle{i}|$" for i in range(dimension)]
    else:
        check_argument(
            isinstance(basis_labels, list)
            and all(isinstance(label, str) for label in basis_labels),
            "The basis labels must be a list of strings.",
            extras={"basis_labels": basis_labels},
        )

        check_argument(
            dimension == len(basis_labels),
            "The length of basis_labels must coincide with the dimension of the density matrix.",
            extras={"dimension": dimension, "len(basis_label)": len(basis_labels)},
        )

        row_labels = [rf"$|\rm {label}\rangle$" for label in basis_labels]
        col_labels = [rf"$\langle\rm {label}|$" for label in basis_labels]

    return row_labels, col_labels
