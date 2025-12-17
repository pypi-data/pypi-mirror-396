# src/mtm/console.py
import os
import time
from typing import Optional

from .machine import MultiTapeTuringMachine


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def animate_run(
    machine: MultiTapeTuringMachine,
    max_steps: int = 100,
    delay: float = 0.25,
    show_final: bool = True,
) -> str:
    """
    Run the machine and show an animation of the heads moving on the tapes.

    - max_steps: safety limit to avoid infinite loops
    - delay: time (in seconds) to wait between frames
    - show_final: if True, show a final summary screen

    Returns the final status: 'ACCEPT', 'REJECT', 'HALT' or 'RUNNING'.
    """
    status: str = "RUNNING"

    while status == "RUNNING" and machine.step_count < max_steps:
        clear_screen()

        # Show current configuration BEFORE taking the step
        print(f"Multi-tape Turing Machine")
        print("=" * 40)
        print(f"Step : {machine.step_count}")
        print(f"State: {machine.current_state}\n")

        for i, tape in enumerate(machine.tapes):
            print(f"Tape {i}: {tape}")

        print("\n(press Ctrl+C to stop)")
        time.sleep(delay)

        # Advance one step
        status = machine.step()

    if show_final:
        clear_screen()
        print("Final configuration")
        print("=" * 40)
        print(f"Step : {machine.step_count}")
        print(f"State: {machine.current_state}\n")

        for i, tape in enumerate(machine.tapes):
            print(f"Tape {i}: {tape}")

        print(f"\nFinal status: {status}")

    return status
