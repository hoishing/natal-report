"""
Module for generating detailed astrological reports in PDF format.

The module handles creation of astrological reports including birth data, elements,
modalities, polarities, hemispheres, quadrants, signs, houses, and celestial bodies.
The report is created using the natal astrology library and rendered as HTML, then
converted to PDF.
"""

from collections import defaultdict
from importlib.resources import files
from io import BytesIO
from natal import Chart, Config, Data, Stats
from natal.config import Orb
from natal.const import (
    ASPECT_MEMBERS,
    ELEMENT_MEMBERS,
    EXTRA_MEMBERS,
    MODALITY_MEMBERS,
    PLANET_MEMBERS,
    SIGN_MEMBERS,
    VERTEX_MEMBERS,
)
from natal.stats import StatData, dignity_of
from pathlib import Path
from tagit import div, main, style, svg, table, td, tr
from typing import Iterable
from weasyprint import HTML

type Grid = list[Iterable[str | int]]
ELEMENTS = [ELEMENT_MEMBERS[i] for i in (0, 2, 3, 1)]
TEXT_COLOR = "#595959"
symbol_name_map = {
    asp.symbol: asp.name
    for asp in (PLANET_MEMBERS + EXTRA_MEMBERS + VERTEX_MEMBERS + ASPECT_MEMBERS)
}


class Report:
    """
    Generates an astrological report based on provided data.

    Args:
        data1: The primary data for the report.
        data2: The secondary data for the report.
    """

    def __init__(
        self,
        data1: Data,
        data2: Data | None = None,
        city1: str | None = None,
        city2: str | None = None,
        tz1: str | None = None,
        tz2: str | None = None,
    ):
        """
        Initialize report with birth data.

        Args:
            data1: Primary birth data for the report.
            data2: Optional secondary birth data for comparison.
            city1: City name for the primary birth data.
            city2: City name for the secondary birth data.
            tz1: Timezone for the primary birth data.
            tz2: Timezone for the secondary birth data.
        """
        self.data1: Data = data1
        self.data2: Data | None = data2
        self.city1: str | None = city1
        self.city2: str | None = city2
        self.tz1: str | None = tz1
        self.tz2: str | None = tz2

    @property
    def basic_info_with_city(self) -> Grid:
        """
        Generate basic birth information including city and timezone.

        Returns:
            Grid containing name, city, and birth date/time for each person.
        """
        time_fmt = "%Y-%m-%d %H:%M"
        dt1 = self.data1.utc_dt.astimezone(self.tz1).strftime(time_fmt)
        output = [["name", "city", "birth"]]
        output.append([self.data1.name, self.city1, dt1])
        if self.data2:
            dt2 = self.data2.utc_dt.astimezone(self.tz2).strftime(time_fmt)
            output.append([self.data2.name, self.data2.city, dt2])
        return list(zip(*output))

    @property
    def basic_info(self) -> Grid:
        """
        Generates basic information about the provided data.

        Returns:
            Grid containing name, coordinates, and birth date/time.
        """
        time_fmt = "%Y-%m-%d %H:%M"
        dt1 = self.data1.utc_dt.strftime(time_fmt)
        coordinates1 = f"{self.data1.lat}°N {self.data1.lon}°E"
        output = [["name", "location", "UTC time"]]
        output.append([self.data1.name, coordinates1, dt1])
        if self.data2:
            dt2 = self.data2.utc_dt.strftime(time_fmt)
            coordinates2 = f"{self.data2.lat}°N {self.data2.lon}°E"
            output.append([self.data2.name, coordinates2, dt2])
        return list(zip(*output))

    @property
    def element_vs_modality(self) -> Grid:
        """
        Generate a grid comparing elements and modalities.

        Returns:
            Grid comparing elements and modalities.
        """
        aspectable1 = self.data1.aspectables
        element_symbols = [svg_of(ele.name) for ele in ELEMENTS]
        grid = [[""] + element_symbols + ["sum"]]
        element_count = defaultdict(int)
        for modality in MODALITY_MEMBERS:
            row = [svg_of(modality.name)]
            modality_count = 0
            for element in ELEMENTS:
                count = 0
                symbols = ""
                for body in aspectable1:
                    if (
                        body.sign.element == element.name
                        and body.sign.modality == modality.name
                    ):
                        symbols += svg_of(body.name)
                        count += 1
                        element_count[element.name] += 1
                row.append(symbols)
                modality_count += count
            row.append(modality_count)
            grid.append(row)
        grid.append(
            ["sum"] + list(element_count.values()) + [sum(element_count.values())]
        )
        grid.append(
            [
                "◐",
                f"null:{element_count['fire'] + element_count['air']} pos",
                f"null:{element_count['water'] + element_count['earth']} neg",
                "",
            ]
        )
        return grid

    @property
    def quadrants_vs_hemisphere(self) -> Grid:
        """
        Generate a grid comparing quadrants and hemispheres.

        Returns:
            Grid comparing quadrants and hemispheres.
        """
        q = self.data1.quadrants
        first_q = [svg_of(body.name) for body in q[0]]
        second_q = [svg_of(body.name) for body in q[1]]
        third_q = [svg_of(body.name) for body in q[2]]
        forth_q = [svg_of(body.name) for body in q[3]]
        hemi_symbols = ["←", "→", "↑", "↓"]
        grid = [[""] + hemi_symbols[:2] + ["sum"]]
        grid += [["↑"] + [forth_q, third_q] + [len(q[3] + q[2])]]
        grid += [["↓"] + [first_q, second_q] + [len(q[3] + q[2])]]
        grid += [
            ["sum"]
            + [len(q[3] + q[0]), len(q[1] + q[2])]
            + [len(q[0] + q[1] + q[2] + q[3])]
        ]
        return grid

    @property
    def signs(self) -> Grid:
        """
        Generate a grid of signs and their corresponding bodies.

        Returns:
            Grid of signs and their corresponding bodies.
        """
        grid = [["sign", "bodies", "sum"]]
        for sign in SIGN_MEMBERS:
            bodies = [
                svg_of(b.name)
                for b in self.data1.aspectables
                if b.sign.name == sign.name
            ]
            grid.append([svg_of(sign.name), "".join(bodies), len(bodies) or ""])
        return grid

    @property
    def houses(self) -> Grid:
        """
        Generate a grid of houses and their corresponding bodies.

        Returns:
            Grid of houses and their corresponding bodies.
        """
        grid = [["house", "cusp", "bodies", "sum"]]
        for hse in self.data1.houses:
            bodies = [
                svg_of(b.name)
                for b in self.data1.aspectables
                if self.data1.house_of(b) == hse.value
            ]
            grid.append(
                [
                    hse.value,
                    f"{hse.signed_deg:02d}° {svg_of(hse.sign.name)} {hse.minute:02d}'",
                    "".join(bodies),
                    len(bodies) or "",
                ]
            )
        return grid

    @property
    def celestial_body1(self) -> Grid:
        """
        Generate a grid of celestial bodies for the primary data.

        Returns:
            Grid of celestial bodies for the primary data.
        """
        return self.celestial_body(self.data1)

    @property
    def celestial_body2(self) -> Grid:
        """
        Generate a grid of celestial bodies for the secondary data.

        Returns:
            Grid of celestial bodies for the secondary data.
        """
        return self.celestial_body(self.data2)

    def celestial_body(self, data: Data) -> Grid:
        """
        Generate a grid of celestial bodies for the given data.

        Args:
            data: The data for which to generate the grid.

        Returns:
            Grid of celestial bodies for the given data.
        """
        grid = [("body", "sign", "house", "dignity")]
        for body in data.aspectables:
            grid.append(
                (
                    svg_of(body.name),
                    f"{body.signed_deg:02d}° {svg_of(body.sign.name)} {body.minute:02d}'",
                    self.data1.house_of(body),
                    svg_of(dignity_of(body)),
                )
            )
        return grid

    @property
    def cross_ref(self) -> StatData:
        """
        Generate cross-reference statistics between primary and secondary data.

        Returns:
            Cross-reference statistics between primary and secondary data.
        """
        stats = Stats(self.data1, self.data2)
        grid = stats.cross_ref.grid
        for row in range(len(grid)):
            for col in range(len(grid[0])):
                cell = grid[row][col]
                if name := symbol_name_map.get(cell):
                    grid[row][col] = svg_of(name)
        return StatData(stats.cross_ref.title, grid)

    @property
    def orbs(self) -> Grid:
        orb = self.data1.config.orb
        return [["aspect", "orb"]] + [[svg_of(aspect), orb[aspect]] for aspect in orb]

    @property
    def full_report(self) -> str:
        """
        Generate the full astrological report as an HTML string.

        Returns:
            Full astrological report as an HTML string.
        """
        chart = Chart(self.data1, width=400, data2=self.data2)
        row1 = div(
            # TODO: use basic_info_with_city when city is provided
            section("Birth Info", self.basic_info)
            + section("Elements, Modality & Polarity", self.element_vs_modality)
            + section("Hemisphere & Quadrants", self.quadrants_vs_hemisphere),
            class_="info_col",
        ) + div(chart.svg, class_="chart")

        row2 = section(f"{self.data1.name}'s Celestial Bodies", self.celestial_body1)

        if self.data2:
            row2 += section(
                f"{self.data2.name}'s Celestial Bodies", self.celestial_body2
            )
        row2 += section(self.cross_ref.title, self.cross_ref.grid)
        row3 = (
            section("Signs", self.signs)
            + section("Houses", self.houses)
            + section("Orbs", self.orbs)
        )
        css = Path(__file__).parent / "report.css"
        html = style(css.read_text()) + main(
            div(row1, class_="row1")
            + div(row2, class_="row2")
            + div(row3, class_="row3")
        )
        return html

    def create_pdf(self, html: str) -> BytesIO:
        """
        Create a PDF from the given HTML string.

        Args:
            html: The HTML string to convert to PDF.

        Returns:
            BytesIO object containing the PDF data.
        """
        fp = BytesIO()
        HTML(string=html).write_pdf(fp)
        return fp


# utils ======================================================================


def html_table_of(grid: Grid) -> str:
    """
    Convert a grid of data into an HTML table.

    Args:
        grid: The grid of data to convert.

    Returns:
        HTML table as a string.
    """
    rows = []
    for row in grid:
        cells = []
        for cell in row:
            if isinstance(cell, str) and cell.startswith("null:"):
                cells.append(td(cell.split(":")[1], colspan=2))
            else:
                cells.append(td(cell))
        rows.append(tr(cells))
    return table(rows)


def svg_of(name: str, scale: float = 0.5) -> str:
    """
    Generate an SVG representation of a given symbol name.

    Args:
        name: The name of the symbol.
        scale: The scale of the SVG.

    Returns:
        SVG representation of the symbol.
    """
    if not name:
        return ""
    stroke = TEXT_COLOR
    fill = "none"
    if name in ["mc", "asc", "dsc", "ic"]:
        stroke = "none"
        fill = TEXT_COLOR

    # get svg content from natal package
    svg_content = files("natal").joinpath(f"svg_paths/{name}.svg").read_text()

    return svg(
        svg_content,
        fill=fill,
        stroke=stroke,
        stroke_width=3 * scale,
        version="1.1",
        width=f"{20 * scale}px",
        height=f"{20 * scale}px",
        transform=f"scale({scale})",
        xmlns="http://www.w3.org/2000/svg",
    )


def section(title: str, grid: Grid) -> str:
    """
    Create an HTML section with a title and a table of data.

    Args:
        title: The title of the section.
        grid: The grid of data to include in the section.

    Returns:
        HTML section as a string.
    """
    return div(
        div(title, class_="title") + html_table_of(grid),
        class_="section",
    )
