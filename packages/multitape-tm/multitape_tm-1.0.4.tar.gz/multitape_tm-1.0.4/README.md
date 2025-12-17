# mtm — Multi-tape Turing Machine simulator in Python

`mtm` is a small, reusable library for simulating **multi-tape Turing Machines** in Python.

It provides:

- A core `MultiTapeTuringMachine` simulator.
- A `Tape` abstraction with infinite tapes in both directions.
- A `Direction` enum for head movements.
- A `TuringMachineDefinition` class to encapsulate reusable machine definitions.
- A `console` helper (`animate_run`) to visualize head movements as a terminal animation.
- Ready-to-use example machines under `mtm.examples`.

The goal is to make it easy to **experiment with Turing Machines**, build examples for **complexity theory** courses, and integrate the simulator into other projects (GUIs, notebooks, etc.).

---

## Installation

From PyPI:

```bash
pip install multitape-tm
```

From the project root (where `pyproject.toml` lives):

```bash
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
python -m pip install -e .
````

This installs `mtm` in **editable mode**, so changes to the source code are immediately reflected when you import the package.

---

## Quick start

### Basic 1-tape example

The smallest possible example: a 1-tape TM that moves right over a run of `a`’s and accepts when it hits blank.

```python
from mtm import MultiTapeTuringMachine, Direction

# States and alphabets
states = {"q0", "q_accept"}
input_alphabet = {"a"}
tape_alphabet = {"a", "_"}
blank = "_"

start_state = "q0"
accept_states = {"q_accept"}

# Transition function:
# (state, (symbols_on_tapes, ...)) -> (new_state, (symbols_to_write, ...), (moves, ...))
transitions = {
    # While reading 'a', move right
    ("q0", ("a",)): ("q0", ("a",), (Direction.RIGHT,)),
    # When reaching blank, accept
    ("q0", ("_",)): ("q_accept", ("_",), (Direction.STAY,)),
}

tm = MultiTapeTuringMachine(
    states=states,
    input_alphabet=input_alphabet,
    tape_alphabet=tape_alphabet,
    blank=blank,
    transitions=transitions,
    start_state=start_state,
    accept_states=accept_states,
    reject_states=set(),
    num_tapes=1,
    initial_inputs=["aaa"],
)

result = tm.run()
print("Final status:", result)
print("Final configuration:", tm.get_configuration())
```

---

## Animating the heads in the terminal

`mtm.console.animate_run` clears the screen every step and shows a live “animation” of the tape(s), with the head position indicated by `[...]`.

```python
from mtm import MultiTapeTuringMachine, Direction, animate_run

states = {"q0", "q_accept"}
input_alphabet = {"a"}
tape_alphabet = {"a", "_"}
blank = "_"
start_state = "q0"
accept_states = {"q_accept"}

transitions = {
    ("q0", ("a",)): ("q0", ("a",), (Direction.RIGHT,)),
    ("q0", ("_",)): ("q_accept", ("_",), (Direction.STAY,)),
}

tm = MultiTapeTuringMachine(
    states=states,
    input_alphabet=input_alphabet,
    tape_alphabet=tape_alphabet,
    blank=blank,
    transitions=transitions,
    start_state=start_state,
    accept_states=accept_states,
    reject_states=set(),
    num_tapes=1,
    initial_inputs=["aaa"],
)

animate_run(tm, max_steps=50, delay=0.2)
```

Output (sketch):

```text
Multi-tape Turing Machine
========================================
Step : 3
State: q0

Tape 0:  a  a [a] _

(press Ctrl+C to stop)
```

---

## Library overview

### Core types

* `Tape`

  * Represents an infinite tape in both directions.
  * Stores only **non-blank** cells in a dictionary `index -> symbol`.
  * Key methods:

    * `read() -> str`
    * `write(symbol: str) -> None`
    * `move(direction: int) -> None`
    * `__str__()` gives a human-readable view with the head wrapped in `[...]`.

* `Direction` (enum)

  * `Direction.LEFT  = -1`
  * `Direction.RIGHT = 1`
  * `Direction.STAY  = 0`

* `MultiTapeTuringMachine`

  * Simulates a TM with **k tapes**.

  * Constructor parameters:

    * `states`: iterable of states (typically strings).
    * `input_alphabet`: symbols that may appear in the input.
    * `tape_alphabet`: symbols that may appear on the tapes (must include `input_alphabet` and `blank`).
    * `blank`: blank symbol.
    * `transitions`: dict with keys and values:

      * Key: `(state, (s1, ..., sk))`
      * Value: `(new_state, (w1, ..., wk), (m1, ..., mk))`

        * `wi` are symbols to write.
        * `mi` are movements (`Direction.LEFT`, `Direction.RIGHT`, `Direction.STAY`, or `-1, 0, 1`).
    * `start_state`
    * `accept_states`
    * `reject_states`
    * `num_tapes`
    * `initial_inputs`: list of strings, one per tape.

  * Main methods:

    * `step() -> str`

      * Executes one step.
      * Returns `"RUNNING"`, `"ACCEPT"`, `"REJECT"` or `"HALT"`.
    * `run(max_steps: int = 10_000) -> str`

      * Runs until halting, accepting/rejecting, or reaching `max_steps`.
    * `reset(initial_inputs: Optional[Sequence[str]] = None) -> None`
    * `get_configuration() -> dict`

      * Returns `{ "state": ..., "tapes": [...], "step": ... }`.

* `TuringMachineDefinition`

  * A dataclass that stores a **reusable definition** of a machine:

    * `states`
    * `input_alphabet`
    * `tape_alphabet`
    * `blank`
    * `transitions`
    * `start_state`
    * `accept_states`
    * `reject_states`
    * `num_tapes`
  * Method:

    * `create_machine(initial_inputs: Optional[Sequence[str]] = None) -> MultiTapeTuringMachine`

  This is intended for building **reusable models**:
  you define the structure once, and then create many instances with different inputs.

---

## Using the built-in examples

The package includes several predefined Turing Machine definitions under `mtm.examples`.

> All examples accept an **input string** and return a `MultiTapeTuringMachine` instance ready to run or animate.

### 1. Binary palindrome (2 tapes)

`mtm.examples.palindrome_2tape` implements a 2-tape TM that checks if a binary string is a palindrome.

```python
from mtm.examples import build_palindrome_2tape_machine
from mtm import animate_run

tm = build_palindrome_2tape_machine("0110")
status = animate_run(tm, max_steps=200, delay=0.3)
print("Final status:", status)
```

* Tape 1: input.
* Tape 2: used for marks.
* Accepts if the string is a palindrome, rejects by **lack of transitions**.

---

### 2. Language aⁿ bⁿ cⁿ (1 tape)

`mtm.examples.abc_equal` implements a 1-tape TM for the language:

> L = { aⁿ bⁿ cⁿ | n ≥ 1 }

```python
from mtm.examples import build_abc_equal_machine
from mtm import animate_run

tm = build_abc_equal_machine("aabbcc")  # n = 2
status = animate_run(tm, max_steps=200, delay=0.3)
print("Final status:", status)
```

The machine:

1. Searches for the next unmarked `a`, marks it as `X`.
2. Searches for the next unmarked `b`, marks it as `Y`.
3. Searches for the next unmarked `c`, marks it as `Z`.
4. Returns to the left end and repeats.
5. Accepts if no `a` remain and there are no extra `b` or `c`.

---

### 3. Language w%w (1 tape)

`mtm.examples.ww_delimiter` implements a 1-tape TM for:

> L = { w % w | w ∈ {a, b}* }

```python
from mtm.examples import build_ww_delimiter_machine
from mtm import animate_run

tm = build_ww_delimiter_machine("abba%abba")
status = animate_run(tm, max_steps=400, delay=0.3)
print("Final status:", status)
```

The machine:

1. Scans the first `w`, marking letters as `X` or `Y`.
2. For each marked letter before `%`, it looks for a matching unmarked letter after `%`.
3. When there are no unmarked letters before `%`, it checks that no unmarked letters remain after `%`.
4. Accepts if and only if the two halves are identical.

---

## Defining your own machines

You have two main options:

### Option A: Use `MultiTapeTuringMachine` directly

This is the most direct, flexible way.

```python
from mtm import MultiTapeTuringMachine, Direction

states = {"q0", "q_accept"}
input_alphabet = {"0", "1"}
tape_alphabet = {"0", "1", "_"}
blank = "_"

transitions = {
    # Toy example: move right while reading 0/1, accept on blank
    ("q0", ("0",)): ("q0", ("0",), (Direction.RIGHT,)),
    ("q0", ("1",)): ("q0", ("1",), (Direction.RIGHT,)),
    ("q0", ("_",)): ("q_accept", ("_",), (Direction.STAY,)),
}

tm = MultiTapeTuringMachine(
    states=states,
    input_alphabet=input_alphabet,
    tape_alphabet=tape_alphabet,
    blank=blank,
    transitions=transitions,
    start_state="q0",
    accept_states={"q_accept"},
    reject_states=set(),
    num_tapes=1,
    initial_inputs=["0101"],
)
```

---

### Option B: Subclass `TuringMachineDefinition`

Use this if you want a **reusable library model** that you can instantiate many times with different inputs (similar to the examples).

```python
from __future__ import annotations
from typing import Dict, Set

from mtm import TuringMachineDefinition, MultiTapeTuringMachine, Direction
from mtm.machine import State, Symbol, TransitionKey, TransitionValue


class MyToyDefinition(TuringMachineDefinition):
    """
    Example of a custom 1-tape TM definition.
    Accepts any string of 0/1 that ends in 1.
    """

    def __init__(self) -> None:
        states: Set[State] = {"q0", "q_accept", "q_reject"}
        input_alphabet: Set[Symbol] = {"0", "1"}
        tape_alphabet: Set[Symbol] = {"0", "1", "_"}
        blank: Symbol = "_"

        transitions: Dict[TransitionKey, TransitionValue] = {
            ("q0", ("0",)): ("q0", ("0",), (Direction.RIGHT,)),
            ("q0", ("1",)): ("q0", ("1",), (Direction.RIGHT,)),
            # On blank, last symbol was 1 if the head is to the right of a 1
            # (here, for simplicity, we just accept on blank)
            ("q0", ("_",)): ("q_accept", ("_",), (Direction.STAY,)),
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


# Helper function, similar to the ones in mtm.examples
def build_my_toy_machine(input_string: str) -> MultiTapeTuringMachine:
    definition = MyToyDefinition()
    return definition.create_machine(initial_inputs=[input_string])
```

Usage:

```python
from my_module import build_my_toy_machine
from mtm import animate_run

tm = build_my_toy_machine("0101")
animate_run(tm)
```

This pattern is recommended if you are building a **collection of Turing Machines** for a course, a paper, or a larger project.

---

## Project structure (for contributors)

```text
src/
  mtm/
    __init__.py
    tape.py               # Tape + Direction
    machine.py            # MultiTapeTuringMachine
    console.py            # animate_run for terminal animation
    definition.py         # TuringMachineDefinition
    examples/
      __init__.py
      palindrome_2tape.py # binary palindrome with 2 tapes
      abc_equal.py        # a^n b^n c^n
      ww_delimiter.py     # w%w
```

Local top-level demo scripts used for manual testing (not published) are kept outside `src/` and ignored by git (see `.gitignore`).

---

## License

```text
This project is licensed under the Apache License 2.0.

You are free to use, modify, and distribute this code (including in commercial and closed-source projects) as long as you keep the copyright and license notices, and respect the terms of the Apache 2.0 license.
```

---

## Roadmap / Ideas

* More built-in examples (unary addition, multiplication, etc.).
* Ready-made GUIs for step-by-step visualization.
* Export/import Turing Machines from JSON or YAML.
* Jupyter notebook helpers.

Contributions and suggestions are very welcome 🚀