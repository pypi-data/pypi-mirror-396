"""Module for loading and managing chess piece textures and board images.

This module uses Kivy to load images for chess pieces and board backgrounds.
"""

from pathlib import Path

from kivy.resources import resource_add_path, resource_find
from kivy.uix.image import Image

# Ensure that the assets directory is in the search path on all platforms
resource_add_path(Path(__file__).parent / "assets")


def piece2source(piece: str) -> str:
    """Get the file path for a chess piece image."""
    file = piece if piece.isupper() else f"{piece}_black"
    return resource_find(f"{file}.png")


def piece2texture(piece: str) -> str:
    """Get the texture for a chess piece image."""
    return Image(source=piece2source(piece)).texture


BOARD_PNG = "board.png"
INVERTED_BOARD_PNG = "board_inverted.png"
