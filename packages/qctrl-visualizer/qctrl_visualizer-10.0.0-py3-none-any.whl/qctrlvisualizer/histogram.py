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
Function for plotting histograms.
"""

from __future__ import annotations

import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .style import qctrl_style
from .utils import (
    check_argument,
    create_figure,
)


def _validate_bitstring_counts(bitstring_counts: dict[str, dict[str, int]]) -> int:
    """
    Validate the input arguments of `plot_bitstring_probabilities_histogram`.

    Parameters
    ----------
    bitstring_counts : dict[str, dict[str, int]]
        Nested dictionaries of experiments with the resulting bitstring counts to plot.

    Returns
    -------
    int
        The length of the bitstrings.
    """
    check_argument(
        isinstance(bitstring_counts, dict),
        "The input bitstring counts must be in a dictionary.",
        extras={"type(bitstring_counts)": type(bitstring_counts)},
    )

    for experiment, counts in bitstring_counts.items():
        check_argument(
            isinstance(bitstring_counts[experiment], dict),
            "The counts must be dictionaries.",
            extras={f"bitstring_counts['{experiment}']": counts},
        )
        check_argument(
            len(bitstring_counts[experiment]) > 0,
            "The inner count dictionaries must not be empty.",
            extras={f"bitstring_counts['{experiment}']": bitstring_counts[experiment]},
        )

    first_key = next(iter(bitstring_counts))
    bitstring_length = len(next(iter(bitstring_counts[first_key])))

    for experiment, counts in bitstring_counts.items():
        for bitstring, count in counts.items():
            check_argument(
                count >= 0,
                "The number of counts for each bitstring must be non-negative.",
                extras={f'bitstring_counts["{experiment}"]["{bitstring}"]': count},
            )
            check_argument(
                len(bitstring) == bitstring_length,
                "The length of all bitstrings must be the same.",
            )

    return bitstring_length


@qctrl_style()
def plot_bitstring_probabilities_histogram(
    bitstring_counts: dict[str, dict[str, int]],
    show_legend: bool = True,
    rotate_x_axis_labels: bool = True,
    display_all_bitstrings: bool = False,
    *,
    figure: Figure | None = None,
):
    """
    Create a histogram of the specified counts.

    Parameters
    ----------
    bitstring_counts : dict[str, dict[str,int]]
        Nested dictionaries of experiments with the resulting bitstring counts to plot, of the form
        ``{"Fire Opal": {"00...0": count_0_1 , ..., "11...1": count_0_2n}, ...,
        "IBM": {"00...0": count_1_1, ..., "11...1": count_1_2n}}``.
        The keys of the outer dictionary will be used for the plot legend,
        and the inner dictionaries keys represent the bitstrings whose counts will be plotted.
        The counts must be nonnegative and the length of all bitstring across all
        experiments must be the same.
    show_legend : bool, optional
        Whether to add a legend to the plot. Defaults to True.
    rotate_x_axis_labels : bool, optional
        Whether to rotate the labels of the x-axis by 90 degrees. Defaults to True.
    display_all_bitstrings : bool, optional
        Whether to display all possible bitstrings, including those not
        present in `bitstring_counts`. Defaults to False.
    figure : matplotlib.figure.Figure or None, optional
        A matplotlib Figure in which to place the plots.
        If passed, its dimensions and axes will be overridden.

    Examples
    --------
    Plot a histogram of bitstring counts to compare the performance of an experiment using
    Fire Opal with an experiment not using Fire Opal. ::

        from qctrlvisualizer import plot_bitstring_probabilities_histogram

        bitstring_counts = {
            "with Fire Opal": {"00": 1, "01": 3, "10": 63, "11": 9},
            "without Fire Opal": {"00": 32, "01": 17, "10": 52, "11": 45},
        }

        plot_bitstring_probabilities_histogram(bitstring_counts)


    .. plot::

        import matplotlib.pyplot as plt
        from qctrlvisualizer import plot_bitstring_probabilities_histogram

        bitstring_counts = {
            "with Fire Opal": {"00": 1, "01": 3, "10": 63, "11": 9},
            "without Fire Opal": {"00": 32, "01": 17, "10": 52, "11": 45},
        }

        plot_bitstring_probabilities_histogram(bitstring_counts)
        plt.tight_layout()
    """
    figure = create_figure(figure)
    bitstring_length = _validate_bitstring_counts(bitstring_counts)

    if display_all_bitstrings:
        sorted_bitstrings = [
            np.binary_repr(i, bitstring_length) for i in range(2**bitstring_length)
        ]
    else:
        # Sort the bitstring labels.
        sorted_bitstrings = sorted(set().union(*list(bitstring_counts.values())))

    axes = figure.subplots(nrows=1, ncols=1)
    assert isinstance(axes, Axes)

    default_bar_width = 0.8
    bar_width = default_bar_width / len(bitstring_counts)

    x_axis = np.arange(len(sorted_bitstrings))

    for bar_shift_index, (experiment, counts) in enumerate(bitstring_counts.items()):
        counts_array = np.zeros(len(sorted_bitstrings))
        for index, bitstring in enumerate(sorted_bitstrings):
            counts_array[index] = counts.get(bitstring, 0)

        total_counts = np.sum(counts_array)

        axes.bar(
            x_axis + bar_shift_index * bar_width,
            counts_array / total_counts,
            width=bar_width,
            label=experiment,
        )

    if rotate_x_axis_labels:
        rotation = 90
    else:
        rotation = 0

    axes.set_xticks(
        x_axis + 0.5 * (default_bar_width - bar_width),
        sorted_bitstrings,
        rotation=rotation,
    )
    axes.set_xlabel("Bitstrings")
    axes.set_ylabel("Probability")
    if show_legend:
        axes.legend(loc="upper left", bbox_to_anchor=(1, 1))
