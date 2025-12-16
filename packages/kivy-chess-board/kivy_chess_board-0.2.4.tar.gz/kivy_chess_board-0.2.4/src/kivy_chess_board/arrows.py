import math

from kivy.graphics import Canvas, Color, Line, Triangle

ARROW_GROUP = "arrows_group"


def draw_arrow(  # noqa: PLR0913
    canvas: Canvas,
    pos1: tuple[int, int],
    pos2: tuple[int, int],
    square_size: int,
    rgb: tuple[float, ...],
    highlight: bool = False,
):
    """Draw a straight arrow from (x1,y1) toward (x2,y2).

    Uses a line of width `line_width` and an arrowhead length of
    `arrowhead_len`, all in the given color `rgb=(r,g,b)`. rgb should be in the
    range [0,1].
    """
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    angle = math.atan2(dy, dx)

    arrowhead_len = square_size * 0.8
    line_width = square_size * 0.1

    # total distance from pos1 to pos2
    arrow_len = math.hypot(dx, dy)

    # how far the line portion should go before the arrowhead
    line_len = max(arrow_len - (arrowhead_len * 0.5), 0)

    # The line will end here, so the triangle tip is at pos2.
    # If you want the *tip* to be at pos2, the line must stop earlier:
    base = _point_at_distance(pos1, angle, line_len)

    # The arrowhead triangle: tip is at pos2; the "base" is around `base`.
    left_angle = angle + math.radians(150)
    right_angle = angle - math.radians(150)
    left = _point_at_distance(pos2, left_angle, arrowhead_len)
    right = _point_at_distance(pos2, right_angle, arrowhead_len)

    line_points = *pos1, *base
    arrow_head_points = *pos2, *left, *right

    with canvas:
        if highlight:
            # Draw a black line in the background to make the arrow stand out
            Color(0, 0, 0, 1, group=ARROW_GROUP)  # Black
            Line(points=line_points, width=line_width * 1.2, group=ARROW_GROUP)

            # Black arrowhead
            Line(
                points=arrow_head_points,
                close=True,
                width=line_width * 0.2,
                group=ARROW_GROUP,
            )

        Color(*rgb, 1, group=ARROW_GROUP)
        # Draw line from pos1 to the start of the arrowhead.
        Line(points=line_points, width=line_width, group=ARROW_GROUP)

        # Draw the arrowhead
        Triangle(points=arrow_head_points, group=ARROW_GROUP)


def _point_at_distance(
    p: tuple[int, int], angle: float, distance: float
) -> tuple[int, int]:
    """Return the point at a given distance.

    Calculates the distance from the point `p` in the direction
    `angle` (in radians) and returns the new point as (x, y).
    """
    x = p[0] + round(distance * math.cos(angle))
    y = p[1] + round(distance * math.sin(angle))
    return x, y
