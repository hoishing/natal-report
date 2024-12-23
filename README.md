# PDF Report for the Natal Package

[![ci-badge]][ci-url] [![pypi-badge]][pypi-url] [![MIT-badge]][MIT-url] [![black-badge]][black-url]

> generate PDF report for the Natal package

## Installation

- dependencies:
  - [Natal]: for natal chart data and SVG paths
  - [weasyprint]: PDF generation
    - refer weasyprint docs for installing OS dependencies
    - you may need to install [Pango] for text rendering

`pip install natal[report]`

## Usage

```python
from natal import Data
from natal_report import Report

mimi = Data(
    name="Mimi",
    dt="1990-01-01 00:00",
    lat="25.0375",
    lon="121.5633",
    tz="Asia/Taipei"
)

transit = Data(
    name="transit",
    dt="2024-12-21 00:00",
    lat="25.0375",
    lon="121.5633",
    tz="Asia/Taipei"
)

report = Report(data1=mimi, data2=transit)
html = report.full_report
report.create_pdf(html) # returns BytesIO
```

- see [demo_report_light.pdf] for light theme with Birth Chart
- see [demo_report_mono.pdf] for mono theme with Transit Chart

[black-badge]: https://img.shields.io/badge/formatter-Black-black
[black-url]: https://github.com/psf/black
[ci-badge]: https://github.com/hoishing/natal_report/actions/workflows/ci.yml/badge.svg
[ci-url]: https://github.com/hoishing/natal_report/actions/workflows/ci.yml
[demo_report_light.pdf]: https://github.com/hoishing/natal_report/blob/main/demo_report_light.pdf
[demo_report_mono.pdf]: https://github.com/hoishing/natal_report/blob/main/demo_report_mono.pdf
[MIT-badge]: https://img.shields.io/badge/license-MIT-blue.svg
[MIT-url]: https://github.com/hoishing/natal_report/blob/main/LICENSE
[Natal]: https://github.com/hoishing/natal
[Pango]: https://gitlab.gnome.org/GNOME/pango
[pypi-badge]: https://img.shields.io/pypi/v/natal-report
[pypi-url]: https://pypi.org/project/natal-report
[weasyprint]: https://doc.courtbouillon.org/weasyprint/stable/
