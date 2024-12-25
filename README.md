# PDF Report for the Natal Package

[![ci-badge]][ci-url] [![pypi-badge]][pypi-url] [![MIT-badge]][MIT-url] [![black-badge]][black-url]

> generate PDF report for the [Natal] package

## Installation

- dependencies:
  - [Natal]: for natal chart data and SVG paths
  - [weasyprint]: PDF generation
    - refer weasyprint docs for installing OS dependencies
    - you may need to install [Pango] for text rendering

`pip install natal-report`

or install as optional dependency of [Natal]:

`pip install "natal[report]"`

## Usage

```python
from natal import Data, Config
from natal.config import Orb
from natal_report import Report

config = Config(
    theme_type="mono",
    orb=Orb(conjunction=2, opposition=2, trine=2, square=2, sextile=1),
)

mimi = Data(
    name="Mimi",
    utc_dt="1980-02-23 00:00",
    lat=25.0375,
    lon=121.5633,
    config=config,
)

transit = Data(
    name="transit",
    utc_dt="2024-12-21 00:00",
    lat=25.0375,
    lon=121.5633,
)

report = Report(data1=mimi, data2=transit)
html = report.full_report
bytes_io = report.create_pdf(html)

with open("demo_report_mono.pdf", "wb") as f:
    f.write(bytes_io.getbuffer())
```

- see [demo_report_light.pdf] for light theme with Birth Chart
- see [demo_report_mono.pdf] for mono theme with Transit Chart

[black-badge]: https://img.shields.io/badge/formatter-Black-black
[black-url]: https://github.com/psf/black
[ci-badge]: https://github.com/hoishing/natal-report/actions/workflows/ci.yml/badge.svg
[ci-url]: https://github.com/hoishing/natal-report/actions/workflows/ci.yml
[demo_report_light.pdf]: https://github.com/hoishing/natal-report/blob/main/demo_report_light.pdf
[demo_report_mono.pdf]: https://github.com/hoishing/natal-report/blob/main/demo_report_mono.pdf
[MIT-badge]: https://img.shields.io/badge/license-MIT-blue.svg
[MIT-url]: https://github.com/hoishing/natal-report/blob/main/LICENSE
[Natal]: https://github.com/hoishing/natal
[Pango]: https://gitlab.gnome.org/GNOME/pango
[pypi-badge]: https://img.shields.io/pypi/v/natal-report
[pypi-url]: https://pypi.org/project/natal-report
[weasyprint]: https://doc.courtbouillon.org/weasyprint/stable/
