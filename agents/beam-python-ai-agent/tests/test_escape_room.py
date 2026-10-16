"""Offline tests: no network, no API key, no model."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent import play  # noqa: E402
from escape_room import EscapeRoom, call_tool, is_prime, run_python, shift_letters  # noqa: E402


def test_same_seed_builds_the_same_rooms():
    assert [r.puzzle for r in EscapeRoom(11).rooms] == [r.puzzle for r in EscapeRoom(11).rooms]
    assert [r.puzzle for r in EscapeRoom(11).rooms] != [r.puzzle for r in EscapeRoom(12).rooms]


def test_answers_match_the_puzzles():
    for seed in range(20):
        archive, radio, vault = EscapeRoom(seed).rooms
        low, high = [int(word.strip(",.")) for word in archive.puzzle.split() if word.strip(",.").isdigit()]
        assert archive.answer == str(sum(is_prime(n) for n in range(low, high + 1)))

        message = radio.puzzle.split("The radio repeats: ")[1].split(". It was")[0]
        assert shift_letters(message, archive.answer, direction=-1).split()[-1] == radio.answer

        pairs = [clause.split(" when divided by ") for clause in vault.puzzle.split("leaves ")[1].rstrip(".").replace("and ", "").split(", ")]
        code = int(vault.answer)
        assert all(code % int(m) == int(r.split()[-1]) for r, m in pairs)
        assert not any(all(n % int(m) == int(r.split()[-1]) for r, m in pairs) for n in range(1, code))


def test_three_wrong_codes_lock_the_door():
    game = EscapeRoom(3)
    for _ in range(3):
        result = game.try_code("nope")
    assert result["correct"] is False and game.locked_out and game.over


def test_correct_codes_escape():
    game = EscapeRoom(3)
    for room in list(game.rooms):
        assert game.try_code(f" {room.answer.lower()} ")["correct"]
    assert game.escaped and game.wrong_codes == 0


def test_sandbox_runs_code_without_the_api_key(monkeypatch):
    monkeypatch.setenv("NEBIUS_API_KEY", "do-not-leak")
    result = run_python("import os\nprint(6 * 7, os.environ.get('NEBIUS_API_KEY'))")
    assert result == {"exit_code": 0, "stdout": "42 None\n", "stderr": ""}


def test_sandbox_times_out():
    assert "Timed out" in run_python("while True: pass", timeout=0.5)["stderr"]


def test_unknown_tool_is_reported_not_raised():
    reply = json.loads(call_tool(EscapeRoom(1), "bash", '{"command": "ls"}'))
    assert "no tool named 'bash'" in reply["error"]


class FakeClient:
    """Plays a perfect game: look, then each correct code, then a final answer."""

    def __init__(self, seed):
        answers = [room.answer for room in EscapeRoom(seed).rooms]
        self.script = [("look", {})] + [("try_code", {"code": a}) for a in answers] + [None]
        self.requests = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.requests.append(json.loads(json.dumps(kwargs["messages"])))
        step = self.script[len(self.requests) - 1]
        tool_calls = None
        if step:
            name, args = step
            call_id = f"call_{len(self.requests)}"
            tool_calls = [SimpleNamespace(id=call_id, function=SimpleNamespace(name=name, arguments=json.dumps(args)))]
        message = SimpleNamespace(
            content=None if step else "I escaped.",
            tool_calls=tool_calls,
            reasoning_content=f"thinking {len(self.requests)}",
        )
        usage = SimpleNamespace(
            prompt_tokens=100,
            completion_tokens=20,
            completion_tokens_details=SimpleNamespace(reasoning_tokens=15),
        )
        return SimpleNamespace(choices=[SimpleNamespace(message=message, finish_reason="stop")], usage=usage)


def test_loop_sends_reasoning_and_tool_ids_back():
    client = FakeClient(seed=5)
    run = play(client, seed=5, prices=(0.25e-6, 1e-6), log=lambda line: None)

    assert run["escaped"] and run["final"] == "I escaped." and run["tool_calls"] == 4
    assert run["prompt_tokens"] == 500 and run["reasoning_tokens"] == 75
    assert run["cost_usd"] == round(500 * 0.25e-6 + 100 * 1e-6, 5)

    second = client.requests[1]
    assistant, tool = second[-2], second[-1]
    assert assistant["reasoning_content"] == "thinking 1"
    assert tool["role"] == "tool" and tool["tool_call_id"] == assistant["tool_calls"][0]["id"]
