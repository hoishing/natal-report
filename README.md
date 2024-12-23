# PDF Report for the Natal Package

> generate PDF report for the Natal package

## Installation

- dependencies:
  - [Natal]: for natal chart data and SVG paths
  - [weasyprint]: PDF generation (refer weasyprint docs for installing OS dependencies)

`pip install natal natal_report weasyprint`

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

[demo_report_light.pdf]: https://github.com/hoishing/natal_report/blob/main/demo_report_light.pdf
[demo_report_mono.pdf]: https://github.com/hoishing/natal_report/blob/main/demo_report_mono.pdf
[Natal]: https://github.com/hoishing/natal
[weasyprint]: https://weasyprint.org
