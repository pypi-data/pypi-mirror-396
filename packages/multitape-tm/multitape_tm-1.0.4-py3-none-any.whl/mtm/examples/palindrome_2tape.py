from __future__ import annotations

from typing import Dict, Set, Tuple

from ..definition import TuringMachineDefinition
from ..machine import State, Symbol, TransitionKey, TransitionValue, MultiTapeTuringMachine
from ..tape import Direction


class Palindrome2TapeDefinition(TuringMachineDefinition):
    """
    2-tape Turing Machine that checks whether a binary string is a palindrome.

    Tape 1 holds the input, tape 2 is used as an auxiliary tape with marks.
    Reject is captured by having no defined transitions.
    """

    def __init__(self) -> None:
        # States from the PDF
        states: Set[State] = {"q0", "q1", "q2", "q3", "q4", "q5"}

        # Input and tape alphabets
        input_alphabet: Set[Symbol] = {"0", "1"}
        tape_alphabet: Set[Symbol] = {"0", "1", "X", "*"}  # X is a mark, * is blank
        blank: Symbol = "*"

        # Transitions
        transitions: Dict[TransitionKey, TransitionValue] = {
            # ============= q0 =============
            ("q0", ("0", "*")): (
                "q1",
                ("0", "X"),
                (Direction.STAY, Direction.RIGHT),
            ),
            ("q0", ("1", "*")): (
                "q1",
                ("1", "X"),
                (Direction.STAY, Direction.RIGHT),
            ),
            # empty input -> accept
            ("q0", ("*", "*")): (
                "q5",
                ("*", "*"),
                (Direction.STAY, Direction.STAY),
            ),

            # ============= q1 =============
            ("q1", ("0", "*")): (
                "q1",
                ("0", "0"),
                (Direction.RIGHT, Direction.RIGHT),
            ),
            ("q1", ("1", "*")): (
                "q1",
                ("1", "1"),
                (Direction.RIGHT, Direction.RIGHT),
            ),
            ("q1", ("*", "*")): (
                "q2",
                ("*", "*"),
                (Direction.STAY, Direction.LEFT),
            ),

            # ============= q2 =============
            ("q2", ("*", "0")): (
                "q2",
                ("*", "0"),
                (Direction.STAY, Direction.LEFT),
            ),
            ("q2", ("*", "1")): (
                "q2",
                ("*", "1"),
                (Direction.STAY, Direction.LEFT),
            ),
            ("q2", ("*", "X")): (
                "q3",
                ("*", "X"),
                (Direction.LEFT, Direction.RIGHT),
            ),

            # ============= q3 =============
            ("q3", ("0", "0")): (
                "q4",
                ("0", "0"),
                (Direction.STAY, Direction.RIGHT),
            ),
            ("q3", ("1", "1")): (
                "q4",
                ("1", "1"),
                (Direction.STAY, Direction.RIGHT),
            ),

            # ============= q4 =============
            ("q4", ("0", "0")): (
                "q3",
                ("0", "0"),
                (Direction.LEFT, Direction.STAY),
            ),
            ("q4", ("0", "1")): (
                "q3",
                ("0", "1"),
                (Direction.LEFT, Direction.STAY),
            ),
            ("q4", ("1", "0")): (
                "q3",
                ("1", "0"),
                (Direction.LEFT, Direction.STAY),
            ),
            ("q4", ("1", "1")): (
                "q3",
                ("1", "1"),
                (Direction.LEFT, Direction.STAY),
            ),
            # all checked -> accept
            ("q4", ("0", "*")): (
                "q5",
                ("0", "*"),
                (Direction.STAY, Direction.STAY),
            ),
            ("q4", ("1", "*")): (
                "q5",
                ("1", "*"),
                (Direction.STAY, Direction.STAY),
            ),
        }

        super().__init__(
            states=states,
            input_alphabet=input_alphabet,
            tape_alphabet=tape_alphabet,
            blank=blank,
            transitions=transitions,
            start_state="q0",
            accept_states={"q5"},
            reject_states=set(),
            num_tapes=2,
        )


def build_palindrome_2tape_machine(input_string: str) -> MultiTapeTuringMachine:
    """
    Convenience helper that creates a palindrome 2-tape machine
    with the given input string on tape 1 and tape 2 initially empty.
    """
    definition = Palindrome2TapeDefinition()
    return definition.create_machine(initial_inputs=[input_string, ""])
