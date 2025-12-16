from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from .chart_alignment import ChartAlignment
from .chart_data_serie import ChartDataSerie
from .chart_data_serie_type import ChartDataSerieType


class RadarChart(BaseModel):
  """Radar chart configuration"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  x_axis: ChartDataSerie = Field(description='X Axis of the chart')
  y_axis: list[ChartDataSerie] = Field(description='Y Axis of the chart', default_factory=list)
  title: str = Field(description='Title of the chart', default='Chart')
  align: ChartAlignment = Field(description='Alignment of the chart', default=ChartAlignment.CENTER)

  @field_serializer('align', when_used='always')
  def serialize_align(self, align: ChartAlignment) -> str:
    return align.value

  def render(self: Self) -> dict[str, Any]:
    """
    Render chart to a graphic Library.

    :param technology: The technology to use to render the chart.
    :type technology: ChartRenderTechnology

    :return: The configuration of the chart.
    :rtype: dict[str, Any]
    """
    return {'library': 'APEXCHARTS', 'configuration': self._render_apexcharts()}

  def _render_apexcharts(self: Self) -> dict[str, Any]:
    """
    Converts the configuration of the chart to Javascript library ApexCharts.
    """

    series = []
    colors = []

    for serie in self.y_axis:
      modified_serie = {'name': serie.label, 'data': serie.data}

      if serie.serie_type is not ChartDataSerieType.NONE:
        modified_serie['type'] = serie.serie_type.value

      series.append(modified_serie)
      colors.append(serie.color)

    config = {
      'series': series,
      'colors': colors,
      'xaxis': {
        'categories': self.x_axis.data,
        'type': self.x_axis.data_type.value,
        'title': {
          'text': self.x_axis.label,
          'style': {'fontFamily': 'Fira Sans Condensed', 'fontSize': '20px', 'fontWeight': 'normal'},
        },
      },
      'title': {
        'text': self.title,
        'align': self.align.value,
        'style': {'fontFamily': 'Fira Sans Condensed', 'fontSize': '20px', 'fontWeight': 'normal'},
      },
      'chart': {
        'type': 'radar',
        'animations': {'enabled': False},
        'toolbar': {'show': False},
        'zoom': {'enabled': False},
      },
      'dataLabels': {'enabled': True},
      'plotOptions': {'bar': {'horizontal': True, 'borderRadius': 4}},
    }

    return config
