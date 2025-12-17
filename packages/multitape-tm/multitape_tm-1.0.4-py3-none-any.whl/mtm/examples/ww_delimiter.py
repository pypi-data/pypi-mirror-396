from __future__ import annotations

from typing import Dict, Set

from ..definition import TuringMachineDefinition
from ..machine import State, Symbol, TransitionKey, TransitionValue, MultiTapeTuringMachine
from ..tape import Direction


class WwDelimiterDefinition(TuringMachineDefinition):
    """
    1-tape Turing Machine for the language { w % w | w in {a, b}* }.

    The machine:
      - scans the first w marking letters,
      - each time it marks a letter in the first w, it matches it with the
        next unmarked letter in the second w (after '%'),
      - when no unmarked letters remain before '%', it checks that there are
        no unmarked letters after '%' either.
    """

    def __init__(self) -> None:
        states: Set[State] = {
            "q0",
            "q1a_scan",
            "q1a_match",
            "q1b_scan",
            "q1b_match",
            "q2",
            "q_check",
            "q_accept",
            "q_reject",
        }

        input_alphabet: Set[Symbol] = {"a", "b", "%"}
        tape_alphabet: Set[Symbol] = {"a", "b", "%", "X", "Y", "_"}
        blank: Symbol = "_"

        transitions: Dict[TransitionKey, TransitionValue] = {
            # q0 — search for an unmarked letter BEFORE '%'
            ("q0", ("X",)): ("q0", ("X",), (Direction.RIGHT,)),
            ("q0", ("Y",)): ("q0", ("Y",), (Direction.RIGHT,)),
            ("q0", ("%",
             )): ("q_check", ("%",), (Direction.RIGHT,)),
            ("q0", ("a",)): ("q1a_scan", ("X",), (Direction.RIGHT,)),
            ("q0", ("b",)): ("q1b_scan", ("Y",), (Direction.RIGHT,)),
            ("q0", ("_",)): ("q_reject", ("_",), (Direction.STAY,)),

            # q1a_scan — move right until finding '%'
            ("q1a_scan", ("a",)): ("q1a_scan", ("a",), (Direction.RIGHT,)),
            ("q1a_scan", ("b",)): ("q1a_scan", ("b",), (Direction.RIGHT,)),
            ("q1a_scan", ("X",)): ("q1a_scan", ("X",), (Direction.RIGHT,)),
            ("q1a_scan", ("Y",)): ("q1a_scan", ("Y",), (Direction.RIGHT,)),
            ("q1a_scan", ("%",
             )): ("q1a_match", ("%",), (Direction.RIGHT,)),
            ("q1a_scan", ("_",)): ("q_reject", ("_",), (Direction.STAY,)),

            # q1a_match — after '%', search first unmarked 'a'
            ("q1a_match", ("X",)): ("q1a_match", ("X",), (Direction.RIGHT,)),
            ("q1a_match", ("Y",)): ("q1a_match", ("Y",), (Direction.RIGHT,)),
            ("q1a_match", ("a",)): ("q2", ("X",), (Direction.LEFT,)),
            ("q1a_match", ("b",)): ("q_reject", ("b",), (Direction.STAY,)),
            ("q1a_match", ("%",
             )): ("q_reject", ("%",), (Direction.STAY,)),
            ("q1a_match", ("_",)): ("q_reject", ("_",), (Direction.STAY,)),

            # q1b_scan — symmetric to q1a_scan, but for 'b'
            ("q1b_scan", ("a",)): ("q1b_scan", ("a",), (Direction.RIGHT,)),
            ("q1b_scan", ("b",)): ("q1b_scan", ("b",), (Direction.RIGHT,)),
            ("q1b_scan", ("X",)): ("q1b_scan", ("X",), (Direction.RIGHT,)),
            ("q1b_scan", ("Y",)): ("q1b_scan", ("Y",), (Direction.RIGHT,)),
            ("q1b_scan", ("%",
             )): ("q1b_match", ("%",), (Direction.RIGHT,)),
            ("q1b_scan", ("_",)): ("q_reject", ("_",), (Direction.STAY,)),

            # q1b_match — after '%', search first unmarked 'b'
            ("q1b_match", ("X",)): ("q1b_match", ("X",), (Direction.RIGHT,)),
            ("q1b_match", ("Y",)): ("q1b_match", ("Y",), (Direction.RIGHT,)),
            ("q1b_match", ("b",)): ("q2", ("Y",), (Direction.LEFT,)),
            ("q1b_match", ("a",)): ("q_reject", ("a",), (Direction.STAY,)),
            ("q1b_match", ("%",
             )): ("q_reject", ("%",), (Direction.STAY,)),
            ("q1b_match", ("_",)): ("q_reject", ("_",), (Direction.STAY,)),

            # q2 — go back to the beginning of the tape
            ("q2", ("a",)): ("q2", ("a",), (Direction.LEFT,)),
            ("q2", ("b",)): ("q2", ("b",), (Direction.LEFT,)),
            ("q2", ("X",)): ("q2", ("X",), (Direction.LEFT,)),
            ("q2", ("Y",)): ("q2", ("Y",), (Direction.LEFT,)),
            ("q2", ("%",
             )): ("q2", ("%",), (Direction.LEFT,)),
            ("q2", ("_",)): ("q0", ("_",), (Direction.RIGHT,)),

            # q_check — no unmarked letters remain before '%'
            ("q_check", ("X",)): ("q_check", ("X",), (Direction.RIGHT,)),
            ("q_check", ("Y",)): ("q_check", ("Y",), (Direction.RIGHT,)),
            ("q_check", ("%",
             )): ("q_check", ("%",), (Direction.RIGHT,)),
            ("q_check", ("a",)): ("q_reject", ("a",), (Direction.STAY,)),
            ("q_check", ("b",)): ("q_reject", ("b",), (Direction.STAY,)),
            ("q_check", ("_",)): ("q_accept", ("_",), (Direction.STAY,)),
        }

        super().__init__(
            states=states,
            input_alphabet=input_alphabet,
            tape_alphabet=tape_alphabet,
            blank=blank,
            transitions=transitions,
            start_state="q0",
            accept_states={"q_accept"},
            reject_states={"q_reject"},
            num_tapes=1,
        )


def build_ww_delimiter_machine(input_string: str) -> MultiTapeTuringMachine:
    """
    Convenience helper that creates a w%w machine with the given input string.
    """
    definition = WwDelimiterDefinition()
    return definition.create_machine(initial_inputs=[input_string])
