"""
Module `catenary`

Provides low-level catenary-based mechanical models for overhead conductors.

This module is responsible for the geometric and physical behavior of a
conductor modeled as a perfectly flexible catenary under uniform load.
It is intentionally independent from regulatory assumptions, hypotheses,
or load-case management.

Higher-level logic such as mechanical zones, hypotheses, and ITC-LAT 07
compliance is handled in the `mech` module.

Classes:
    CatenaryState:
        Represents a mechanical state of the conductor, defined by
        temperature, horizontal tension, and apparent weight per unit length.

    CatenaryApparentLoad:
        Represents the combined apparent load acting on the conductor due
        to wind and vertical loads (bare weight + ice).

    CatenaryModel:
        Encapsulates catenary equations, including:
        - Change-of-state (COS) calculations
        - Mid-span sag computation for a given mechanical state and span

Notes:
    - Tension is expressed as horizontal tension (daN).
    - Loads and weights are expressed in daN/m.
    - Sag is computed at mid-span using the exact catenary equation
      (not a parabolic approximation).
"""


import math
from dataclasses import dataclass

from .utils import find_root
from .conductor import Conductor


@dataclass
class CatenaryState:
    """Represents the mechanical state of a conductor catenary.

    Attributes:
        temp (float): Conductor temperature in degrees Celsius.
        tense (float): Horizontal tension in the conductor (daN).
        weight (float): Permanent weight per unit length (daN/m), including any ice or additional loads.
    """

    temp: float
    tense: float
    weight: float


@dataclass
class CatenaryApparentLoad:
    """Represents the apparent (combined) load due to wind, ice and weight.

    Attributes:
        wind_load: Horizontal load component from wind (daN/m).
        vertical_load: Vertical load component (bare + ice) (daN/m).
    """
    wind_load: float
    vertical_load: float

    @property
    def resultant(self):
        """Returns the magnitude of resultant load vector."""
        return math.sqrt(self.wind_load ** 2 + self.vertical_load **2)

    @property
    def swing_angle(self):
        """Returns the swing angle in radians.

        Swing angle is the angle formed between the conductor’s resultant load
        vector and the vertical direction.
        """
        return math.atan2(self.wind_load, self.vertical_load)

    def __str__(self):
        """Return a readable string representation of the load."""
        return f"CatenaryApparentLoad(wind_load={self.wind_load}, vertical_load={self.vertical_load}) daN/m"

    
class CatenaryModel:
    """Represents a conductor as a catenary to understand its mechanical properties."""

    def __init__(self, conductor: Conductor) -> None:
        """Initialize the catenary model for a specific conductor.

        Args:
            conductor: The conductor object containing material and geometric properties.
        """
        self.conductor = conductor

    def cos(self, state0: CatenaryState, temp1: float, weight1: float, span: float) -> CatenaryState:
        """Perform a change of state (COS) for a catenary.

        Computes the new tension of the conductor when moving from an initial
        state to a new temperature and weight over a given span. This implements
        the standard catenary change-of-state equations used in sag-tension
        analysis.

        Args:
            state0: Initial catenary state (temperature, tension, and weight).
            temp1: Target temperature of the conductor (°C).
            weight1: Target conductor weight (daN/m), including ice if present.
            span: Span length between supports (m).

        Returns:
            CatenaryState: New state of the conductor at the target temperature
            and weight, including the recalculated horizontal tension.
        """

        def coseq(tense1: float) -> float:
            """Catenary equation for root finding: returns residual for a given horizontal tension."""

            temperature_factor = self.conductor.thermal_exp_factor * (temp1 - state0.temp)
            strength_factor = (tense1 - state0.tense) / (self.conductor.total_area * self.conductor.elastic_modulus)
            arc_length1_factor = (state0.tense / state0.weight) * math.sinh(span * state0.weight / (2 * state0.tense))
            arc_length2_factor = (tense1 / weight1) * math.sinh(span * weight1 / (2 * tense1))

            return temperature_factor + strength_factor - arc_length2_factor / arc_length1_factor + 1

        def cos_prime(tense1: float) -> float:
            """Derivative of the catenary residual function with respect to horizontal tension."""

            arc_length_state1 = (state0.tense / state0.weight) * math.sinh(span * state0.weight / (2 * state0.tense))
            span_times_weight2 = span * weight1
            return 1 / (self.conductor.total_area * self.conductor.elastic_modulus) + (1 / (weight1 * arc_length_state1)) * ((span_times_weight2 / (2 * tense1)) * math.cosh(span_times_weight2 / (2 * tense1)) - math.sinh(span_times_weight2 / (2 * tense1)))

        tense1 = find_root(coseq, cos_prime, state0.tense)
        return CatenaryState(temp=temp1, weight=weight1, tense=tense1)

    def sag(self, state: CatenaryState, span: float):
        """Compute the mid-span sag using the catenary equation.

        Calculates the vertical sag at mid-span for a conductor modeled as a
        perfectly flexible catenary under uniform apparent load. The sag is
        computed from the horizontal tension and apparent weight per unit length
        stored in the given mechanical state.

        Args:
            state (CatenaryState): Mechanical state of the catenary, containing:
                - temperature of the catenary
                - horizontal tension (daN)
                - apparent weight per unit length (daN/m)
            span (float): Span length between supports (m).

        Returns:
            float: Mid-span sag of the conductor (m).
        """
        catparam = state.tense / state.weight
        return catparam * (math.cosh(span / (2 * catparam)) - 1)


