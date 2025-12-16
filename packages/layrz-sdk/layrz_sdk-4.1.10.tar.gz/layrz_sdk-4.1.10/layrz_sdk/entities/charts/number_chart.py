from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field

from .chart_render_technology import ChartRenderTechnology


class NumberChart(BaseModel):
  """Number chart configuration"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  value: float = Field(description='Value of the number')
  color: str = Field(description='Color of the number')
  label: str = Field(description='Label of the number')

  def render(self: Self, technology: ChartRenderTechnology = ChartRenderTechnology.FLUTTER) -> dict[str, Any]:
    """
    Render chart to a graphic Library.

    :param technology: The technology to use to render the chart.
    :type technology: ChartRenderTechnology

    :return: The configuration of the chart.
    :rtype: dict[str, Any]
    """
    if technology == ChartRenderTechnology.FLUTTER:
      return {
        'library': 'FLUTTER',
        'chart': 'NUMBER',
        'configuration': self._render_flutter(),
      }

    return {
      'library': 'FLUTTER',
      'chart': 'TEXT',
      'configuration': [f'Unsupported {technology}'],
    }

  def _render_flutter(self: Self) -> dict[str, Any]:
    """
    Converts the configuration of the chart to a Flutter native components.
    """
    return {
      'value': self.value,
      'color': self.color,
      'label': self.label,
    }
