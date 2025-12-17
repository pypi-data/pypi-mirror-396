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
Functions for plotting confidence ellipses.
"""

from __future__ import annotations

import numpy as np
from matplotlib.figure import Figure
from scipy.linalg import fractional_matrix_power
from scipy.special import betaincinv

from .style import (
    FIG_HEIGHT,
    QCTRL_STYLE_COLORS,
    qctrl_style,
)
from .utils import (
    check_argument,
    create_axes,
    create_figure,
    get_units,
)


@qctrl_style()
def plot_confidence_ellipses(  # noqa: PLR0913
    ellipse_matrix: np.ndarray,
    estimated_parameters: np.ndarray,
    actual_parameters: np.ndarray | None = None,
    parameter_names: list[str] | None = None,
    parameter_units: str | list[str] = "Hz",
    *,
    figure: Figure | None = None,
):
    r"""
    Create an array of confidence ellipse plots.

    From an (N,N) matrix transformation and N estimated parameters,
    plots the confidence ellipse for each pair of parameters.

    Parameters
    ----------
    ellipse_matrix : np.ndarray
        The square matrix which transforms a unit hypersphere in an
        N-dimensional space into a hyperellipse representing the confidence
        region. Must be of shape (N, N), with N > 1.
    estimated_parameters : np.ndarray
        The values of the estimated parameters. Must be of shape (N,).
    actual_parameters : np.ndarray or None, optional
        The actual values of the estimated parameters.
        If you provide these, they're plotted alongside the ellipses and
        estimated parameters. Must be of shape (N,).
    parameter_names : list[str] or None, optional
        The name of each parameter, to be used as axes labels.
        If provided, it must be of length N. If not provided,
        the axes are labelled "Parameter 0", "Parameter 1", ...
    parameter_units : str or list[str], optional
        The units of each parameter. You can provide a list of strings with
        the units of each parameter, or a single string if all parameters have
        the same units. Defaults to "Hz".
    figure : matplotlib.figure.Figure or None, optional
        A matplotlib Figure in which to place the plots.
        If passed, its dimensions and axes will be overridden.

    Examples
    --------
    Plot the confidence ellipses for a parameter estimation from a quantum system
    identification task. This can be done by using the Hessian of the cost that is
    computed during a hardware characterization. ::

        import numpy as np
        from qctrlvisualizer import plot_confidence_ellipses, confidence_ellipse_matrix

        estimated_parameters = 2 * np.pi * np.array([31.4e6, 15.2e6, 42.7e6])  # rad/s
        actual_parameters = 2 * np.pi * np.array([31.7e6, 15.1e6, 42.9e6])  # rad/s
        parameter_names = [r"$\omega_x$", r"$\omega_y$", r"$\omega_z$"]

        measurement_count = 100
        cost = 0.003
        hessian = np.array(
            [
                [1.51556e-17, 3.74200e-18, 5.83060e-18],
                [3.74200e-18, 1.18800e-18, 1.54420e-18],
                [5.83060e-18, 1.54420e-18, 2.46170e-18],
            ]
        )

        confidence_region = confidence_ellipse_matrix(hessian, cost, measurement_count)

        plot_confidence_ellipses(
            confidence_region, estimated_parameters, actual_parameters, parameter_names
        )


    .. plot::

        from qctrlvisualizer import plot_confidence_ellipses

        estimated_parameters = 2 * np.pi * np.array([31.4e6, 15.2e6, 42.7e6])  # rad/s
        actual_parameters = 2 * np.pi * np.array([31.7e6, 15.1e6, 42.9e6])  # rad/s
        parameter_names = [r"$\omega_x$", r"$\omega_y$", r"$\omega_z$"]

        confidence_region = [
            [12178362.58872402, -5536552.15978952, -14225691.40353029],
            [ -5536552.15978951, 46404614.32995261, -12470346.23090813],
            [-14225691.4035303, -12470346.23090812, 49686337.04387178],
        ]

        plot_confidence_ellipses(
            confidence_region, estimated_parameters, actual_parameters, parameter_names
        )
    """
    figure = create_figure(figure)
    ellipse_matrix = np.asarray(ellipse_matrix)
    estimated_parameters = np.asarray(estimated_parameters)
    if actual_parameters is not None:
        actual_parameters = np.asarray(actual_parameters)

    check_argument(
        len(estimated_parameters.shape) == 1 and len(estimated_parameters) > 1,
        "The estimated parameters must be a 1D array containing at least two parameters.",
        extras={"estimated_parameters.shape": estimated_parameters.shape},
    )

    parameter_count = len(estimated_parameters)

    check_argument(
        ellipse_matrix.shape == (parameter_count, parameter_count),
        "The ellipse_matrix must be a square 2D array, "
        "with the same length as the estimated parameters.",
        extras={
            "ellipse_matrix.shape": ellipse_matrix.shape,
            "len(estimated_parameters)": parameter_count,
        },
    )

    if actual_parameters is not None:
        check_argument(
            actual_parameters.shape == (parameter_count,),
            "If passed, the actual parameters must be a 1D array "
            "with the same shape as estimated parameters.",
            extras={
                "actual_parameters.shape": actual_parameters.shape,
                "estimated_parameters.shape": estimated_parameters.shape,
            },
        )

    if parameter_names is not None:
        check_argument(
            len(parameter_names) == parameter_count,
            "If passed, the parameter names must be a list "
            "with the same length as the estimated parameters.",
            extras={
                "len(parameter_names)": len(parameter_names),
                "len(estimated_parameters)": parameter_count,
            },
        )

    else:
        parameter_names = [f"Parameter {k}" for k in range(parameter_count)]

    if isinstance(parameter_units, str):
        parameter_units = [parameter_units] * parameter_count
    else:
        check_argument(
            len(parameter_units) == parameter_count,
            "The parameter units must be either a string or a list "
            "with the same length as the estimated parameters.",
            extras={
                "len(parameter_units)": len(parameter_units),
                "len(estimated_parameters)": parameter_count,
            },
        )

    # Set the N (N-1) / 2 plots in a 2D grid of axes.
    if parameter_count % 2 == 0:
        plot_count_x = parameter_count - 1
        plot_count_y = parameter_count // 2
    else:
        plot_count_x = parameter_count
        plot_count_y = (parameter_count - 1) // 2

    axes_array = create_axes(
        figure,
        plot_count_x,
        plot_count_y,
        FIG_HEIGHT,
        FIG_HEIGHT,
    ).flatten()

    # Create pairs of indices with all possible parameter pairings.
    index_1_list, index_2_list = np.triu_indices(parameter_count, k=1)

    for axes, index_1, index_2 in zip(axes_array, index_1_list, index_2_list):
        # Obtain points representing the correct parameters and their estimates.
        estimated_dot = estimated_parameters[[index_1, index_2]]

        # Obtain coordinates for a circle.
        theta = np.linspace(0, 2 * np.pi, 101)
        circle_coordinates = np.array([np.cos(theta), np.sin(theta)])

        # Define matrix that transforms circle coordinates into ellipse coordinates.
        coordinate_change = ellipse_matrix[np.ix_([index_1, index_2], [index_1, index_2])]
        ellipse = coordinate_change @ circle_coordinates + estimated_dot[:, None]
        scale_x, units_x = get_units(ellipse[0])
        scale_y, units_y = get_units(ellipse[1])
        scale = np.array([scale_x, scale_y])

        # Define labels of the axes.
        axes.set_xlabel(
            f"{parameter_names[index_1]} ({units_x}{parameter_units[index_1]})",
            labelpad=0,
        )
        axes.set_ylabel(
            f"{parameter_names[index_2]} ({units_y}{parameter_units[index_2]})",
            labelpad=0,
        )

        # Plot estimated parameters.
        estimated_dot = estimated_dot / scale
        axes.plot(
            *estimated_dot,
            "o",
            label="Estimated parameters",
            c=QCTRL_STYLE_COLORS[0],
        )

        # Plot confidence ellipse.
        ellipse = ellipse / scale[:, None]
        axes.plot(*ellipse, "--", label="Confidence region", c=QCTRL_STYLE_COLORS[0])

        # Plot actual parameters (if available).
        if actual_parameters is not None:
            actual_dot = actual_parameters[[index_1, index_2]] / scale
            axes.plot(
                *actual_dot,
                "o",
                label="Actual parameters",
                c=QCTRL_STYLE_COLORS[1],
            )

    # Create legends.
    handles, labels = axes_array[0].get_legend_handles_labels()
    figure.legend(
        handles=handles,
        labels=labels,
        loc="center",
        bbox_to_anchor=(0.5, 0.95),
        ncol=3,
    )


def confidence_ellipse_matrix(
    hessian: np.ndarray,
    cost: float,
    measurement_count: int,
    confidence_fraction: float = 0.95,
):
    r"""
    Calculate a matrix that you can use to represent the confidence region
    of parameters that you estimated. Pass to this function the Hessian of
    the residual sum of squares with respect to the parameters, and use the
    output matrix to transform a hypersphere into a hyperellipse representing
    the confidence region. You can then plot this hyperellipse to visualize the
    confidence region using the `plot_confidence_ellipses` function.

    Alternatively, you can apply a (2,2)-slice of the transformation matrix to
    a unit circle to visualize the confidence ellipse for a pair of estimated
    parameters.

    Parameters
    ----------
    hessian : np.ndarray
        The Hessian of the residual sum of squares cost with respect to the estimated parameters,
        :math:`H`.
        Must be a square matrix.
    cost : float
        The residual sum of squares of the measurements with respect to the actual measurements,
        :math:`C_\mathrm{RSS}`.
        Must be positive.
    measurement_count : int
        The number of measured data points, :math:`n`.
        Must be positive.
    confidence_fraction : float, optional
        The confidence fraction for the ellipse, :math:`\alpha`.
        If provided, must be between 0 and 1.
        Defaults to 0.95.

    Returns
    -------
    np.ndarray
        A :math:`(p, p)`-matrix which transforms a unit hypersphere in a p-dimensional
        space into a hyperellipse representing the confidence region for the
        confidence fraction :math:`\alpha`. Here :math:`p` is the dimension of the Hessian matrix.

    Notes
    -----
    From the Hessian matrix of the residual sum of squares with respect
    to the estimated parameters :math:`\{\lambda_i\}`,

    .. math::
        H_{ij} = \frac{\partial^2 C_\mathrm{RSS}}{\partial \lambda_i \partial \lambda_j} ,

    we can estimate the covariance matrix for the estimated parameters

    .. math::
        \Sigma = \left( \frac{n-p}{2 C_\mathrm{RSS}} H \right)^{-1}  .

    Finally, we can find a scaling factor :math:`z`, such that the matrix :math:`z \Sigma^{1/2}`
    transforms the coordinates of a unit hypersphere in a p-dimensional space into a
    hyperellipse representing the confidence region

    .. math::
        z = \sqrt{p F_{1-\alpha} \left( \frac{n-p}{2}, \frac{p}{2} \right)} ,

    where :math:`F_{1-\alpha}(a,b)` is the point of the `F-distribution
    <https://en.wikipedia.org/wiki/F-distribution>`_ where the probability in
    the tail is equal to :math:`F_{1-\alpha}(a,b)`.

    For more details, see the topic
    `Characterizing your hardware using system identification in Boulder Opal
    <https://docs.q-ctrl.com/boulder-opal/topics/characterizing-your-hardware-using-system-identification-in-boulder-opal>`_
    and `N. R. Draper and I. Guttman, The Statistician 44, 399 (1995)
    <https://doi.org/10.2307/2348711>`_.
    """
    parameter_count = hessian.shape[0]

    check_argument(
        hessian.shape == (parameter_count, parameter_count),
        "Hessian must be a square matrix.",
        extras={"hessian.shape": hessian.shape},
    )

    check_argument(cost > 0, "The cost must be positive.", extras={"cost": cost})

    check_argument(
        measurement_count > 0,
        "The number of measurements must be positive.",
        extras={"measurement_count": measurement_count},
    )

    check_argument(
        0 < confidence_fraction < 1,
        "The confidence fraction must be between 0 and 1.",
        extras={"confidence_fraction": confidence_fraction},
    )

    # Estimate covariance matrix from the Hessian.
    covariance_matrix = np.linalg.inv(
        0.5 * hessian * (measurement_count - parameter_count) / cost,
    )

    # Calculate scaling factor for the confidence region.
    iibeta = betaincinv(
        (measurement_count - parameter_count) / 2,
        parameter_count / 2,
        1 - confidence_fraction,
    )
    inverse_cdf = (measurement_count - parameter_count) / parameter_count * (1 / iibeta - 1)
    scaling_factor = np.sqrt(parameter_count * inverse_cdf)

    # Calculate confidence region for the confidence fraction.
    return scaling_factor * fractional_matrix_power(covariance_matrix, 0.5)
