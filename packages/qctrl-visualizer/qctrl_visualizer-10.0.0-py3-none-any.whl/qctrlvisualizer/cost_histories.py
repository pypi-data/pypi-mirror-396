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

from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .style import qctrl_style
from .utils import (
    check_argument,
    create_figure,
)


@qctrl_style()
def plot_cost_histories(
    cost_histories: list,
    labels: list[str] | None = None,
    y_axis_log: bool = False,
    initial_iteration: int = 1,
    *,
    figure: Figure | None = None,
):
    """
    Create a plot of the cost against iterations for either a single cost history or
    a set of cost histories.

    Parameters
    ----------
    cost_histories : list
        The values of the cost histories.
        Must be either a list of a single cost history or a list of several cost histories,
        where each individual cost history is a list.
        For example, a single cost history can be passed
        (``cost_histories = [0.1, 0.05, 0.02]``) or multiple cost histories
        (``cost_histories = [[0.1, 0.05, 0.02], [0.23, 0.2, 0.14, 0.1, 0.04, 0.015]]``).
    labels : list[str] or None, optional
        The labels corresponding to the individual cost histories in `cost_histories`.
        If you provide this, it must be the same length as `cost_histories`.
    y_axis_log : bool, optional
        Whether the y-axis is log-scale.
        Defaults to False.
    initial_iteration : int, optional
        Where the iteration count on the x-axis starts from.
        This is useful if you want to include the initial cost—before optimization—at
        iteration 0 or if you pass cost histories that start at a later iteration.
        Defaults to 1.
    figure : matplotlib.figure.Figure or None, optional
        A matplotlib Figure in which to place the plots.
        If passed, its dimensions and axes will be overridden.

    Examples
    --------
    Compare the cost histories of two closed-loop optimizers. ::

        from qctrlvisualizer import plot_cost_histories

        cost_histories = [
            [0.1, 0.05, 0.02, 0.015, 0.009, 0.006, 0.004, 0.001],
            [0.23, 0.2, 0.14, 0.08, 0.04, 0.025, 0.015, 0.01, 0.008, 0.005, 0.004, 0.002, 0.001],
        ]

        plot_cost_histories(
            cost_histories=cost_histories, labels=["CMA-ES", "Simulated annealing"]
        )


    .. plot::

        import matplotlib.pyplot as plt
        from qctrlvisualizer import plot_cost_histories

        cost_histories = [
            [0.1, 0.05, 0.02, 0.015, 0.009, 0.006, 0.004, 0.001],
            [0.23, 0.2, 0.14, 0.08, 0.04, 0.025, 0.015, 0.01, 0.008, 0.005, 0.004, 0.002, 0.001],
        ]

        plot_cost_histories(
            cost_histories=cost_histories, labels=["CMA-ES", "Simulated annealing"]
        )
        plt.tight_layout()
    """
    figure = create_figure(figure)
    axs = figure.subplots(nrows=1, ncols=1)
    assert isinstance(axs, Axes)

    check_argument(
        isinstance(cost_histories, list),
        "The cost histories must be in a list.",
        extras={"type(cost_histories)": type(cost_histories)},
    )

    if not all(isinstance(history, list) for history in cost_histories):
        cost_histories = [cost_histories]

    if labels is not None:
        check_argument(
            len(cost_histories) == len(labels),
            "If passed, the labels must have the same length as the list of cost histories.",
            extras={
                "len(labels)": len(labels),
                "len(cost_histories)": len(cost_histories),
            },
        )

        for cost_history, label in zip(cost_histories, labels):
            axs.plot(
                range(initial_iteration, initial_iteration + len(cost_history)),
                cost_history,
                label=label,
            )
        axs.legend(loc="upper left", bbox_to_anchor=(1, 1))
    else:
        for cost_history in cost_histories:
            axs.plot(
                range(initial_iteration, initial_iteration + len(cost_history)),
                cost_history,
            )

    axs.set_xlabel("Iteration")
    axs.set_ylabel("Cost")

    if y_axis_log:
        axs.set_yscale("log")
