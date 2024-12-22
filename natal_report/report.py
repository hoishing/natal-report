"""
This module generates a detailed astrological report in PDF format. 
It includes information about birth data, elements, modalities, polarities, hemispheres, quadrants, signs, houses, and celestial bodies. 
The report is created using the natal astrology library and rendered as an HTML document, which is then converted to a PDF.

Classes:
    Report: Generates the astrological report.
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

    Attributes:
        data1: The primary data for the report.
        data2: The secondary data for the report, if any.
    """

    def __init__(self, data1: Data, data2: Data | None = None):
        """
        Initializes the Report with the given data.

        Args:
            data1: The primary data for the report.
            data2: The secondary data for the report, if any.
        """
        self.data1: Data = data1
        self.data2: Data = data2

    @property
    def basic_info(self) -> Grid:
        """
        Generates basic information about the provided data.

        Returns:
            A grid containing the name, city, and birth date/time.
        """
        time_fmt = "%Y-%m-%d %H:%M"
        dt1 = self.data1.dt.strftime(time_fmt)
        output = [["name", "city", "birth"]]
        output.append([self.data1.name, self.data1.city, dt1])
        if self.data2:
            dt2 = self.data2.dt.strftime(time_fmt)
            output.append([self.data2.name, self.data2.city, dt2])
        return list(zip(*output))

    @property
    def element_vs_modality(self) -> Grid:
        """
        Generates a grid comparing elements and modalities.

        Returns:
            A grid comparing elements and modalities.
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
        Generates a grid comparing quadrants and hemispheres.

        Returns:
            A grid comparing quadrants and hemispheres.
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
        Generates a grid of signs and their corresponding bodies.

        Returns:
            A grid of signs and their corresponding bodies
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
        Generates a grid of houses and their corresponding bodies.

        Returns:
            A grid of houses and their corresponding bodies.
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
        Generates a grid of celestial bodies for the primary data.

        Returns:
            Grid: A grid of celestial bodies for the primary data.
        """
        return self.celestial_body(self.data1)

    @property
    def celestial_body2(self) -> Grid:
        """
        Generates a grid of celestial bodies for the secondary data.

        Returns:
            Grid: A grid of celestial bodies for the secondary data.
        """
        return self.celestial_body(self.data2)

    def celestial_body(self, data: Data) -> Grid:
        """
        Generates a grid of celestial bodies for the given data.

        Args:
            data: The data for which to generate the grid.

        Returns:
            A grid of celestial bodies for the given data.
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
        Generates cross-reference statistics between the primary and secondary data.

        Returns:
            StatData: Cross-reference statistics between the primary and secondary data.
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
        Generates the full astrological report as an HTML string.

        Returns:
            str: The full astrological report as an HTML string.
        """
        chart = Chart(self.data1, width=400, data2=self.data2)
        row1 = div(
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
        Creates a PDF from the given HTML string.

        Args:
            html: The HTML string to convert to PDF.

        Returns:
            A BytesIO object containing the PDF data.
        """
        fp = BytesIO()
        HTML(string=html).write_pdf(fp)
        return fp


# utils ======================================================================


def html_table_of(grid: Grid) -> str:
    """
    Converts a grid of data into an HTML table.

    # Arguments
    * grid - The grid of data to convert

    # Returns
    String containing the HTML table
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
    """Generates an SVG representation of a given symbol name.

    Args:
        name: The name of the symbol
        scale: The scale of the SVG

    Returns:
        The SVG representation of the symbol
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
    Creates an HTML section with a title and a table of data.

    Args:
        title: The title of the section.
        grid: The grid of data to include in the section.

    Returns:
        The HTML section as a string.
    """
    return div(
        div(title, class_="title") + html_table_of(grid),
        class_="section",
    )


# sample data ================================================================

if __name__ == "__main__":
    orb = Orb(
        conjunction=2,
        opposition=2,
        trine=2,
        square=2,
        sextile=1,
    )

    mimi = Data(
        name="MiMi",
        city="Taipei",
        dt="1980-04-20 14:30",
        config=Config(theme_type="mono", orb=orb),
    )

    transit = Data(name="Transit", city="Taipei", dt="2024-01-01 13:30")

    report = Report(mimi, transit)
    fp = report.create_pdf(report.full_report)
    with open("demo_report_mono.pdf", "wb") as f:
        f.write(fp.getvalue())

    mimi.config.theme_type = "light"
    mimi.config.orb = Orb()
    report.data2 = None
    fp = report.create_pdf(report.full_report)
    with open("demo_report_light.pdf", "wb") as f:
        f.write(fp.getvalue())
