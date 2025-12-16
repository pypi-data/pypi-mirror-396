from collections.abc import Callable
from pathlib import Path

import chess
from kivy.core.window import Window  # ty: ignore[unresolved-import]
from kivy.graphics.texture import Texture  # ty: ignore[unresolved-import]
from kivy.lang import Builder
from kivy.properties import (  # ty: ignore[unresolved-import]
    BooleanProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
)
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget

from ._chess_button import ColRow, _ChessButton
from ._highlight_square import HighlightSquare
from .arrows import ARROW_GROUP, draw_arrow
from .assets import piece2texture
from .nop import nop


class ChessBoard(RelativeLayout):
    """
    Kivy widget that renders a chessboard, pieces, and optional move arrows.

    The board is composed of 64 internal `_ChessButton` tiles arranged in an
    8×8 grid inside the `ids.board` container defined in the accompanying
    `chess_gui.kv`. Each tile displays the current piece texture for its
    square and forwards click/drag interactions to game logic via
    `process_square_selection` or `process_move_selection` callbacks.
    """

    board: chess.Board = ObjectProperty(chess.Board())
    """
    The current position being displayed. Assignement triggers redraw. If
    changed in-place `update()` must be called to force a redraw.
    """

    highlight_hover: bool
    """
    If set to true, the square over which the mouse hovers will be highlighted.
    Implies `highlight_hoverd_squares_when_dragged`.
    """

    highlight_hover_when_dragged: bool
    """
    If set to true, the square over which the mouse hovers will be highlighted,
    if something is dragged (the mouse is pressed). Can be used to give visual
    feedback for drag-n-drop of pieces.
    """

    inverted: bool = BooleanProperty(False)
    """
    When True, the board is shown from Black's perspective (ranks/files
    mirrored). Defaults to False. Assignment triggers redraw.
    """

    moves_to_be_highlighted: list[chess.Move] = ListProperty([])
    """
    Sequence of moves to visualize as arrows. A red-white gradient
    is used for the arrow's color, hence moves early in the list appear
    more highlighted than moves late in the list. Change to this property
    triggers a redraw of the arrows.
    """

    move_selector: int = NumericProperty(-1)
    """
    Index of the highlighted move inside `moves_to_be_highlighted`. Values
    which are not an valied index of `moves_to_be_highlighted` mean no
    selection. Assigning this property triggers a redraw of the arrows.
    """

    process_square_selection: Callable[["ChessBoard", chess.Square], None]
    """
    Callback invoked whenever a square is clicked/tapped. Receives the 
    ChessBoard widget itself and a `python-chess` square index (0..63, a1==0).
    """

    process_move_selection: Callable[["ChessBoard", chess.Move], None]
    """
    Callback invoked whenever a move is made. Receives the ChessBoard widget
    itself and a `python-chess` `chess.Move`. The move might not be a valid
    move. This is a convenience wrapper, use `process_square_selection` for
    more control.
    """

    squares_to_be_highlighted: list[chess.Move] = ListProperty([])
    """
    List of chess.Moves which are highlighted on the board. Change of this
    property triggers a redraw of the highlighted squares.
    """

    _buttons: list[_ChessButton]
    _highlibht_sq: list[HighlightSquare]
    _first_square: chess.Square | None
    _no_redraw: bool
    _was_dragged: bool
    _last_hover_hs: Widget | None

    def __init__(self, **kwargs):
        """
        Initialize the chessboard widget.

        Parameters
        ----------
        **kwargs
            Forwarded to `RelativeLayout.__init__`. Typical Kivy keyword
            arguments (e.g., `size_hint`, `pos`, etc.) are supported.

        Notes
        -----
        The `process_square_selection` and `process_move_selection` callbacks
        are initialized to no-op and can be assigned by the consumer to receive
        square-click events.
        """
        super().__init__(**kwargs)
        self.process_square_selection, self.process_move_selection = nop, nop
        self.highlight_hover, self.highlight_hover_when_dragged = (False,) * 2
        self._no_redraw, self._was_dragged = (False,) * 2
        self._first_square, self._last_hover_hs = None, None
        Window.bind(mouse_pos=self._on_mouse_pos)

    def on_kv_post(self, base_widget: Widget) -> None:
        """@private

        For each chess square we create a button which calls game logic on
        click and can also display an piece image. We than attach all 64
        of them to the board (grid-layout) in the needed order.
        """
        self._buttons = [_ChessButton(self._process_click) for _ in chess.SQUARES]
        for btn in reversed(self._buttons):
            self.ids.board.add_widget(btn)

        self._highlight_sq = [HighlightSquare() for _ in chess.SQUARES]
        for btn in reversed(self._highlight_sq):
            self.ids.highlight.add_widget(btn)

    def update(
        self,
        board: chess.Board | None = None,
        moves_to_be_highlighted: list[chess.Move] | None = None,
        move_selector: int | None = None,
    ) -> None:
        """
        Optionally, update the position and the move arrows to draw. Forces a redraw.

        Parameters
        ----------
        board : chess.Board, optional
            The position to render. If `None`, the current position is kept.
        moves_to_be_highlighted : list[chess.Move], optional
            Sequence of moves to visualize as arrows on the board. The arrow
            color lightens from red to white with increasing index to indicate
            ranking/order. Defaults to empty list.
        move_selector : int, optional
            Index into `moves_to_be_highlighted` to draw as the "selected"
            (highlighted) arrow. Use `None` for no selection (default)
        """
        self._no_redraw = True
        if board:
            self.board = board
        if moves_to_be_highlighted is not None:
            self.moves_to_be_highlighted = moves_to_be_highlighted
        if move_selector is not None:
            self.move_selector = move_selector
        self._no_redraw = False
        self._update_image()

    def _update_image(self) -> None:
        if self._no_redraw:
            return

        btns = reversed(self._buttons) if self.inverted else self._buttons
        for square, btn in enumerate(btns):
            p = self.board.piece_at(square)
            btn.texture = piece2texture(p.symbol()) if p else Texture.create()

        self._update_arrows()

    def _update_arrows(self) -> None:
        if self._no_redraw:
            return

        canvas = self.ids.board.canvas
        canvas.remove_group(ARROW_GROUP)  # Clear old arrows
        pos = self.moves_to_be_highlighted

        rgb = 0.8, 0, 0  # Start color (red)
        for i, move in enumerate(pos):
            from_sq, to_sq = move.from_square, move.to_square
            if self.inverted:
                from_sq = 63 - from_sq
                to_sq = 63 - to_sq
            draw_arrow(
                canvas,
                pos1=self._buttons[from_sq].center,
                pos2=self._buttons[to_sq].center,
                square_size=self._buttons[0].size[0],
                rgb=tuple(c + (1 - c) * i / len(pos) for c in rgb),
                highlight=i == self.move_selector,
            )

    def _update_highlighted_squares(self) -> None:
        if self._no_redraw:
            return

        for i, sq in enumerate(self._highlight_sq):
            j = 63 - i if self.inverted else i
            sq.highlighted = j in self.squares_to_be_highlighted

    def invert_board(self) -> None:
        """
        Toggle the board orientation between White and Black perspectives.
        Triggers redraw
        """
        self.inverted = not self.inverted

    def _process_click(self, col_row: ColRow) -> None:
        if self.inverted:
            col_row = 7 - col_row[0], 7 - col_row[1]

        square = chess.square(*col_row)
        if square not in chess.SQUARES:
            return

        self.process_square_selection(self, square)

        if square == self._first_square:  # Deselect if same square clicked
            self._first_square = None
            return

        if (p := self.board.piece_at(square)) and self.board.turn == p.color:
            self._first_square = square  # Save first square
            return

        if self._first_square is None:
            print("No own piece on this square")
            return

        self.process_move_selection(self, chess.Move(self._first_square, square))
        self._first_square = None

    def on_parent(self, *args):
        """@private"""
        # Unbind when removed from the window
        if not self.parent:
            Window.unbind(mouse_pos=self._on_mouse_pos)

    def _on_mouse_pos(self, _win, pos):
        """Depending on settings, highlight hovered square."""
        if not (
            self.highlight_hover
            or self.highlight_hover_when_dragged
            and self._was_dragged
        ):
            return

        # Find which highlight square the mouse is over (64 checks is fine)
        hovered = None
        for sq in self._highlight_sq:
            # convert window coords to the square's local coords and test
            if sq.collide_point(*sq.to_widget(*pos)):
                hovered = sq
                break

        # Flip highlight on change
        if hovered is self._last_hover_hs:
            return
        if self._last_hover_hs:
            for sq in self.squares_to_be_highlighted:
                isq = 63 - int(sq) if self.inverted else sq
                if self._highlight_sq[isq] is self._last_hover_hs:
                    break
            else:
                self._last_hover_hs.highlighted = False
        if hovered:
            hovered.highlighted = True
            self._last_hover_hs = hovered


kv_file = str(Path(__file__).parent / "chess_board.kv")
Builder.load_file(kv_file)
