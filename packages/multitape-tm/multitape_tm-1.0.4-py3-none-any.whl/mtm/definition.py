# src/mtm/definition.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Sequence, Set, Tuple, Hashable, Optional

from .machine import (
    MultiTapeTuringMachine,
    State,
    Symbol,
    TransitionKey,
    TransitionValue,
)


@dataclass(frozen=True)
class TuringMachineDefinition:
    """
    Immutable definition of a multi-tape Turing Machine.

    This object stores all the structural information:
      - states
      - input and tape alphabets
      - blank symbol
      - transition function
      - start, accept and reject states
      - number of tapes

    It can be reused to build multiple machine instances with
    different initial inputs.
    """

    states: Set[State]
    input_alphabet: Set[Symbol]
    tape_alphabet: Set[Symbol]
    blank: Symbol
    transitions: Dict[TransitionKey, TransitionValue]
    start_state: State
    accept_states: Set[State]
    reject_states: Set[State]
    num_tapes: int

    def create_machine(
        self,
        initial_inputs: Optional[Sequence[str]] = None,
    ) -> MultiTapeTuringMachine:
        """
        Build a new MultiTapeTuringMachine instance with the given initial inputs.

        - initial_inputs: one string per tape. If None, all tapes start empty.
        """
        return MultiTapeTuringMachine(
            states=self.states,
            input_alphabet=self.input_alphabet,
            tape_alphabet=self.tape_alphabet,
            blank=self.blank,
            transitions=self.transitions,
            start_state=self.start_state,
            accept_states=self.accept_states,
            reject_states=self.reject_states,
            num_tapes=self.num_tapes,
            initial_inputs=initial_inputs,
        )
