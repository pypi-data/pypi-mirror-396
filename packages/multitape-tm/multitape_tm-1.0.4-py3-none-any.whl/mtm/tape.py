# src/mtm/tape.py
from enum import IntEnum
from typing import Dict


class Direction(IntEnum):
    LEFT = -1
    RIGHT = 1
    STAY = 0


class Tape:
    """
    Represents a two-sided infinite tape with a single head.

    Symbols are stored in a dictionary index -> symbol so that
    only non-blank cells are explicitly represented.
    """

    def __init__(self, blank: str = "_", initial_input: str = "") -> None:
        self.blank: str = blank
        self.cells: Dict[int, str] = {}
        for i, ch in enumerate(initial_input):
            self.cells[i] = ch
        self.head: int = 0

    def read(self) -> str:
        """Read the symbol under the head."""
        return self.cells.get(self.head, self.blank)

    def write(self, symbol: str) -> None:
        """Write a symbol under the head (if it is blank, clear the cell)."""
        if symbol == self.blank and self.head in self.cells:
            del self.cells[self.head]
        else:
            self.cells[self.head] = symbol

    def move(self, direction: int) -> None:
        """
        Move the head one cell.

        direction must be one of:
            Direction.LEFT (-1), Direction.RIGHT (1), Direction.STAY (0)
        """
        self.head += int(direction)

    def __str__(self) -> str:
        """Human-readable view of the tape (for debugging)."""
        if not self.cells:
            return f"[{self.blank}]"
        indices = set(self.cells.keys()) | {self.head}
        min_i = min(indices)
        max_i = max(indices)
        out = []
        for i in range(min_i, max_i + 1):
            ch = self.cells.get(i, self.blank)
            if i == self.head:
                out.append(f"[{ch}]")
            else:
                out.append(f" {ch} ")
        return "".join(out)
