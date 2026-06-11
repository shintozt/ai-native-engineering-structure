#!/usr/bin/env python3
"""harness_gate.py 的轻量回归测试。"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


TEMPLATE_ROOT = Path(__file__).resolve().parents[3]
GATE_SCRIPT = TEMPLATE_ROOT / "harness" / "scripts" / "hooks" / "harness_gate.py"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_gate(root: Path, mode: str, payload: dict) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(GATE_SCRIPT), mode],
        cwd=root,
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        capture_output=True,
        check=False,
    )


def make_project() -> Path:
    root = Path(tempfile.mkdtemp(prefix="harness-gate-test-"))
    write(root / "AGENTS.md", "# AGENTS\n")
    write(root / "harness" / "state" / "init-status.md", "# Init\n\n## 状态\n\n已完成\n")
    track = root / "specs" / "tracks" / "2026-06-10-demo"
    track.mkdir(parents=True)
    write(
        root / "harness" / "state" / "active-track.md",
        "# Active Track\n\n## 元数据\n\n"
        "- 状态：active\n"
        "- Track 路径：specs/tracks/2026-06-10-demo\n"
        "- Track slug：2026-06-10-demo\n",
    )
    return root


def approved() -> str:
    return "# Doc\n\n## 定稿戳\n\n- approved-by: tester\n- approved-at: 2026-06-10T00:00:00\n"


def draft() -> str:
    return "# Doc\n\n## 定稿戳\n\n- approved-by:\n- approved-at:\n"


def test_read_only_shell_allowed_without_track_docs() -> None:
    root = make_project()
    try:
        result = run_gate(root, "pre-edit", {"cmd": "rg TODO src include"})
        assert result.returncode == 0, result.stderr
    finally:
        shutil.rmtree(root)


def test_stage_edit_requires_previous_approval() -> None:
    root = make_project()
    try:
        track = root / "specs" / "tracks" / "2026-06-10-demo"
        write(track / "proposal.md", draft())
        result = run_gate(root, "pre-edit", {"path": "specs/tracks/2026-06-10-demo/spec.md"})
        assert result.returncode != 0
        write(track / "proposal.md", approved())
        ok = run_gate(root, "pre-edit", {"path": "specs/tracks/2026-06-10-demo/spec.md"})
        assert ok.returncode == 0, ok.stderr
    finally:
        shutil.rmtree(root)


def test_code_edit_requires_all_stage_approvals() -> None:
    root = make_project()
    try:
        track = root / "specs" / "tracks" / "2026-06-10-demo"
        write(track / "proposal.md", approved())
        write(track / "spec.md", approved())
        write(track / "design.md", approved())
        write(track / "tasks.md", draft())
        blocked = run_gate(root, "pre-edit", {"path": "src/domain/foo.cpp"})
        assert blocked.returncode != 0
        write(track / "tasks.md", approved())
        ok = run_gate(root, "pre-edit", {"path": "src/domain/foo.cpp"})
        assert ok.returncode == 0, ok.stderr
    finally:
        shutil.rmtree(root)


def test_approved_stage_requires_revise_stage() -> None:
    root = make_project()
    try:
        track = root / "specs" / "tracks" / "2026-06-10-demo"
        write(track / "proposal.md", approved())
        blocked = run_gate(root, "pre-edit", {"path": "specs/tracks/2026-06-10-demo/proposal.md"})
        assert blocked.returncode != 0
    finally:
        shutil.rmtree(root)


def main() -> int:
    tests = [
        test_read_only_shell_allowed_without_track_docs,
        test_stage_edit_requires_previous_approval,
        test_code_edit_requires_all_stage_approvals,
        test_approved_stage_requires_revise_stage,
    ]
    for test in tests:
        test()
        print(f"[PASS] {test.__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
