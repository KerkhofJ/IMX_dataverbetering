from shapely import Point
from shapely.geometry import LineString

from imxTools.utils.measure_line import (
    LineMeasureResult,
    MeasureLine,
    PointMeasureResult,
    ProjectionPointPosition,
    ProjectionsStatus,
)


def test_project_line_on_measure_line():
    # Define a reference line (like a railway track or road)
    measure_line = MeasureLine([[0, 0, 0], [10, 0, 0], [20, 10, 0]])

    # Define a line to be projected (e.g., a platform or asset)
    input_line = LineString(
        [
            (5, 5, 0),  # near first segment
            (15, 5, 0),  # near second segment
        ]
    )

    # Project the line
    result = measure_line.project_line(input_line)

    assert isinstance(result, LineMeasureResult)
    assert isinstance(result.from_result, PointMeasureResult)
    assert isinstance(result.to_result, PointMeasureResult)

    # Check that the projected measures are within expected range
    assert 0 <= result.from_measure <= measure_line.shapely_line.length
    assert 0 <= result.to_measure <= measure_line.shapely_line.length

    # Ensure from_measure is not greater than to_measure
    assert result.from_measure <= result.to_measure

    # check projected points lie on the measure line
    assert measure_line.shapely_line.distance(result.from_result.projected_point) < 1e-6
    assert measure_line.shapely_line.distance(result.to_result.projected_point) < 1e-6


def test_project_point_on_measure_line():
    # Define the reference measure line
    measure_line = MeasureLine([[0, 0, 0], [10, 0, 0], [20, 10, 0]])

    # Define a point near the first segment
    input_point = Point(5, 5, 0)

    result = measure_line.project(input_point)

    assert isinstance(result, PointMeasureResult)
    assert isinstance(result.projected_point, Point)

    # Check the projected point lies on the line
    assert measure_line.shapely_line.distance(result.projected_point) < 1e-6

    # Measure should be within bounds of the line
    assert 0 <= result.measure_2d <= measure_line.shapely_line.length

    # Side should be determined
    assert result.side in (
        ProjectionPointPosition.LEFT,
        ProjectionPointPosition.RIGHT,
        ProjectionPointPosition.ON_LINE,
        ProjectionPointPosition.UNDEFINED,
    )

    # Projection type should be one of the defined enum values
    assert result.overshoot_undershoot in (
        ProjectionsStatus.PERPENDICULAR,
        ProjectionsStatus.UNDERSHOOT,
        ProjectionsStatus.OVERSHOOT,
        ProjectionsStatus.ANGLE,
    )
