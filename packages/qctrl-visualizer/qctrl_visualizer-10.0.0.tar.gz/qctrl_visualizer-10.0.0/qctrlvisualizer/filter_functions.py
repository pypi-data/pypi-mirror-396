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
Functions for plotting filter functions.
"""

from __future__ import annotations

import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .style import qctrl_style
from .utils import (
    check_argument,
    create_figure,
    get_units,
)


@qctrl_style()
def plot_filter_functions(
    filter_functions: dict,
    show_legend: bool = True,
    x_axis_log: bool = True,
    y_axis_log: bool = True,
    *,
    figure: Figure | None = None,
):
    r"""
    Create a plot of the specified filter functions.

    Parameters
    ----------
    filter_functions : dict
        The dictionary of filter functions to plot. The keys should be the names of the filter
        functions, and the values represent the filter functions by either a dictionary with the
        keys 'frequencies', 'inverse_powers', and optional 'uncertainties';
        or a list of samples as dictionaries with keys 'frequency', 'inverse_power',
        and optional 'inverse_power_uncertainty'.
        The frequencies must be in Hertz an the inverse powers and their uncertainties in seconds.
        If the uncertainty of an inverse power is provided, it must be non-negative.
    show_legend : bool, optional
        Whether to add a legend to the plot. Defaults to True.
    x_axis_log : bool, optional
        Whether the x-axis is log-scale.
        Defaults to True.
    y_axis_log : bool, optional
        Whether the y-axis is log-scale.
        Defaults to True.
    figure : matplotlib.figure.Figure or None, optional
        A matplotlib Figure in which to place the plot.
        If passed, its dimensions and axes will be overridden.

    Notes
    -----
    For dictionary input, the key 'inverse_power_uncertainties' can be used
    instead of 'uncertainties'. If both are provided then the value corresponding to
    'uncertainties' is used.
    For list of samples input, the key 'inverse_power_precision' can be used instead of
    'inverse_power_uncertainty'. If both are provided then the value corresponding to
    'inverse_power_uncertainty' is used.

    As an example, the following is valid ``filter_functions`` input ::

        filter_functions = {
            "Primitive": {
                "frequencies": [0.0, 1.0, 2.0],
                "inverse_powers": [15., 12., 3.],
                "uncertainties": [0., 0., 0.2],
            },
            "CORPSE": [
                {"frequency": 0.0, "inverse_power": 10.},
                {"frequency": 0.5, "inverse_power": 8.5},
                {"frequency": 1.0, "inverse_power": 5., "inverse_power_uncertainty": 0.1},
                {"frequency": 1.5, "inverse_power": 2.5},
            ],
        }

    Examples
    --------
    Compare the filter functions of a primitive control scheme to BB1. The primitive scheme is
    sensitive to amplitude noise, whereas BB1 suppresses amplitude noise.
    The Hamiltonian of the system is

    .. math::
        H(t) = \frac{1 + \beta(t)}{2} [\Omega(t) \sigma_- + \Omega^*(t) \sigma_+] ,

    where :math:`\Omega(t)` is the time-dependent Rabi rate implementing each control scheme
    and :math:`\beta(t)` is a fractional time-dependent amplitude fluctuation process. ::

        import numpy as np
        import boulderopal as bo
        from qctrlvisualizer import plot_filter_functions

        graph = bo.Graph()

        omega_max = 2 * np.pi * 1e6  # rad/s
        frequencies = omega_max * np.logspace(-8, 0, 1000, base=10)
        sample_count = 3000

        primitive_duration = 5e-7  # s
        primitive_hamiltonian = graph.hermitian_part(
            graph.constant_pwc(omega_max, primitive_duration) * graph.pauli_matrix("M")
        )
        graph.filter_function(
            control_hamiltonian=primitive_hamiltonian,
            noise_operator=primitive_hamiltonian,
            frequencies=frequencies,
            sample_count=sample_count,
            name="Primitive",
        )

        bb1_duration = 2.5e-6  # s
        bb1_rates = omega_max * np.exp(1j * np.arccos(-1 / 4) * np.array([0, 1, 3, 3, 1]))
        bb1_hamiltonian = graph.hermitian_part(
            graph.pwc_signal(bb1_rates, bb1_duration) * graph.pauli_matrix("M")
        )
        graph.filter_function(
            control_hamiltonian=bb1_hamiltonian,
            noise_operator=bb1_hamiltonian,
            frequencies=frequencies,
            sample_count=sample_count,
            name="BB1",
        )

        filter_function_result = bo.execute_graph(
            graph=graph, output_node_names=["Primitive", "BB1"], execution_mode="EAGER"
        )["output"]

        plot_filter_functions(filter_function_result)


    .. plot::

        import json
        import matplotlib.pyplot as plt
        import numpy as np
        from qctrlcommons.serializers import decode
        from qctrlvisualizer import plot_filter_functions

        with open("../docs/plot_data/filter_functions/plot_filter_functions.json") as file:
            filter_functions = decode(json.load(file))

        plot_filter_functions(filter_functions)
        plt.tight_layout()
    """
    figure = create_figure(figure)

    check_argument(
        len(filter_functions) > 0,
        "At least one filter function must be provided.",
        extras={"len(filter_functions)": len(filter_functions)},
    )

    axes = figure.subplots(nrows=1, ncols=1)
    assert isinstance(axes, Axes)

    all_frequencies = []
    all_inverse_powers = []
    all_uncertainties = []
    for name, filter_function in filter_functions.items():
        if isinstance(filter_function, list):
            frequencies, inverse_powers, inverse_power_uncertainties = np.array(
                list(
                    zip(
                        *[
                            (
                                sample["frequency"],
                                sample["inverse_power"],
                                (
                                    sample["inverse_power_uncertainty"]
                                    if "inverse_power_uncertainty" in sample
                                    else sample.get("inverse_power_precision", 0.0)
                                ),
                            )
                            for sample in filter_function
                        ],
                    ),
                ),
            )
        else:
            check_argument(
                isinstance(filter_function, dict),
                "Each filter function must either be a list or a dictionary.",
                extras={f"filter_functions['{name}']": filter_function},
            )
            check_argument(
                ("frequencies" in filter_function) and ("inverse_powers" in filter_function),
                "Each filter function dictionary must contain `frequencies` and"
                " `inverse_powers` keys.",
                extras={f"filter_functions['{name}']": filter_function},
            )
            frequencies = np.asarray(filter_function["frequencies"])
            inverse_powers = np.asarray(filter_function["inverse_powers"])
            inverse_power_uncertainties = filter_function.get(
                "uncertainties",
                filter_function.get("inverse_power_uncertainties"),
            )
            if inverse_power_uncertainties is not None:
                inverse_power_uncertainties = np.asarray(inverse_power_uncertainties)
            else:
                inverse_power_uncertainties = np.zeros_like(frequencies)

        check_argument(
            np.all(inverse_power_uncertainties >= 0.0),
            "Inverse power uncertainties must all be non-negative.",
            extras={
                f"filter_functions['{name}']"
                "['inverse_power_uncertainties']": inverse_power_uncertainties,
            },
        )

        all_frequencies.append(frequencies)
        all_inverse_powers.append(inverse_powers)
        all_uncertainties.append(inverse_power_uncertainties)

    # Set log axes, scale units only in linear scales.
    if x_axis_log:
        axes.set_xscale("log")
        scale_x, units_x = 1.0, ""
    else:
        scale_x, units_x = get_units(np.concatenate(all_frequencies))

    if y_axis_log:
        axes.set_yscale("log")
        scale_y, units_y = 1.0, ""
    else:
        scale_y, units_y = get_units(np.concatenate(all_inverse_powers))
        if scale_y > 1.0:
            # Only scale y units if smaller than 1 (ms, µs, ns, ...).
            scale_y, units_y = 1.0, ""

    for frequencies, inverse_powers, uncertainties, name in zip(
        all_frequencies,
        all_inverse_powers,
        all_uncertainties,
        filter_functions,
    ):
        inverse_powers_upper = inverse_powers + uncertainties
        inverse_powers_lower = inverse_powers - uncertainties

        lines = axes.plot(frequencies / scale_x, inverse_powers / scale_y, label=name)
        axes.fill_between(
            frequencies / scale_x,
            inverse_powers_lower / scale_y,
            inverse_powers_upper / scale_y,
            alpha=0.35,
            hatch="||",
            facecolor="none",
            edgecolor=lines[0].get_color(),
            linewidth=0,
        )

    if show_legend:
        axes.legend()

    axes.autoscale(axis="x", tight=True)

    axes.set_xlabel(f"Frequency ({units_x}Hz)")
    axes.set_ylabel(f"Inverse power ({units_y}s)")
