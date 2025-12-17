from __future__ import annotations

from typing import Dict, Set

from ..definition import TuringMachineDefinition
from ..machine import State, Symbol, TransitionKey, TransitionValue, MultiTapeTuringMachine
from ..tape import Direction


class AbcEqualDefinition(TuringMachineDefinition):
    """
    1-tape Turing Machine for the language { a^n b^n c^n | n >= 1 }.

    It repeatedly:
      - finds the next unmarked 'a' on the left,
      - matches it with an unmarked 'b',
      - then with an unmarked 'c',
      - then returns to the left end and repeats.
    If no more 'a' are found and there are no extra b/c, it accepts.
    """

    def __init__(self) -> None:
        states: Set[State] = {
            "q0",       # look for next unmarked 'a'
            "q1",       # from X, search for unmarked 'b'
            "q2",       # from Y, search for unmarked 'c'
            "q3",       # go back to the left (until left blank)
            "q_accept",
            "q_reject",
        }

        input_alphabet: Set[Symbol] = {"a", "b", "c"}
        tape_alphabet: Set[Symbol] = {"a", "b", "c", "X", "Y", "Z", "_"}
        blank: Symbol = "_"

        transitions: Dict[TransitionKey, TransitionValue] = {
            # q0: look for the next unmarked 'a'
            ("q0", ("X",)): ("q0", ("X",), (Direction.RIGHT,)),
            ("q0", ("Y",)): ("q0", ("Y",), (Direction.RIGHT,)),
            ("q0", ("Z",)): ("q0", ("Z",), (Direction.RIGHT,)),
            ("q0", ("a",)): ("q1", ("X",), (Direction.RIGHT,)),
            ("q0", ("b",)): ("q_reject", ("b",), (Direction.STAY,)),
            ("q0", ("c",)): ("q_reject", ("c",), (Direction.STAY,)),
            ("q0", ("_",)): ("q_accept", ("_",), (Direction.STAY,)),

            # q1: search for first unmarked 'b'
            ("q1", ("a",)): ("q1", ("a",), (Direction.RIGHT,)),
            ("q1", ("Y",)): ("q1", ("Y",), (Direction.RIGHT,)),
            ("q1", ("b",)): ("q2", ("Y",), (Direction.RIGHT,)),
            ("q1", ("c",)): ("q_reject", ("c",), (Direction.STAY,)),
            ("q1", ("Z",)): ("q_reject", ("Z",), (Direction.STAY,)),
            ("q1", ("X",)): ("q_reject", ("X",), (Direction.STAY,)),
            ("q1", ("_",)): ("q_reject", ("_",), (Direction.STAY,)),

            # q2: search for first unmarked 'c'
            ("q2", ("b",)): ("q2", ("b",), (Direction.RIGHT,)),
            ("q2", ("Y",)): ("q2", ("Y",), (Direction.RIGHT,)),
            ("q2", ("Z",)): ("q2", ("Z",), (Direction.RIGHT,)),
            ("q2", ("c",)): ("q3", ("Z",), (Direction.LEFT,)),
            ("q2", ("a",)): ("q_reject", ("a",), (Direction.STAY,)),
            ("q2", ("X",)): ("q_reject", ("X",), (Direction.STAY,)),
            ("q2", ("_",)): ("q_reject", ("_",), (Direction.STAY,)),

            # q3: go back to the left end
            ("q3", ("a",)): ("q3", ("a",), (Direction.LEFT,)),
            ("q3", ("b",)): ("q3", ("b",), (Direction.LEFT,)),
            ("q3", ("c",)): ("q3", ("c",), (Direction.LEFT,)),
            ("q3", ("X",)): ("q3", ("X",), (Direction.LEFT,)),
            ("q3", ("Y",)): ("q3", ("Y",), (Direction.LEFT,)),
            ("q3", ("Z",)): ("q3", ("Z",), (Direction.LEFT,)),
            ("q3", ("_",)): ("q0", ("_",), (Direction.RIGHT,)),
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


def build_abc_equal_machine(input_string: str) -> MultiTapeTuringMachine:
    """
    Convenience helper that creates an a^n b^n c^n machine
    with the given input string on tape 1.
    """
    definition = AbcEqualDefinition()
    return definition.create_machine(initial_inputs=[input_string])
