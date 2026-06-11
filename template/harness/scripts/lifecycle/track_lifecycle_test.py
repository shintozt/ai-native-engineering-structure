#!/usr/bin/env python3
"""track.py 的轻量回归测试。

这些测试只验证母版级生命周期行为，不依赖具体业务技术栈。
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


TEMPLATE_ROOT = Path(__file__).resolve().parents[3]
TRACK_SCRIPT = TEMPLATE_ROOT / "harness" / "scripts" / "lifecycle" / "track.py"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(TRACK_SCRIPT), *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def make_project() -> Path:
    root = Path(tempfile.mkdtemp(prefix="track-lifecycle-test-"))
    write(root / "AGENTS.md", "# AGENTS\n")
    write(root / "harness" / "state" / "init-status.md", "# Init\n\n## 状态\n\n已完成\n")
    shutil.copytree(TEMPLATE_ROOT / "specs" / "templates", root / "specs" / "templates")
    write(root / "harness" / "scripts" / "verify" / "verify-template.sh", "#!/usr/bin/env bash\nexit 0\n")
    write(root / "harness" / "scripts" / "verify" / "check-layer-boundaries-template.sh", "#!/usr/bin/env bash\nexit 0\n")
    os.chmod(root / "harness" / "scripts" / "verify" / "verify-template.sh", 0o755)
    os.chmod(root / "harness" / "scripts" / "verify" / "check-layer-boundaries-template.sh", 0o755)
    return root


def approve(path: Path, name: str = "tester") -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace("- approved-by:", f"- approved-by: {name}")
    text = text.replace("- approved-at:", "- approved-at: 2026-06-10T00:00:00")
    path.write_text(text, encoding="utf-8")


def current_track(root: Path) -> Path:
    state = (root / "harness" / "state" / "active-track.md").read_text(encoding="utf-8")
    for line in state.splitlines():
        if line.startswith("- Track 路径"):
            return root / line.split("：", 1)[1].strip()
    raise AssertionError("active-track.md 缺少 Track 路径")


def test_open_only_creates_proposal() -> None:
    root = make_project()
    try:
        result = run(root, "open", "demo-feature", "--no-branch")
        assert result.returncode == 0, result.stderr
        track = current_track(root)
        assert (track / "proposal.md").exists()
        assert (track / "notes.md").exists()
        assert not (track / "spec.md").exists()
        assert not (track / "design.md").exists()
        assert not (track / "tasks.md").exists()
    finally:
        shutil.rmtree(root)


def test_next_stage_requires_approval() -> None:
    root = make_project()
    try:
        assert run(root, "open", "demo-feature", "--no-branch").returncode == 0
        blocked = run(root, "next-stage")
        assert blocked.returncode != 0
        track = current_track(root)
        approve(track / "proposal.md")
        ok = run(root, "next-stage")
        assert ok.returncode == 0, ok.stderr
        assert (track / "spec.md").exists()
    finally:
        shutil.rmtree(root)


def test_finish_task_lays_archive_without_commit() -> None:
    root = make_project()
    try:
        assert run(root, "open", "demo-feature", "--no-branch").returncode == 0
        track = current_track(root)
        for stage_file in ("proposal.md", "spec.md", "design.md", "tasks.md"):
            if not (track / stage_file).exists():
                approve(track / {"spec.md": "proposal.md", "design.md": "spec.md", "tasks.md": "design.md"}[stage_file])
                assert run(root, "next-stage").returncode == 0
            approve(track / stage_file)
        result = run(root, "finish-task", "--task", "T1")
        assert result.returncode == 0, result.stderr
        result = run(root, "finish-task", "--task", "T2")
        assert result.returncode == 0, result.stderr
        tasks = (track / "tasks.md").read_text(encoding="utf-8")
        assert "- 状态：Done" in tasks
        assert (track / "acceptance.md").exists()
        assert (track / "learnings.md").exists()
    finally:
        shutil.rmtree(root)


def test_revise_stage_clears_downstream_approvals() -> None:
    root = make_project()
    try:
        assert run(root, "open", "demo-feature", "--no-branch").returncode == 0
        track = current_track(root)
        approve(track / "proposal.md")
        assert run(root, "next-stage").returncode == 0
        approve(track / "spec.md")
        assert run(root, "next-stage").returncode == 0
        approve(track / "design.md")
        result = run(root, "revise-stage", "spec", "--confirmed-by", "tester")
        assert result.returncode == 0, result.stderr
        assert "- approved-by:" in (track / "spec.md").read_text(encoding="utf-8")
        assert "- approved-by: tester" not in (track / "spec.md").read_text(encoding="utf-8")
        assert "- approved-by: tester" not in (track / "design.md").read_text(encoding="utf-8")
    finally:
        shutil.rmtree(root)


def main() -> int:
    tests = [
        test_open_only_creates_proposal,
        test_next_stage_requires_approval,
        test_finish_task_lays_archive_without_commit,
        test_revise_stage_clears_downstream_approvals,
    ]
    for test in tests:
        test()
        print(f"[PASS] {test.__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
