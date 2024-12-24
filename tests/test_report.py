import pytest
from io import BytesIO
from natal import Config, Data
from natal.config import Orb
from natal_report import Report


@pytest.fixture(scope="module")
def report():
    person1 = {
        "name": "shing",
        "lat": 22.2783,
        "lon": 114.175,
        "utc_dt": "1976-04-20 09:58",
    }

    person2 = {
        "name": "belle",
        "lat": 22.2783,
        "lon": 114.175,
        "utc_dt": "2011-01-23 00:44",
    }

    orb = Orb(
        conjunction=2,
        opposition=2,
        trine=2,
        square=2,
        sextile=1,
    )

    data1 = Data(**person1, config=Config(theme_type="light", orb=orb))
    data2 = Data(**person2)
    return Report(data1=data1, data2=data2)


def test_basic_info(report):
    basic_info = report.basic_info
    assert basic_info[0] == ("name", "shing", "belle")
    assert basic_info[1] == (
        "location",
        "22.2783°N 114.175°E",
        "22.2783°N 114.175°E",
    )
    assert basic_info[2][0] == "UTC time"
    assert basic_info[2][1] == "1976-04-20 09:58", "2011-01-23 00:44"


def test_element_vs_modality(report):
    grid = report.element_vs_modality
    assert len(grid) > 0
    assert grid[4] == ["sum", 2, 2, 5, 4, 13]
    assert [g[5] for g in grid[:5]] == ["sum", 7, 5, 1, 13]
    assert grid[5] == ["◐", "null:4 pos", "null:9 neg", ""]
    assert grid[1][1].startswith("<svg")


def test_quadrants_vs_hemisphere(report):
    grid = report.quadrants_vs_hemisphere
    assert len(grid) > 0
    assert grid[3] == ["sum", 6, 5, 11]
    assert [g[3] for g in grid] == ["sum", 6, 6, 11]
    assert grid[1][1][0].startswith("<svg")


def test_signs(report):
    grid = report.signs
    assert len(grid) > 0
    assert [g[2] for g in grid[:6]] == ["sum", 1, 3, "", 3, ""]
    assert grid[1][1].startswith("<svg")


def test_houses(report):
    grid = report.houses
    assert len(grid) > 0
    assert [g[0] for g in grid[1:13]] == list(range(1, 13))
    assert [g[3] for g in grid[:5]] == ["sum", 3, 1, 1, ""]
    assert "<svg" in grid[1][1]


def test_celestial_body1(report):
    grid = report.celestial_body1
    assert len(grid) > 0
    assert [g[2] for g in grid] == ["house", 7, 3, 7, 6, 9, 7, 10, 1, 2, 12, 1, 1, 10]
    assert [g[1][:3] for g in grid[1:5]] == ["00°", "19°", "18°", "14°"]
    assert grid[1][3] == ""
    assert grid[2][3].startswith("<svg")


def test_celestial_body2(report):
    grid = report.celestial_body2
    assert len(grid) > 0


def test_cross_ref(report):
    grid = report.cross_ref.grid
    assert len(grid) == 14
    assert len(grid[0]) == 15
    assert grid[1][1] == ""
    assert grid[4][4].startswith("<svg")


def test_orb(report):
    grid = report.orbs
    assert len(grid) == 7
    assert grid[1][1] == 2
    assert grid[4][0].startswith("<svg")
    assert grid[6][1] == 0


def test_full_report(report):
    full_report = report.full_report
    assert isinstance(full_report, str)
    assert len(full_report) > 0


def test_create_pdf(report):
    html = report.full_report
    pdf = report.create_pdf(html)

    # Check it's a BytesIO object
    assert isinstance(pdf, BytesIO)
    assert pdf.getbuffer().nbytes > 0

    # Check PDF magic numbers
    pdf.seek(0)
    header = pdf.read(4).decode("utf-8")
    assert header == "%PDF", "File doesn't start with PDF header"
