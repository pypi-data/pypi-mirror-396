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
Top-level package for the Q-CTRL Visualizer.

The public API of this package consists only of the objects exposed through this top-level package.
Direct access to sub-modules is not officially supported, so may be affected by
backwards-incompatible changes without notice.
"""

from .bloch import (
    display_bloch_sphere,
    display_bloch_sphere_from_bloch_vectors,
    display_bloch_sphere_from_density_matrices,
)
from .confidence_ellipses import (
    confidence_ellipse_matrix,
    plot_confidence_ellipses,
)
from .controls import (
    plot_controls,
    plot_sequences,
)
from .cost_histories import plot_cost_histories
from .density_matrix import plot_density_matrix
from .filter_functions import plot_filter_functions
from .histogram import plot_bitstring_probabilities_histogram
from .populations import (
    plot_population_distributions,
    plot_population_dynamics,
)
from .style import (
    QCTRL_DIVERGENT_COLORMAP,
    QCTRL_SEQUENTIAL_COLORMAP,
    QCTRL_STYLE_COLORS,
    get_qctrl_style,
)
from .wigner_function import plot_wigner_function

__all__ = [
    "QCTRL_DIVERGENT_COLORMAP",
    "QCTRL_SEQUENTIAL_COLORMAP",
    "QCTRL_STYLE_COLORS",
    "confidence_ellipse_matrix",
    "display_bloch_sphere",
    "display_bloch_sphere_from_bloch_vectors",
    "display_bloch_sphere_from_density_matrices",
    "get_qctrl_style",
    "plot_confidence_ellipses",
    "plot_controls",
    "plot_cost_histories",
    "plot_density_matrix",
    "plot_filter_functions",
    "plot_population_dynamics",
    "plot_population_distributions",
    "plot_bitstring_probabilities_histogram",
    "plot_sequences",
    "plot_wigner_function",
]

__version__ = "10.0.0"
