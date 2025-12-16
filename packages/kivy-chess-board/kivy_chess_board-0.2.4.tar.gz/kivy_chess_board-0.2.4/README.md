# ChessBoard - a Kivy Widget to interact with a Chess Board

This package provides a chess board as a kivy widget. It allows users to
interact with the chess board by dragging and dropping pieces, and it can be
integrated into Kivy applications.

The widget displays the current state of a `chess.Board` from the
`python-chess` library. It supports highlighting specific moves and selecting
squares. By design, it does not implement any game logic or enforce chess rules;
it simply reflects the state of the provided `chess.Board` and notifies the host
application of user interactions.

## Exmaple Usage

See the [documentation](https://kivy-chess-board-ebce1f.gitlab.io/) for more
details and full API reference.

```python
import chess
from kivy.app import App
from kivy.config import Config as KivyConfig
from kivy.logger import LOG_LEVELS, Logger
from kivy.uix.floatlayout import FloatLayout
from kivy.utils import platform

from kivy_chess_board import ChessBoard


class MyApp(App):
    def build(self):
        root = FloatLayout()
        cb = ChessBoard()
        cb.highlight_hover_when_dragged = True
        root.add_widget(cb)

        # At any time we can set the board to a specific position and highlight
        # moves.
        cb.update(
            chess.Board(),
            moves_to_be_highlighted=[
                chess.Move.from_uci("e2e4"),
                chess.Move.from_uci("d2d4"),
            ],
            move_selector=0,  # e2e4 move appears "selected"
        )

        cb.process_square_selection = process_square
        cb.process_move_selection = process_move
        return root


def process_square(cb: ChessBoard, pos: chess.Square) -> None:
    """Callback to process square selections (clicks as well as drag-and-drop)."""
    cb.squares_to_be_highlighted = [pos]
    square_name = chess.square_name(pos)
    Logger.debug(f"App: Square selected: {square_name}")


def process_move(cb: ChessBoard, move: chess.Move) -> None:
    """Callback to process move selection."""
    if move not in cb.board.legal_moves:
        Logger.warning("App: Illegal move")
        return

    cb.board.push(move)
    cb.update()

    # flip board after each move, this will only be slow the first time when
    # the assets for the inverted board are loaded
    cb.inverted = not cb.inverted

    cb.moves_to_be_highlighted = [move]  # highlight last move
    cb.squares_to_be_highlighted = []


def adjust_kivy_config() -> None:
    """Remove weird touchpad behavior on Linux.

    This is a bug in Kivy itself, not specific to this progream."""
    if platform != "linux":
        return

    if KivyConfig is None or not KivyConfig.has_section("input"):
        return

    for opt in list(KivyConfig.options("input")):
        if KivyConfig.get("input", opt) == "probesysfs":
            KivyConfig.remove_option("input", opt)


Logger.setLevel(LOG_LEVELS["debug"])
adjust_kivy_config()
MyApp().run()
```
