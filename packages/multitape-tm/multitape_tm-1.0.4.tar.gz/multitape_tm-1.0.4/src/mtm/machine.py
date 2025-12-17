# src/mtm/machine.py
from __future__ import annotations
from typing import Dict, Hashable, Iterable, List, Sequence, Tuple

from .tape import Tape, Direction


State = Hashable  # usually str or int
Symbol = str

# Transition key type: (state, (s1,...,sk))
TransitionKey = Tuple[State, Tuple[Symbol, ...]]

# Transition value type: (new_state, (w1,...,wk), (m1,...,mk))
TransitionValue = Tuple[State, Tuple[Symbol, ...], Tuple[int, ...]]


class MultiTapeTuringMachine:
    """
    k-tape Turing Machine simulator.

    - states: set of states
    - input_alphabet: input symbols
    - tape_alphabet: tape symbols (includes input_alphabet and blank)
    - blank: blank symbol
    - transitions: dict mapping
        (state, (s1,...,sk)) -> (new_state, (w1,...,wk), (m1,...,mk))
      where mi ∈ {Direction.LEFT, Direction.RIGHT, Direction.STAY} or -1, 0, 1.
    """

    def __init__(
        self,
        states: Iterable[State],
        input_alphabet: Iterable[Symbol],
        tape_alphabet: Iterable[Symbol],
        blank: Symbol,
        transitions: Dict[TransitionKey, TransitionValue],
        start_state: State,
        accept_states: Iterable[State],
        reject_states: Iterable[State] | None = None,
        num_tapes: int = 1,
        initial_inputs: Sequence[str] | None = None,
    ) -> None:
        # Basic sets
        self.states = set(states)
        self.input_alphabet = set(input_alphabet)
        self.tape_alphabet = set(tape_alphabet)
        self.blank = blank

        # Transitions
        self.transitions: Dict[TransitionKey, TransitionValue] = transitions

        self.start_state = start_state
        self.accept_states = set(accept_states)
        self.reject_states = set(reject_states or [])

        self.num_tapes = num_tapes

        # Initial inputs per tape
        if initial_inputs is None:
            initial_inputs = [""] * num_tapes
        if len(initial_inputs) != num_tapes:
            raise ValueError("initial_inputs must have length num_tapes.")

        # Create tapes
        self.tapes: List[Tape] = [
            Tape(blank, initial_inputs[i]) for i in range(num_tapes)
        ]

        # Initial state
        self.current_state: State = start_state
        self.step_count: int = 0

    # ---------------- Utility methods ----------------

    def reset(self, initial_inputs: Sequence[str] | None = None) -> None:
        """Reset the machine with optional new inputs."""
        if initial_inputs is None:
            initial_inputs = ["" for _ in range(self.num_tapes)]

        if len(initial_inputs) != self.num_tapes:
            raise ValueError("initial_inputs must have length num_tapes.")

        self.tapes = [Tape(self.blank, s) for s in initial_inputs]
        self.current_state = self.start_state
        self.step_count = 0

    def get_configuration(self) -> dict:
        """Return a snapshot of the current configuration."""
        return {
            "state": self.current_state,
            "tapes": [str(t) for t in self.tapes],
            "step": self.step_count,
        }

    # ----------------- Single simulation step -----------------

    def step(self) -> str:
        """
        Execute one TM step.

        Returns:
            - 'RUNNING' if the machine keeps running,
            - 'ACCEPT', 'REJECT' or 'HALT' if it stops.
        """
        # Read symbols on all tapes
        read_symbols = tuple(t.read() for t in self.tapes)
        key: TransitionKey = (self.current_state, read_symbols)

        # If no transition is defined, the machine halts
        if key not in self.transitions:
            if self.current_state in self.accept_states:
                return "ACCEPT"
            if self.current_state in self.reject_states:
                return "REJECT"
            return "HALT"

        new_state, write_symbols, moves = self.transitions[key]

        # Write on tapes
        for t, sym in zip(self.tapes, write_symbols):
            t.write(sym)

        # Move heads
        for t, mv in zip(self.tapes, moves):
            t.move(mv)

        # Update state
        self.current_state = new_state
        self.step_count += 1

        # Check special states
        if self.current_state in self.accept_states:
            return "ACCEPT"
        if self.current_state in self.reject_states:
            return "REJECT"
        return "RUNNING"

    # --------------- Full execution ----------------

    def run(self, max_steps: int = 10_000) -> str:
        """
        Run the machine until it stops or max_steps is reached.

        Returns the final status: 'ACCEPT', 'REJECT', 'HALT' or 'RUNNING'
        (if it was cut off at max_steps).
        """
        status = "RUNNING"
        while status == "RUNNING" and self.step_count < max_steps:
            status = self.step()
        return status
