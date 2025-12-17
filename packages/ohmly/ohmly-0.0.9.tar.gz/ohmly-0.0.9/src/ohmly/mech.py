"""
Module `mech`

Mechanical analysis tools for overhead conductors, including:

-   Zone-based conductor properties (altitude-dependent ice loads)
-   Every-Day Stress (EDS) and Cold-Hour Stress (CHS) calculations
-   Apparent load computation under wind and ice
-   Ruling span calculation
-   Sag-tension analysis based on hypotheses

Classes:
-   MechAnalysisZone: Altitude-based mechanical analysis zone.
-   MechAnalysisHypothesis: Represents a single scenario for mechanical analysis.
-   MechAnalysis: Performs mechanical analysis for a conductor in a given zone.
-   SagTensionAnalyzer: Generates sag-tension tables and identifies controlling hypotheses.
-   SagTensionTable: Stores results of sag-tension analysis.
-   SagTensionTableRow(TypedDict): Represents a row in a sag-tension table.

Notes:
-   Tensions are in daN, weights in daN/m.
-   The controlling hypothesis is the scenario whose calculated tension does not
    exceed allowable limits in any evaluated scenario.
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import TypedDict

from rich.table import Table
from rich.console import Console
from rich import box

from .conductor import Conductor
from .catenary import CatenaryModel, CatenaryState, CatenaryApparentLoad


class MechAnalysisZone(Enum):
    """Mechanical analysis zone based on altitude."""

    A = (0, "Below 500 m")
    B = (1, "Between 500 and 1000 m")
    C = (2, "Above 1000 m")

    def __init__(self, _, description):
        """Initializes the zone with a description.

        Args:
            description: Human-readable description of the zone.
        """
        self.description = description


@dataclass
class MechAnalysisHypothesis:
    """Represents a single hypothesis (scenario) for mechanical analysis.

    Attributes:
        temp (float): Conductor temperature (°C).
        rts_factor (float): Fraction of conductor rated strength to use.
        zone (MechAnalysisZone | None): Optional mechanical analysis zone.
        wind_speed (float): Wind speed in km/h.
        with_ice (bool): Whether ice is present.
        name (str | None): Optional descriptive name for the hypothesis.
    """

    temp: float
    rts_factor: float
    zone: MechAnalysisZone | None = None
    wind_speed: float = 0.
    with_ice: bool = False
    name: str | None = None


class SagTensionTableRow(TypedDict):
    """Represents a row in a sag-tension table.

    Attributes:
        span (float): Span length between supports (m).
        results (list[tuple[float, float]]): Calculated tensions (daN) and
            corresponding percentage of rated strength for each hypothesis.
    """

    span: float
    results: list[tuple[float, float]]


@dataclass
class SagTensionTable:
    """Stores sag-tension analysis results for multiple hypotheses and spans.

    Attributes:
        hypos (list[MechAnalysisHypothesis]): List of evaluated hypotheses.
        rows (list[SagTensionTableRow]): Computed results per span.
    """

    hypos: list[MechAnalysisHypothesis] = field(default_factory=list)
    rows: list[SagTensionTableRow] = field(default_factory=list)

    def __str__(self) -> str:
        table = Table(box=box.SIMPLE_HEAVY)

        table.add_column("Span", justify="right")

        for hypo in self.hypos:
            col_name = f"{hypo.name}\nT (daN), RTS (%)" if hypo.name else "T (daN), RTS (%)"
            table.add_column(col_name, justify="center")

        for row in self.rows:
            span = str(row["span"])

            # The first tuple value is the tense and the second is the percentage of rts
            values = [
                f"{row['results'][i][0]:.4f}, {row['results'][i][1]:.4f}"
                for i in range(len(self.hypos))
            ]
            
            table.add_row(span, *values)

        console = Console()
        with console.capture() as capture:
            console.print(table)
        return capture.get()

    def __repr__(self) -> str:
        return f"SagTensionTable(hypos={self.hypos}, rows={self.rows})"


class MechAnalysis:
    """Performs mechanical analysis of a conductor for a given zone.

    Provides methods for Every-Day Stress (EDS), Cold-Hour Stress (CHS),
    overload calculations, ruling span, and sag-tension tables.
    """

    def __init__(self, conductor: Conductor, zone: MechAnalysisZone):
        """Initializes the mechanical analysis.

        Args:
            conductor: Conductor object with material and geometric properties.
            zone: Mechanical analysis zone (altitude-dependent).
        """

        self.conductor = conductor
        self.cat = CatenaryModel(conductor)
        self.zone = zone
    
    @property
    def ice_weight(self) -> float:
        """Compute ice load per unit length (daN/m) based on the analysis zone.

        Raises:
            ValueError: If ice is undefined for the zone (zone A).

        Returns:
            float: Ice weight per meter of conductor.
        """

        if self.zone == MechAnalysisZone.A:
            raise ValueError("Ice weight is undefined for zone A (no ice per the norm)")
        if self.zone == MechAnalysisZone.B:
            return 0.18 * math.sqrt(self.conductor.overall_diameter)
        return 0.36 * math.sqrt(self.conductor.overall_diameter)

    def eds(self, with_dampers: bool = False) -> CatenaryState:
        """Computes Every-Day Stress (EDS) conditions for the conductor.

        Args:
            with_dampers: If True, includes the effect of dampers.

        Returns:
            CatenaryState: Conductor state with temperature, tension, and weight.
        """

        max_tense = 0.15 * self.conductor.rated_strength
        if with_dampers: max_tense = 0.22 * self.conductor.rated_strength

        return CatenaryState(temp=15, tense=max_tense, weight=self.conductor.unit_weight)

    def chs(self, temp: float, rts_factor: float) -> CatenaryState:
        """Computes Cold-Hour Stress (CHS) conditions for the conductor.

        Args:
            temp: Conductor temperature (°C).
            rts_factor: Fraction of conductor rated strength to use.

        Returns:
            CatenaryState: Conductor state at the given temperature and tension.
        """

        return CatenaryState(temp, tense = rts_factor * self.conductor.rated_strength, weight=self.conductor.unit_weight)

    def overload(self, wind_speed: float = 0.0, with_ice: bool = False, pressure_factor: float = 1.0):
        """Compute the apparent load on the conductor due to wind and ice.

        Calculates the horizontal wind load and vertical permanent load acting on
        the conductor, following ITC-LAT 07 assumptions. Wind pressure depends on
        wind speed and effective conductor diameter, which may increase due to ice
        accretion. An optional pressure factor allows scaling the wind pressure
        (e.g. for safety factors or special load cases).

        Args:
            wind_speed (float): Wind speed in km/h.
            with_ice (bool): Whether ice is present.
            pressure_factor (float): Multiplicative factor applied to the wind
            pressure. Use values > 1.0 to increase wind load (e.g. safety
            margins or exceptional conditions).

        Returns:
            CatenaryApparentLoad: Resulting apparent load, containing:
            - horizontal wind load (daN/m)
            - vertical (weight + ice) load (daN/m)
        """

        wind_velocity_factor = (wind_speed / 120) ** 2  # this is in daN/m^2

        conductor_diameter = self.conductor.overall_diameter * 1e-3  # We need this in meters, not millimeters.

        total_diameter = conductor_diameter
        if with_ice:
            total_diameter = math.sqrt((4 * self.ice_weight / (750 * math.pi)) + conductor_diameter ** 2)

        wind_pressure = 60 * wind_velocity_factor
        if total_diameter > 16 * 1e-3:
            wind_pressure = 50 * wind_velocity_factor

        wind_load = wind_pressure * pressure_factor * total_diameter
        vertical_load = self.conductor.unit_weight 
        if with_ice:
            vertical_load += self.ice_weight

        return CatenaryApparentLoad(wind_load, vertical_load)

    def overload_factor(self, apparent_load: CatenaryApparentLoad) -> float:
        """Returns the ratio of resultant load to the conductor's weight.

        Args:
            apparent_load: Apparent load including wind and ice.

        Returns:
            float: Overload factor (dimensionless).
        """

        return apparent_load.resultant / self.conductor.unit_weight

    def ruling_span(self, spans: list[float | int]) -> float:
        """Computes the ruling span for a set of spans.

        Args:
            spans: List of span lengths (m).

        Returns:
            float: Ruling span (m), weighted by cube of individual spans.
        """
        
        return math.sqrt(sum(pow(span, 3) for span in spans) / sum(spans))

    def stt(
            self,
            hypos: list[MechAnalysisHypothesis],
            spans: list[float] | list[int]
    ) -> SagTensionTable | None:
        """Generate a sag-tension table for a set of spans and hypotheses.

        Args:
            hypos (list[MechAnalysisHypothesis]): Hypotheses to evaluate.
            spans (list[float] | list[int]): List of spans (m).

        Returns:
            SagTensionTable | None: Table with sag-tension results, or None if no controlling state is found.
        """
        sta = SagTensionAnalyzer(self, hypos)
        return sta.tbl(spans)


class SagTensionAnalyzer:
    """Generates sag-tension tables and finds controlling mechanical states."""

    def __init__(self, mech: MechAnalysis, hypotheses: list[MechAnalysisHypothesis]) -> None:
        """Initialize the sag-tension analyzer.

        Args:
            mech: Mechanical analysis object for the conductor.
            hypotheses: List of scenarios to evaluate.
        """
        self.mech = mech
        self.hypotheses = hypotheses

    def find_controlling_state(self, span: float | int) -> MechAnalysisHypothesis | None:
        """Find the hypothesis that controls the conductor tension for a span.

        Iteratively checks all hypotheses and returns the first one that does
        not violate allowable tension in any scenario.

        Args:
            span: Span length between supports (m).

        Returns:
            MechAnalysisHypothesis or None: Controlling hypothesis, if found.
        """

        sorted_hypos = sorted(self.hypotheses, key=lambda h: h.temp)
        for i, base_hypo in enumerate(sorted_hypos):

            base_overload = self.mech.overload(wind_speed=base_hypo.wind_speed, with_ice=base_hypo.with_ice)
            base_case = CatenaryState(temp=base_hypo.temp, weight=base_overload.resultant, tense=self.mech.conductor.rated_strength * base_hypo.rts_factor)

            violation_found = False
            for j, hypo in enumerate(sorted_hypos):
                if j == i:
                    continue
                overload = self.mech.overload(wind_speed=hypo.wind_speed, with_ice=hypo.with_ice)
                state1 = self.mech.cat.cos(state0=base_case, temp1=hypo.temp, weight1=overload.resultant, span=span)

                allowed_tense = hypo.rts_factor * self.mech.conductor.rated_strength
                if state1.tense >= allowed_tense:
                    violation_found = True
                    break
                
            if not violation_found:
                return base_hypo

        return None

    def tbl(self, spans: list[float] | list[int]) -> SagTensionTable | None:
        """Generate a sag-tension table for a list of spans.

        Computes tension and RTS (%) for each hypothesis and span.

        Args:
            spans (list[float] | list[int]): List of spans to compute (m).

        Returns:
            SagTensionTable | None: Table of results or None if no controlling state is found.
        """

        tbl = SagTensionTable(hypos=self.hypotheses)

        for span in spans:
            controller = self.find_controlling_state(span)
            if not controller:
                return None

            base_overload = self.mech.overload(wind_speed=controller.wind_speed, with_ice=controller.with_ice)
            base_state = CatenaryState(temp=controller.temp, weight=base_overload.resultant, tense=self.mech.conductor.rated_strength * controller.rts_factor)

            row: SagTensionTableRow = {"span": span, "results": []}

            for hypo in self.hypotheses:
                load = self.mech.overload(wind_speed=hypo.wind_speed, with_ice=hypo.with_ice)
                state1 = self.mech.cat.cos(state0=base_state, temp1=hypo.temp, weight1=load.resultant, span=span)
                
                row["results"].append((state1.tense, state1.tense / self.mech.conductor.rated_strength * 100))

            tbl.rows.append(row)

        return tbl

