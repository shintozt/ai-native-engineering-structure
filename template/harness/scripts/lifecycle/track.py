#!/usr/bin/env python3
"""Track 生命周期命令。

Commands:
    track.py open <name>                创建新 track 并标记为 active（含 git branch）
    track.py finish-task [--task <id>]  完成当前任务（验证 + commit + push）
                          [--message <m>]
    track.py close [--abort] [--reason] 关闭当前 active track
    track.py status                     查看当前 active track 状态

Examples:
    python3 -B harness/scripts/lifecycle/track.py open user-profile-cache-port
    python3 -B harness/scripts/lifecycle/track.py finish-task --task T1
    python3 -B harness/scripts/lifecycle/track.py close
    python3 -B harness/scripts/lifecycle/track.py close --abort --reason "需求变更"

约束：
- init-status 必须为已完成才能 open。
- 同时仅允许 1 个 active track；close 后才能 open 下一个。
- finish-task 必须通过 verify-template.sh 和 check-layer-boundaries 才会 commit。
- 验证失败时阻断 commit，保留工作区供修复。
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def find_project_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    while True:
        if (current / "AGENTS.md").is_file():
            return current
        if current == current.parent:
            print(
                "WARN: 未找到 AGENTS.md，回退到 cwd 作为项目根。建议从项目根目录运行。",
                file=sys.stderr,
            )
            return Path.cwd().resolve()
        current = current.parent


ROOT = find_project_root()
ACTIVE_TRACK_FILE = ROOT / "harness" / "state" / "active-track.md"
TRACKS_DIR = ROOT / "specs" / "tracks"
TEMPLATES_DIR = ROOT / "specs" / "templates"
INIT_STATUS = ROOT / "harness" / "state" / "init-status.md"

TRACK_TEMPLATES = (
    "proposal-template.md",
    "spec-template.md",
    "design-template.md",
    "tasks-template.md",
    "notes-template.md",
    "acceptance-template.md",
    "learnings-template.md",
)

VERIFY_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("bash", "harness/scripts/verify/verify-template.sh"),
    ("bash", "harness/scripts/verify/check-layer-boundaries-template.sh"),
)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def track_name_from_slug(slug: str) -> str:
    if re.match(r"^\d{4}-\d{2}-\d{2}-", slug):
        return slug[11:]
    return slug


def fail(message: str) -> None:
    print(f"WHAT: {message}", file=sys.stderr)
    sys.exit(1)


def fail_with_fix(what: str, why: str, how: str) -> None:
    print(f"WHAT: {what}", file=sys.stderr)
    print(f"WHY: {why}", file=sys.stderr)
    print(f"HOW: {how}", file=sys.stderr)
    sys.exit(1)


# ---------- active-track.md 解析与写入 ----------

def parse_active_track() -> dict[str, str] | None:
    if not ACTIVE_TRACK_FILE.exists():
        return None
    text = ACTIVE_TRACK_FILE.read_text(encoding="utf-8")
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
    return fields if fields else None


def is_active() -> bool:
    info = parse_active_track()
    return info is not None and info.get("状态") == "active"


def write_active_track(track_relative: Path, slug: str, current_task: str, base_branch: str) -> None:
    ACTIVE_TRACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Active Track",
        "",
        "本文件是当前 active track 的**本地指针**，已在 `.gitignore` 中排除。",
        "多人协作时各自维护，不共享。",
        "",
        "## 元数据",
        "",
        "- 状态：active",
        f"- Track 路径：{track_relative}",
        f"- Track slug：{slug}",
        f"- Base 分支：{base_branch}",
        f"- 启动时间：{now_iso()}",
        f"- 当前任务：{current_task}",
        "",
        "## 历史",
        "",
        f"- {now_iso()} open",
        "",
    ]
    ACTIVE_TRACK_FILE.write_text("\n".join(lines), encoding="utf-8")


def append_history(action: str) -> None:
    if not ACTIVE_TRACK_FILE.exists():
        return
    text = ACTIVE_TRACK_FILE.read_text(encoding="utf-8")
    if "## 历史" not in text:
        text = text.rstrip() + "\n\n## 历史\n\n"
    text = text.rstrip() + f"\n- {now_iso()} {action}\n"
    ACTIVE_TRACK_FILE.write_text(text, encoding="utf-8")


def set_field(key: str, value: str) -> None:
    if not ACTIVE_TRACK_FILE.exists():
        return
    text = ACTIVE_TRACK_FILE.read_text(encoding="utf-8")
    text = re.sub(
        rf"^- {re.escape(key)}[：:].*$",
        f"- {key}：{value}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    ACTIVE_TRACK_FILE.write_text(text, encoding="utf-8")


def mark_empty() -> None:
    """把 active-track 标为 empty（保留历史）。"""
    if not ACTIVE_TRACK_FILE.exists():
        return
    set_field("状态", "empty")
    set_field("当前任务", "")


# ---------- init-status 检查 ----------

def init_completed() -> bool:
    if not INIT_STATUS.exists():
        return False
    text = INIT_STATUS.read_text(encoding="utf-8")
    if "## 状态" not in text:
        return False
    block = text.split("## 状态", 1)[1].split("##", 1)[0]
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    return bool(lines) and lines[0] == "已完成"


# ---------- tasks.md 解析 ----------

TASK_HEADING_RE = re.compile(r"^###\s+(Task\s+\d+|T\d+)\s*[：:]\s*(.*?)\s*$", re.IGNORECASE)


def normalize_task_id(raw: str) -> str:
    s = raw.strip()
    m = re.match(r"^Task\s+(\d+)$", s, re.IGNORECASE)
    if m:
        return f"T{m.group(1)}"
    return s


def parse_tasks(track_path: Path) -> list[dict[str, str]]:
    tasks_file = track_path / "tasks.md"
    if not tasks_file.exists():
        return []
    text = tasks_file.read_text(encoding="utf-8")
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in text.splitlines():
        m = TASK_HEADING_RE.match(line)
        if m:
            if current:
                entries.append(current)
            raw_id = m.group(1).strip()
            current = {
                "raw_id": raw_id,
                "id": normalize_task_id(raw_id),
                "name": m.group(2).strip(),
                "status": "",
            }
            continue
        if current is None:
            continue
        sm = re.match(r"^\s*-\s*状态\s*[：:]\s*(.*?)\s*$", line)
        if sm:
            current["status"] = sm.group(1).strip()
    if current:
        entries.append(current)
    return entries


def first_undone(track_path: Path) -> dict[str, str] | None:
    for task in parse_tasks(track_path):
        if task["status"].lower() not in ("done", "completed", "已完成"):
            return task
    return None


def mark_task_done(track_path: Path, raw_id: str) -> None:
    tasks_file = track_path / "tasks.md"
    if not tasks_file.exists():
        return
    text = tasks_file.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    in_target = False
    status_written = False
    for line in lines:
        m = TASK_HEADING_RE.match(line.rstrip("\n"))
        if m:
            # 离开上一个 task：若在目标 task 内且未写 status，补一行
            if in_target and not status_written:
                out.append("- 状态：Done\n")
            in_target = m.group(1).strip() == raw_id
            status_written = False
            out.append(line)
            continue
        if in_target and re.match(r"^\s*-\s*状态\s*[：:]", line):
            out.append("- 状态：Done\n")
            status_written = True
            continue
        out.append(line)
    if in_target and not status_written:
        out.append("- 状态：Done\n")
    tasks_file.write_text("".join(out), encoding="utf-8")


# ---------- git helpers ----------

def git(*args: str, check: bool = False, capture: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=capture,
        check=check,
    )


def git_has_staged_changes() -> bool:
    return git("diff", "--cached", "--quiet").returncode != 0


def git_has_changes() -> bool:
    return bool(git("status", "--porcelain").stdout.strip())


def current_git_branch() -> str:
    result = git("branch", "--show-current")
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


# ---------- 验证 ----------

def run_verification() -> bool:
    for cmd in VERIFY_COMMANDS:
        print(f"$ {' '.join(cmd)}", file=sys.stderr)
        result = subprocess.run(cmd, cwd=ROOT, text=True)
        if result.returncode != 0:
            return False
    return True


# ---------- 命令: open ----------

def cmd_open(args: argparse.Namespace) -> None:
    name = args.name
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
        fail(f"track 名 '{name}' 不合法（只允许小写字母、数字、横线，开头非横线）。")

    if not init_completed():
        fail_with_fix(
            "初始化未完成，无法启动 track。",
            "harness/state/init-status.md 状态必须为已完成。",
            "先执行 harness/sop/01-新服务初始化SOP.md，跑 check-init-readiness.py 通过。",
        )
    if is_active():
        info = parse_active_track() or {}
        fail_with_fix(
            f"已有 active track：{info.get('Track 路径', '<unknown>')}",
            "同时只允许 1 个 active track。",
            "先 close 当前 track（python3 -B harness/scripts/lifecycle/track.py close），再 open 新的。",
        )

    today = datetime.now().strftime("%Y-%m-%d")
    slug = f"{today}-{name}"
    track_path = TRACKS_DIR / slug

    if track_path.exists():
        fail(f"track 目录已存在：{track_path}")

    TRACKS_DIR.mkdir(parents=True, exist_ok=True)
    track_path.mkdir(parents=True)
    for template in TRACK_TEMPLATES:
        src = TEMPLATES_DIR / template
        dst = track_path / template.replace("-template", "")
        if src.exists():
            shutil.copyfile(src, dst)
        else:
            print(f"WARN: 模板 {template} 不存在，跳过", file=sys.stderr)

    base_branch = current_git_branch() or "main"

    if not args.no_branch:
        branch = f"track/{name}"
        result = git("checkout", "-b", branch)
        if result.returncode != 0:
            print(
                f"WARN: git checkout -b {branch} 失败：{result.stderr.strip()}",
                file=sys.stderr,
            )
            print("继续 open track；如需独立分支，请手动切换。", file=sys.stderr)

    relative = track_path.relative_to(ROOT)
    first = first_undone(track_path)
    current_task = first["id"] if first else "T1"
    write_active_track(relative, slug, current_task, base_branch)

    print(f"已 open track: {relative}")
    print(f"slug: {slug}")
    if not args.no_branch:
        print(f"分支: track/{name}")
    print()
    print("下一步：填写 proposal.md → spec.md → design.md → tasks.md")


# ---------- 命令: finish-task ----------

def cmd_finish_task(args: argparse.Namespace) -> None:
    info = parse_active_track()
    if not info or info.get("状态") != "active":
        fail_with_fix(
            "没有 active track，无法 finish-task。",
            "active-track.md 状态不是 active。",
            "先 open 新 track，或检查 active-track.md 是否被误清。",
        )
    track_relative = info["Track 路径"]
    track_path = ROOT / track_relative
    slug = info["Track slug"]

    if args.task:
        normalized = normalize_task_id(args.task)
        candidates = [t for t in parse_tasks(track_path) if t["id"] == normalized]
        if not candidates:
            fail(f"task {args.task}（标准化为 {normalized}）不在 tasks.md 中。")
        task = candidates[0]
    else:
        first = first_undone(track_path)
        if not first:
            fail("所有 task 都已 Done。应该走 close 命令。")
        task = first

    print(f"== finish-task: {task['id']} {task['name']} ==", file=sys.stderr)

    if not run_verification():
        fail_with_fix(
            f"验证失败，task {task['id']} 未 commit。",
            "verify-template.sh 或 check-layer-boundaries 未通过。工作区保留以便修复。",
            f"修复后重新运行：python3 -B harness/scripts/lifecycle/track.py finish-task --task {task['id']}",
        )

    mark_task_done(track_path, task["raw_id"])

    if not git_has_changes():
        print("WARN: 没有改动需要 commit。仍标记 task 为 Done。", file=sys.stderr)
    else:
        add = git("add", "-A")
        if add.returncode != 0:
            fail(f"git add 失败：{add.stderr.strip()}")

        message_tail = args.message or task["name"]
        full = f"feat({slug}): {task['id']} {message_tail}"
        commit = git("commit", "-m", full)
        if commit.returncode != 0:
            fail(f"git commit 失败：{commit.stderr.strip()}")

        push = git("push", "-u", "origin", "HEAD")
        if push.returncode != 0:
            print(
                f"WARN: git push 失败：{push.stderr.strip()}",
                file=sys.stderr,
            )
            print("commit 已完成，请手动推送或检查 remote 配置。", file=sys.stderr)

    next_task = first_undone(track_path)
    if next_task:
        set_field("当前任务", next_task["id"])
    else:
        set_field("当前任务", "（全部 Done，可 close）")
    append_history(f"finish {task['id']}")

    print(f"task {task['id']} 完成，已 commit。")
    if next_task:
        print(f"下一个任务：{next_task['id']} {next_task['name']}")
    else:
        print("所有 task Done。请填写 acceptance.md 和 learnings.md 后 close。")


# ---------- 命令: close ----------

def cmd_close(args: argparse.Namespace) -> None:
    info = parse_active_track()
    if not info or info.get("状态") != "active":
        fail("没有 active track。")
    track_relative = info["Track 路径"]
    track_path = ROOT / track_relative
    slug = info["Track slug"]

    if args.abort:
        aborted = track_path / "aborted.md"
        aborted.write_text(
            f"# Aborted\n\n时间：{now_iso()}\n\n原因：{args.reason or '（未填写）'}\n",
            encoding="utf-8",
        )
        append_history(f"abort {slug}")
        mark_empty()
        print(f"track {slug} 已放弃。分支已保留：track/{track_name_from_slug(slug)}")
        return

    issues: list[str] = []

    acceptance = track_path / "acceptance.md"
    learnings = track_path / "learnings.md"
    if not (acceptance.exists() and acceptance.read_text(encoding="utf-8").strip()):
        issues.append("acceptance.md 不存在或为空。")
    if not (learnings.exists() and learnings.read_text(encoding="utf-8").strip()):
        issues.append("learnings.md 不存在或为空。")

    tasks = parse_tasks(track_path)
    undone = [
        f"{t['id']} (状态={t['status'] or '未填'})"
        for t in tasks
        if t["status"].lower() not in ("done", "completed", "已完成")
    ]
    if undone:
        issues.append("以下 task 未 Done：" + ", ".join(undone))

    if not run_verification():
        issues.append("最终 verify 未通过。")

    if issues:
        fail_with_fix(
            f"close 失败：{len(issues)} 项检查未通过。",
            "\n".join(f"- {x}" for x in issues),
            "修复后重新运行 close；或使用 --abort 放弃 track。",
        )

    append_history(f"close {slug}")
    mark_empty()
    print(f"track {slug} 已关闭。")
    # 提示后续合并
    name = track_name_from_slug(slug)
    base_branch = info.get("Base 分支") or "main"
    print(f"可选下一步：git checkout {base_branch} && git merge --no-ff track/{name}")


# ---------- 命令: status ----------

def cmd_status(args: argparse.Namespace) -> None:
    info = parse_active_track()
    if not info:
        print("无 active track（harness/state/active-track.md 不存在）。")
        return
    if info.get("状态") != "active":
        print(f"无 active track（状态：{info.get('状态', '?')}）。")
        return
    print(f"Active Track: {info.get('Track 路径', '?')}")
    print(f"  slug: {info.get('Track slug', '?')}")
    print(f"  base: {info.get('Base 分支', '?')}")
    print(f"  启动: {info.get('启动时间', '?')}")
    print(f"  当前任务: {info.get('当前任务', '?')}")

    track_path = ROOT / info["Track 路径"]
    tasks = parse_tasks(track_path)
    if tasks:
        done = sum(1 for t in tasks if t["status"].lower() in ("done", "completed", "已完成"))
        print(f"\n任务进度：{done}/{len(tasks)}")
        for t in tasks:
            mark = "✓" if t["status"].lower() in ("done", "completed", "已完成") else "·"
            print(f"  {mark} {t['id']} {t['name']} [{t['status'] or 'Todo'}]")


# ---------- main ----------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_open = sub.add_parser("open", help="创建新 track 并标记为 active")
    p_open.add_argument("name", help="track 名（小写字母/数字/横线）")
    p_open.add_argument("--no-branch", action="store_true", help="不自动 git checkout -b")
    p_open.set_defaults(func=cmd_open)

    p_finish = sub.add_parser("finish-task", help="完成当前任务（验证 + commit + push）")
    p_finish.add_argument("--task", help="指定 task id（默认为第一个未 Done 的）")
    p_finish.add_argument("--message", help="自定义 commit message 末尾")
    p_finish.set_defaults(func=cmd_finish_task)

    p_close = sub.add_parser("close", help="关闭当前 active track")
    p_close.add_argument("--abort", action="store_true", help="放弃 track（跳过验收）")
    p_close.add_argument("--reason", help="放弃原因（仅 --abort 时使用）")
    p_close.set_defaults(func=cmd_close)

    p_status = sub.add_parser("status", help="查看当前 active track 状态")
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
