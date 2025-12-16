from collections.abc import Callable

from kivy.input.motionevent import MotionEvent
from kivy.uix.behaviors import DragBehavior
from kivy.uix.image import Image

Pos = tuple[float, float]
ColRow = tuple[int, int]


class _ChessButton(DragBehavior, Image):
    """Can display a chess pieces and call a callback on click/drag-n-drop.

    This can not be used outside of a RelativeLayout, because it relies on
    the parent size to compute the (col, row) of the button.
    """

    _process_col_row: Callable[[ColRow], None]
    _col_row_on_down: ColRow | None
    _start_pos: Pos | None
    _was_dragged: bool

    def __init__(self, process_col_row, **kwargs):
        super().__init__(**kwargs)
        self._process_col_row = process_col_row
        self._col_row_on_down = None
        self._start_pos = None
        self._was_dragged = False

    def _col_row(self, pos: Pos) -> ColRow:
        """Get the (col, row) of the button at the given position."""
        # Relies on the fact that the parent is a RelativeLayout.
        return tuple(int(p // self.width) for p in pos)

    def on_touch_down(self, touch: MotionEvent) -> bool:
        if self.collide_point(*touch.pos):
            col_row = self._col_row(touch.pos)
            self._col_row_on_down = col_row
            self._process_col_row(col_row)
            self._start_pos = tuple(self.pos)
        return super().on_touch_down(touch)

    def on_touch_move(self, touch: MotionEvent) -> bool:
        """Center the button on the touch position."""
        if touch.grab_current is self:
            self.center = touch.pos
            self._was_dragged = True
            self.parent.cb_root._was_dragged = True
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch: MotionEvent) -> bool:
        if self.collide_point(*touch.pos) and self._was_dragged:
            self.pos = self._start_pos
            self._start_pos = None
            self.parent.cb_root._was_dragged = False
            self._was_dragged = False
            col_row = self._col_row(touch.pos)
            if col_row != self._col_row_on_down:
                self._process_col_row(col_row)
        return super().on_touch_up(touch)
