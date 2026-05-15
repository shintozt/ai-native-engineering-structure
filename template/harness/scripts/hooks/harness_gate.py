#!/usr/bin/env python3
"""Codex 和 Claude Code 共用的轻量 Harness 门禁。

本脚本刻意保持保守且无第三方依赖。它不是安全边界，而是项目工作流护栏。

用途：
- prompt：提醒 AI 先读工程入口、上下文和当前 Track。
- pre-edit：代码类编辑前检查当前 Track 是否已有非空 spec.md。
- stop：结束前提醒验证和归档。

调用方：
- Codex / Claude Code Hook。
- 人工命令。

项目化要求：
- 按真实项目调整 SRC_LIKE_PREFIXES 和 SRC_LIKE_FILES。
- 当前 Track 默认由 harness/state/active-track.md 指定；如团队有其他 Track 选择机制，应改写 _current_track()。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path.cwd()
TRACKS = ROOT / "specs" / "tracks"
INIT_STATUS = ROOT / "harness" / "state" / "init-status.md"
ACTIVE_TRACK = ROOT / "harness" / "state" / "active-track.md"
SRC_LIKE_PREFIXES = ("src/", "include/", "tests/", "proto/", "api/")
SRC_LIKE_FILES = ("CMakeLists.txt", "package.json", "pyproject.toml", "go.mod")
TRACK_PREFIX = "specs/tracks/"
INIT_ALLOWED_PREFIXES = (
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "constitution.md",
    "context/",
    "harness/",
)


def _read_active_track() -> dict[str, str] | None:
    if not ACTIVE_TRACK.exists():
        return None
    try:
        text = ACTIVE_TRACK.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    fields: dict[str, str] = {}
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("- ") and ("：" in s or ":" in s):
            body = s[2:]
            key, sep, value = body.partition("：")
            if not sep:
                key, sep, value = body.partition(":")
            if sep:
                fields[key.strip()] = value.strip()
    return fields or None


def _active_track_path() -> str | None:
    info = _read_active_track()
    if not info or info.get("状态") != "active":
        return None
    path = info.get("Track 路径", "").strip().rstrip("/")
    return path or None


def _read_stdin_json() -> dict[str, Any]:
    try:
        raw = sys.stdin.read()
    except Exception:
        return {}
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def _is_nonempty(path: Path) -> bool:
    try:
        return path.exists() and bool(path.read_text(encoding="utf-8").strip())
    except UnicodeDecodeError:
        return False


def _current_track() -> Path | None:
    env_track = os.environ.get("HARNESS_TRACK")
    if env_track:
        track = Path(env_track)
        if not track.is_absolute():
            track = ROOT / track
        if track.is_dir():
            return track
    active = _active_track_path()
    if not active:
        return None
    track = ROOT / active
    if track.is_dir():
        return track
    return None


def _has_current_track_spec() -> bool:
    track = _current_track()
    if track is None:
        return False
    return _is_nonempty(track / "spec.md")


def _init_completed() -> bool:
    if not INIT_STATUS.exists():
        return True
    try:
        text = INIT_STATUS.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    if "## 状态" not in text:
        return False
    status_block = text.split("## 状态", 1)[1].split("##", 1)[0]
    status_lines = [line.strip() for line in status_block.splitlines() if line.strip()]
    return bool(status_lines) and status_lines[0] == "已完成"


def _looks_like_code_edit(payload: dict[str, Any]) -> bool:
    text = json.dumps(payload, ensure_ascii=False)
    return any(prefix in text for prefix in SRC_LIKE_PREFIXES) or any(
        name in text for name in SRC_LIKE_FILES
    )


def _looks_like_track_edit(payload: dict[str, Any]) -> bool:
    text = json.dumps(payload, ensure_ascii=False)
    return TRACK_PREFIX in text


def _looks_like_init_allowed_edit(payload: dict[str, Any]) -> bool:
    text = json.dumps(payload, ensure_ascii=False)
    return any(prefix in text for prefix in INIT_ALLOWED_PREFIXES)


def _git_changed_files() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=ROOT,
            check=False,
            text=True,
            capture_output=True,
        )
    except FileNotFoundError:
        return []
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _has_code_changes() -> bool:
    for file_name in _git_changed_files():
        if file_name in SRC_LIKE_FILES:
            return True
        if file_name.startswith(SRC_LIKE_PREFIXES):
            return True
    return False


def _print_context_reminder() -> int:
    if not _init_completed():
        print(
            "Harness 初始化提醒：当前工程尚未完成新服务初始化。请先执行 "
            "`harness/sop/01-新服务初始化SOP.md`，完成 `harness/state/init-status.md` "
            "检查项后，再创建需求 Track 或编码。"
        )
    else:
        print(
            "Harness 提醒：规划或编辑前，请先阅读 AGENTS.md、constitution.md、"
            "context/INDEX.md，以及当前 specs/tracks/<需求名>/ 下的需求文件。"
        )
    return 0


def _pre_edit(payload: dict[str, Any]) -> int:
    if not _init_completed():
        if _looks_like_code_edit(payload) or _looks_like_track_edit(payload):
            print(
                "Harness 初始化门禁已阻断：新服务初始化未完成前，不允许创建需求 Track "
                "或修改业务代码。请先完成 harness/sop/01-新服务初始化SOP.md，"
                "并将 harness/state/init-status.md 状态改为已完成。",
                file=sys.stderr,
            )
            return 2
        if not _looks_like_init_allowed_edit(payload):
            print(
                "Harness 初始化提醒：当前只应修改入口文档、context 或 harness。",
                file=sys.stderr,
            )

    # 初始化已完成后的 track 锁检查
    if _looks_like_track_edit(payload):
        text = json.dumps(payload, ensure_ascii=False)
        active = _active_track_path()
        if active is None:
            print(
                "Harness Track 门禁已阻断：当前无 active track，不允许编辑 specs/tracks/ 下任何文件。"
                "请先运行 `python3 -B harness/scripts/lifecycle/track.py open <name>` 启动 track。",
                file=sys.stderr,
            )
            return 2
        if active and active not in text and (active + "/") not in text:
            print(
                f"Harness Track 门禁已阻断：当前 active track 是 {active}/，"
                "不允许编辑其他 track 的文件。要切换请先 close 当前 track。",
                file=sys.stderr,
            )
            return 2

    if _looks_like_code_edit(payload) and not _has_current_track_spec():
        print(
            "Harness 门禁已阻断：代码类编辑需要先存在当前 Track 的 spec.md，"
            "且内容非空。请先创建并确认 Spec。",
            file=sys.stderr,
        )
        return 2
    return 0


def _stop() -> int:
    if not _init_completed():
        print(
            "Harness 初始化结束提醒：当前工程尚未完成新服务初始化。"
            "改为已完成前，请先运行 `python3 -B harness/scripts/lifecycle/check-init-readiness.py`，"
            "并在 `harness/state/init-status.md` 记录自动检查结果和人工确认。"
        )
    if _has_code_changes():
        print(
            "Harness 结束提醒：检测到代码变更。声称完成前，请运行 "
            "`bash harness/scripts/verify/verify-template.sh`，或说明无法运行的原因。"
        )
        track = _current_track()
        if track is None:
            print("Harness 归档提醒：未找到当前需求 Track。")
        elif not _is_nonempty(track / "acceptance.md"):
            print(
                "Harness 归档提醒：当前 Track 的 acceptance.md 不存在或为空："
                f"{track / 'acceptance.md'}"
            )
    return 0


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "prompt"
    payload = _read_stdin_json()

    if mode == "prompt":
        return _print_context_reminder()
    if mode == "pre-edit":
        return _pre_edit(payload)
    if mode == "stop":
        return _stop()

    print(f"未知 Harness 门禁模式：{mode}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
