"""A seeded three-room escape room that a model solves through tool calls.

The game is deterministic for a given seed and knows its own answers, so every
run can be scored without a human or a judge model.
"""

from __future__ import annotations

import json
import random
import subprocess
import sys
import tempfile
from dataclasses import dataclass

WORDS = ["ORBIT", "LANTERN", "QUARTZ", "HARBOR", "MERIDIAN", "FALCON", "GLACIER", "NEBULA", "COMPASS", "TIMBER"]
OUTPUT_LIMIT = 4000


@dataclass(frozen=True)
class Room:
    name: str
    description: str
    puzzle: str
    answer: str


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    factor = 3
    while factor * factor <= n:
        if n % factor == 0:
            return False
        factor += 2
    return True


def shift_letters(text: str, digits: str, direction: int = 1) -> str:
    """Shift each letter by the next digit of `digits`, cycling and skipping spaces."""
    out, position = [], 0
    for char in text:
        if char.isalpha():
            step = int(digits[position % len(digits)]) * direction
            out.append(chr((ord(char) - 65 + step) % 26 + 65))
            position += 1
        else:
            out.append(char)
    return "".join(out)


def archive(rng: random.Random) -> Room:
    low = rng.randrange(20_000, 90_000, 100)
    high = low + rng.randrange(400, 900, 50)
    count = sum(1 for n in range(low, high + 1) if is_prime(n))
    return Room(
        name="The Archive",
        description="Shelves of number-theory ledgers. A brass keypad glows beside the only door.",
        puzzle=f"The keypad code is how many prime numbers lie between {low} and {high}, inclusive.",
        answer=str(count),
    )


def radio_room(rng: random.Random, archive_code: str) -> Room:
    word = rng.choice(WORDS)
    message = shift_letters(f"THE DOOR OPENS FOR THOSE WHO SAY {word}", archive_code)
    return Room(
        name="The Radio Room",
        description="A shortwave set crackles, repeating the same line over and over.",
        puzzle=(
            f"The radio repeats: {message}. It was enciphered by shifting each letter forward "
            "in the alphabet by the next digit of the Archive keypad code, cycling through the "
            "digits and skipping spaces. The code for this door is the last word of the decoded line."
        ),
        answer=word,
    )


def vault(rng: random.Random) -> Room:
    moduli = rng.sample([53, 59, 61, 67, 71, 73, 79, 83, 89, 97], 3)
    remainders = [rng.randrange(1, m) for m in moduli]
    code = next(n for n in range(1, 10**7) if all(n % m == r for m, r in zip(moduli, remainders)))
    clauses = [f"remainder {r} when divided by {m}" for m, r in zip(moduli, remainders)]
    return Room(
        name="The Vault",
        description="A steel door with a combination dial. Daylight shows under it.",
        puzzle=f"The combination is the smallest positive integer that leaves {', '.join(clauses[:2])}, and {clauses[2]}.",
        answer=str(code),
    )


class EscapeRoom:
    def __init__(self, seed: int, attempts_per_room: int = 3):
        rng = random.Random(seed)
        first = archive(rng)
        self.rooms = [first, radio_room(rng, first.answer), vault(rng)]
        self.attempts_per_room = attempts_per_room
        self.current = 0
        self.attempts_left = attempts_per_room
        self.wrong_codes = 0
        self.escaped = False
        self.locked_out = False

    @property
    def over(self) -> bool:
        return self.escaped or self.locked_out

    def look(self) -> dict:
        if self.escaped:
            return {"status": "escaped", "message": "You are outside. There are no more doors."}
        if self.locked_out:
            return {"status": "locked_out", "message": "The doors have sealed. The game is over."}
        room = self.rooms[self.current]
        return {
            "room": f"{self.current + 1} of {len(self.rooms)}",
            "name": room.name,
            "description": room.description,
            "puzzle": room.puzzle,
            "attempts_left": self.attempts_left,
        }

    def try_code(self, code: str) -> dict:
        if self.over:
            return self.look()
        room = self.rooms[self.current]
        if code.strip().strip("\"'").upper() == room.answer:
            self.current += 1
            self.attempts_left = self.attempts_per_room
            if self.current == len(self.rooms):
                self.escaped = True
                return {"correct": True, "message": "The vault swings open onto daylight. You escaped."}
            return {"correct": True, "message": f"The door opens into {self.rooms[self.current].name}. Call look."}
        self.wrong_codes += 1
        self.attempts_left -= 1
        if self.attempts_left == 0:
            self.locked_out = True
            return {"correct": False, "message": "Wrong code. The doors seal. The game is over."}
        return {"correct": False, "message": "Wrong code.", "attempts_left": self.attempts_left}


def run_python(code: str, timeout: float = 10.0) -> dict:
    """Run code in a child interpreter with an empty environment and a time limit.

    The child cannot read your API key and cannot run forever. It is not a
    security boundary: it can still reach the network and your files, so run
    model-written code in a container or VM before pointing this at anything
    you care about.
    """
    with tempfile.TemporaryDirectory() as workdir:
        try:
            done = subprocess.run(
                [sys.executable, "-I", "-"],
                input=code,
                cwd=workdir,
                env={},
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return {"exit_code": None, "stdout": "", "stderr": f"Timed out after {timeout:g} seconds."}
    return {"exit_code": done.returncode, "stdout": done.stdout[-OUTPUT_LIMIT:], "stderr": done.stderr[-OUTPUT_LIMIT:]}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "look",
            "description": "Describe the room you are in, its puzzle, and how many code attempts are left.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": "Run a self-contained Python 3 script and return its exit code, stdout, and stderr. Print what you need to see.",
            "parameters": {
                "type": "object",
                "properties": {"code": {"type": "string", "description": "The Python source to run."}},
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "try_code",
            "description": "Enter a code on the current door. A wrong code costs one of the door's three attempts.",
            "parameters": {
                "type": "object",
                "properties": {"code": {"type": "string", "description": "The code to enter."}},
                "required": ["code"],
            },
        },
    },
]


def call_tool(game: EscapeRoom, name: str, arguments: str | None) -> str:
    try:
        args = json.loads(arguments or "{}")
    except json.JSONDecodeError:
        return json.dumps({"error": "Arguments were not valid JSON."})
    if name == "look":
        result = game.look()
    elif name == "run_python":
        result = run_python(str(args.get("code", "")))
    elif name == "try_code":
        result = game.try_code(str(args.get("code", "")))
    else:
        result = {"error": f"There is no tool named {name!r}. Use look, run_python, or try_code."}
    return json.dumps(result)
