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
Functions for plotting the populations.
"""

from __future__ import annotations

import warnings
from typing import NamedTuple

import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .style import qctrl_style
from .utils import (
    check_argument,
    create_figure,
    get_units,
    safe_greater_than,
    safe_less_than,
)


@qctrl_style()
def plot_population_dynamics(
    sample_times: np.ndarray,
    populations: dict,
    *,
    figure: Figure | None = None,
):
    r"""
    Create a plot of the dynamics of the specified populations.

    Parameters
    ----------
    sample_times : np.ndarray
        The 1D array of times in seconds at which the populations have been sampled.
    populations : dict
        The dictionary of populations to plot, of the form
        ``{"label_1": population_values_1, "label_2": population_values_2, ...}``.
        Each `population_values_n` is a 1D array of population values with the same
        length as `sample_times` and `label_n` is its label.
        Population values must lie between 0 and 1.
    figure : matplotlib.figure.Figure or None, optional
        A matplotlib Figure in which to place the plots.
        If passed, its dimensions and axes will be overridden.

    Examples
    --------
    Plot the Rabi oscillations of a single qubit with initial state
    :math:`|0\rangle` under the Hamiltonian :math:`H = \omega \sigma_x`. ::

        import matplotlib.pyplot as plt
        import numpy as np
        import boulderopal as bo
        from qctrlvisualizer import plot_population_dynamics

        graph = bo.Graph()

        omega = 2 * np.pi * 0.5e6  # rad/s
        duration = 2e-6  # s

        hamiltonian = graph.constant_pwc_operator(
            duration, omega * graph.pauli_matrix("X")
        )

        sample_times = np.linspace(0.0, duration, 100)

        unitaries = graph.time_evolution_operators_pwc(
            hamiltonian=hamiltonian, sample_times=sample_times, name="unitaries"
        )

        initial_state = graph.fock_state(2, 0)[:, None]
        evolved_states = unitaries @ initial_state
        evolved_states.name = "states"

        result = bo.execute_graph(graph=graph, output_node_names=["states"])
        states = result["output"]["states"]["value"]

        qubit_populations = np.abs(states.squeeze()) ** 2

        plot_population_dynamics(
            sample_times=sample_times,
            populations={rf"$|{k}\rangle$": qubit_populations[:, k] for k in [0, 1]},
        )


    .. plot::

        import json
        import matplotlib.pyplot as plt
        import numpy as np
        from qctrlcommons.serializers import decode
        from qctrlvisualizer import plot_population_dynamics

        duration = 2e-6
        sample_times = np.linspace(0.0, duration, 100)

        with open("../docs/plot_data/populations/plot_population_dynamics.json") as file:
            qubit_populations = decode(json.load(file))

        plot_population_dynamics(
            sample_times=sample_times,
            populations={rf"$|{k}\rangle$": qubit_populations[:, k] for k in [0, 1]},
        )
        plt.tight_layout()
    """
    figure = create_figure(figure)
    population_data = _create_population_data(sample_times, populations)

    axes = figure.subplots(nrows=1, ncols=1)
    assert isinstance(axes, Axes)

    scale, prefix = get_units(sample_times)
    for data in population_data:
        axes.plot(sample_times / scale, data.values, label=data.label)

    axes.set_xlabel(f"Time ({prefix}s)")
    axes.set_ylabel("Probability")

    axes.legend()


class _PopulationData(NamedTuple):
    values: np.ndarray
    label: str


def _create_population_data(
    sample_times: np.ndarray,
    populations: dict,
) -> list[_PopulationData]:
    """
    Validate inputs and create a list of _PopulationData objects.

    Parameters
    ----------
    sample_count : np.ndarray
        The times at which the populations have been sampled.
    populations : dict
        The populations to plot.

    Returns
    -------
    list[_PopulationData]
        A list of _PopulationData.
    """
    check_argument(
        isinstance(sample_times, np.ndarray) and len(sample_times.shape) == 1,
        "The sample times must be a 1D array.",
        extras={"sample_times": sample_times},
    )
    check_argument(
        isinstance(populations, dict),
        "The populations must be a dictionary.",
        extras={"type(populations)": type(populations)},
    )

    sample_count = len(sample_times)

    plot_data = []
    for label, pop in populations.items():
        check_argument(
            isinstance(pop, (list, np.ndarray)),
            "Each element in the dictionary of populations must be an array or a list.",
            extras={f"populations['{label}']": pop},
        )
        check_argument(
            not safe_less_than(np.asarray(pop), 0) and (not safe_greater_than(np.asarray(pop), 1)),
            "Population values must lie between 0 and 1.",
            extras={f"populations['{label}']": pop},
        )
        check_argument(
            len(pop) == sample_count,
            "The number of population values must match the number of sample times.",
            extras={
                f"len(populations['{label}'])": len(pop),
                "len(sample_times)": sample_count,
            },
        )
        plot_data.append(_PopulationData(np.asarray(pop), label))

    return plot_data


@qctrl_style()
def plot_population_distributions(
    populations: dict[str, np.ndarray],
    basis_labels: list[str] | None = None,
    rotate_x_axis_labels: bool = False,
    show_legend: bool = True,
    *,
    figure: Figure | None = None,
):
    """
    Create a bar graph of the given population distributions.

    Parameters
    ----------
    populations : dict[str, np.ndarray]
        A dictionary of the 1D arrays specifying the populations of the form
        `{"populations_1": np.array([1, 0, ...]), "populations_2": np.array([0, 1, ...]), ...}`.
        The keys of the dictionary will be used for the plot legend. The values of the dictionary
        must be NumPy arrays of the same length.
    basis_labels : list(str) or None, optional
        A list of strings representing the labels of the computational basis states.
        The elements of this list will be used as the labels for the x-axis. Its length must
        match the length of the arrays in `populations`. Defaults to `["|0⟩", "|1⟩", ...]`.
    rotate_x_axis_labels : bool, optional
        Whether to rotate the labels of the x-axis by 90 degrees. Defaults to False.
    show_legend : bool, optional
        Whether to add a legend to the plot. Defaults to True.
    figure : matplotlib.figure.Figure or None, optional
        A matplotlib Figure in which to place the plots.
        If passed, its dimensions and axes will be overridden.

    Examples
    --------
    Plot the population distributions of two qutrit states. ::

        import numpy as np
        from qctrlvisualizer import plot_population_distributions

        populations = {
            "Measured": np.array([0.4, 0.15, 0.45]),
            "Simulated": np.array([0.5, 0.0, 0.5]),
        }

        plot_population_distributions(populations)


    .. plot::

        import matplotlib.pyplot as plt
        import numpy as np
        from qctrlvisualizer import plot_population_distributions

        populations = {
            "Measured": np.array([0.4, 0.15, 0.45]),
            "Simulated": np.array([0.5, 0.0, 0.5]),
        }

        plot_population_distributions(populations)
        plt.tight_layout()
    """
    figure = create_figure(figure)
    dimension = _validate_populations(populations)
    basis_labels = _validate_basis_labels(basis_labels, dimension)

    axes = figure.subplots(nrows=1, ncols=1)
    assert isinstance(axes, Axes)

    default_bar_width = 0.8
    bar_width = default_bar_width / len(populations)

    x_axis = np.arange(dimension)

    for vector_number, (vector_label, population) in enumerate(populations.items()):
        axes.bar(
            x_axis + vector_number * bar_width,
            population,
            width=bar_width,
            label=vector_label,
        )

    if rotate_x_axis_labels:
        rotation = 90
    else:
        rotation = 0
    axes.set_xticks(
        x_axis + bar_width * (len(populations) - 1) / 2,
        basis_labels,
        rotation=rotation,
    )
    axes.set_xlabel("Basis state")
    axes.set_ylabel("Probability")
    if show_legend:
        axes.legend(loc="upper left", bbox_to_anchor=(1, 1))


def _validate_populations(populations: dict[str, np.ndarray]) -> int:
    """
    Validate the input `populations` and compute the dimension of the Hilbert space.
    """
    check_argument(
        isinstance(populations, dict),
        "The input populations must be in a dictionary.",
        extras={"type(populations)": type(populations)},
    )

    for label, single_population in populations.items():
        check_argument(
            isinstance(label, str),
            "The population labels must be strings.",
            extras={"label": label},
        )

        check_argument(
            isinstance(single_population, np.ndarray) and len(single_population.shape) == 1,
            "The populations must be 1D NumPy arrays.",
            extras={f"populations['{label}']": single_population},
        )

        check_argument(
            all(np.isreal(single_population)),
            "The population values must be real numbers.",
            extras={f"populations['{label}']": single_population},
        )

        check_argument(
            not safe_less_than(np.asarray(single_population), 0)
            and (not safe_greater_than(np.asarray(single_population), 1)),
            "The population values must lie between 0 and 1.",
            extras={f"populations['{label}']": single_population},
        )

        norm = np.sqrt(np.sum(single_population))
        if not np.isclose(norm, 1):
            warnings.warn(
                f'The "{label}" state is not normalized, '
                f"norm({label})={norm}. "
                "Plotting provided populations corresponding to unnormalized vector.",
                UserWarning,
                stacklevel=2,
            )

        if np.isclose(norm, 0):
            warnings.warn(f'The "{label}" state is the zero vector.', UserWarning, stacklevel=2)

    iter_populations = iter(populations.values())
    dimension = len(next(iter_populations))
    check_argument(
        all(len(single_population) == dimension for single_population in iter_populations),
        "All provided populations must have the same dimension.",
    )

    return dimension


def _validate_basis_labels(basis_labels: list[str] | None, dimension) -> list[str]:
    """
    Validate the input `basis_labels` if passed and set to default if not.
    """
    if basis_labels is None:
        basis_labels = [rf"$|{i}\rangle$" for i in range(dimension)]
    else:
        check_argument(
            isinstance(basis_labels, list)
            and all(isinstance(label, str) for label in basis_labels),
            "The basis labels must be a list of strings.",
            extras={"basis_labels": basis_labels},
        )

        check_argument(
            dimension == len(basis_labels),
            "The length of basis_labels must coincide with the length of the population arrays.",
            extras={
                "populations dimension": dimension,
                "len(basis_label)": len(basis_labels),
            },
        )

    return basis_labels
