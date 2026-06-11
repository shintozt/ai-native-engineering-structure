#!/usr/bin/env python3
"""Track 生命周期命令。

Commands:
    track.py open <name>                创建新 track 并标记为 active（默认铺 proposal.md 和 notes.md）
    track.py next-stage                 推进到下一档（spec / design / tasks / archive）
    track.py revise-stage <stage>       重审某档并清空该档及下游定稿戳
    track.py finish-task [--task <id>]  完成当前任务（验证 + 更新 task 状态）
                          [--message <m>]
                          [--commit --confirmed-by <name>]
    track.py close [--abort] [--reason] 关闭当前 active track
    track.py knowledge-status           扫描已关闭 Track 的待沉淀 learnings
    track.py pre-merge-check            合并 / push / 删除分支前检查 Track 是否已关闭
    track.py status                     查看当前 active track 状态

约束：
- init-status 必须为已完成才能 open。
- 同时仅允许 1 个 active track；close 后才能 open 下一个。
- open 默认只铺 proposal.md 和 notes.md；后续文档由 next-stage 顺序推进。
- 推进下一档前，上一档必须有非空 approved-by 定稿戳。
- finish-task 必须通过 verify-template.sh 和 check-layer-boundaries 才会更新 task 状态。
- git commit / push 必须显式传入 --commit --confirmed-by <name>，表示已有人工确认。
- 验证失败时阻断状态推进和 git 操作，保留工作区供修复。
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

STAGE_ORDER = ("proposal", "spec", "design", "tasks", "archive")
STAGE_FILES: dict[str, tuple[tuple[str, str], ...]] = {
    "proposal": (
        ("proposal.md", "proposal-template.md"),
        ("notes.md", "notes-template.md"),
    ),
    "spec": (("spec.md", "spec-template.md"),),
    "design": (("design.md", "design-template.md"),),
    "tasks": (("tasks.md", "tasks-template.md"),),
    "archive": (
        ("acceptance.md", "acceptance-template.md"),
        ("learnings.md", "learnings-template.md"),
    ),
}
NEXT_STAGE = {
    "proposal": "spec",
    "spec": "design",
    "design": "tasks",
    "tasks": "archive",
}
STAGE_APPROVAL_FILES = {
    "proposal": ("proposal.md",),
    "spec": ("spec.md",),
    "design": ("design.md",),
    "tasks": ("tasks.md",),
    "archive": ("acceptance.md",),
}

VERIFY_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("bash", "harness/scripts/verify/verify-template.sh"),
    ("bash", "harness/scripts/verify/check-layer-boundaries-template.sh"),
)

IMPLEMENTATION_MODULE_MAP_PATH = "context/architecture/implementation-module-map.md"
STRUCTURE_IMPACT_PREFIXES = ("src/", "include/", "api/", "proto/")
STRUCTURE_IMPACT_FILES = (
    "CMakeLists.txt",
    "CMakePresets.json",
    "Makefile",
    "meson.build",
    "BUILD",
    "WORKSPACE",
)
STRUCTURE_IMPACT_DIRS = ("cmake/",)
IMPLEMENTATION_MAP_NO_IMPACT_MARKERS = (
    "implementation module map 影响：不影响",
    "implementation module map 影响: 不影响",
    "实现模块映射影响：不影响",
    "实现模块映射影响: 不影响",
)

TASK_HEADING_RE = re.compile(r"^###\s+(Task\s+\d+|T\d+)\s*[：:]\s*(.*?)\s*$", re.IGNORECASE)
APPROVED_BY_RE = re.compile(r"^\s*-\s*approved-by\s*[:：]\s*(.*?)\s*$", re.IGNORECASE)


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
    if not ACTIVE_TRACK_FILE.exists():
        return
    set_field("状态", "empty")
    set_field("当前任务", "")


def init_completed() -> bool:
    if not INIT_STATUS.exists():
        return False
    text = INIT_STATUS.read_text(encoding="utf-8")
    if "## 状态" not in text:
        return False
    block = text.split("## 状态", 1)[1].split("##", 1)[0]
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    return bool(lines) and lines[0] == "已完成"


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


def all_tasks_done(track_path: Path) -> bool:
    tasks = parse_tasks(track_path)
    return bool(tasks) and all(
        task["status"].lower() in ("done", "completed", "已完成") for task in tasks
    )


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


def task_section_text(track_path: Path, raw_id: str) -> str:
    tasks_file = track_path / "tasks.md"
    if not tasks_file.exists():
        return ""
    text = tasks_file.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    in_target = False
    for line in lines:
        m = TASK_HEADING_RE.match(line.rstrip("\n"))
        if m:
            if in_target:
                break
            in_target = m.group(1).strip() == raw_id
        if in_target:
            out.append(line)
    return "".join(out)


def git(*args: str, check: bool = False, capture: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=capture,
        check=check,
    )


def git_has_changes() -> bool:
    return bool(git("status", "--porcelain").stdout.strip())


def current_git_branch() -> str:
    result = git("branch", "--show-current")
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def normalize_changed_file(path: str) -> str:
    return path.strip().strip('"').lstrip("./")


def parse_git_status_changed_files(status_text: str) -> list[str]:
    files: list[str] = []
    for line in status_text.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip() if len(line) > 3 else line.strip()
        if " -> " in path:
            old, new = path.split(" -> ", 1)
            files.append(normalize_changed_file(old))
            files.append(normalize_changed_file(new))
        else:
            files.append(normalize_changed_file(path))
    return [path for path in files if path]


def git_worktree_changed_files() -> list[str]:
    result = git("status", "--porcelain")
    if result.returncode != 0:
        return []
    return parse_git_status_changed_files(result.stdout)


def git_branch_changed_files(base_branch: str) -> list[str]:
    files: set[str] = set(git_worktree_changed_files())
    untracked = git("ls-files", "--others", "--exclude-standard")
    if untracked.returncode == 0:
        files.update(normalize_changed_file(line) for line in untracked.stdout.splitlines() if line.strip())
    base = base_branch.strip() or "main"
    result = git("diff", "--name-only", f"{base}...HEAD")
    if result.returncode == 0:
        files.update(normalize_changed_file(line) for line in result.stdout.splitlines() if line.strip())
    return sorted(path for path in files if path)


def is_structure_impact_file(path: str) -> bool:
    normalized = normalize_changed_file(path)
    if normalized == IMPLEMENTATION_MODULE_MAP_PATH:
        return False
    if normalized in STRUCTURE_IMPACT_FILES:
        return True
    if normalized.endswith("/CMakeLists.txt"):
        return True
    if any(normalized.startswith(prefix) for prefix in STRUCTURE_IMPACT_PREFIXES):
        return True
    return any(normalized.startswith(prefix) for prefix in STRUCTURE_IMPACT_DIRS)


def has_implementation_map_no_impact_evidence(text: str) -> bool:
    return any(marker in text for marker in IMPLEMENTATION_MAP_NO_IMPACT_MARKERS)


def implementation_module_map_issues(changed_files: list[str], evidence_text: str) -> list[str]:
    normalized = [normalize_changed_file(path) for path in changed_files]
    structure_changes = [path for path in normalized if is_structure_impact_file(path)]
    if not structure_changes:
        return []
    if IMPLEMENTATION_MODULE_MAP_PATH in normalized:
        return []
    if has_implementation_map_no_impact_evidence(evidence_text):
        return []
    preview = ", ".join(structure_changes[:5])
    if len(structure_changes) > 5:
        preview += f" 等 {len(structure_changes)} 个文件"
    return [
        "结构影响文件已变更，但未更新 "
        f"{IMPLEMENTATION_MODULE_MAP_PATH}，也未写明 implementation module map 影响：不影响。"
        f"命中文件：{preview}"
    ]


def require_implementation_module_map_review(
    changed_files: list[str],
    evidence_text: str,
    action: str,
) -> None:
    issues = implementation_module_map_issues(changed_files, evidence_text)
    if not issues:
        return
    fail_with_fix(
        f"{action} 被阻断：缺少 implementation module map 影响判断。",
        "\n".join(f"- {issue}" for issue in issues),
        "更新 context/architecture/implementation-module-map.md，"
        "或在当前 task / acceptance 中写明 `implementation module map 影响：不影响` 及原因。",
    )


def run_verification() -> bool:
    for cmd in VERIFY_COMMANDS:
        print(f"$ {' '.join(cmd)}", file=sys.stderr)
        result = subprocess.run(cmd, cwd=ROOT, text=True)
        if result.returncode != 0:
            return False
    return True


def is_file_approved(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    for line in text.splitlines():
        m = APPROVED_BY_RE.match(line)
        if not m:
            continue
        value = m.group(1).strip()
        return bool(value and value not in ("待确认", "TBD", "TODO"))
    return False


def clear_approval_stamp(path: Path) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"^(\s*-\s*approved-by\s*[:：]).*$", r"\1", text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r"^(\s*-\s*approved-at\s*[:：]).*$", r"\1", text, flags=re.MULTILINE | re.IGNORECASE)
    path.write_text(text, encoding="utf-8")


def copy_stage_templates(track_path: Path, stage: str) -> list[Path]:
    created: list[Path] = []
    for dst_name, template_name in STAGE_FILES[stage]:
        src = TEMPLATES_DIR / template_name
        dst = track_path / dst_name
        if dst.exists():
            continue
        if not src.exists():
            fail(f"模板不存在：{src}")
        shutil.copyfile(src, dst)
        created.append(dst)
    return created


def require_stage_approved(track_path: Path, stage: str) -> None:
    missing: list[str] = []
    for file_name in STAGE_APPROVAL_FILES[stage]:
        if not is_file_approved(track_path / file_name):
            missing.append(file_name)
    if missing:
        fail_with_fix(
            f"{stage} 未定稿，不能推进下一档。",
            "以下文件缺少非空 approved-by：" + ", ".join(missing),
            "请人工 review 该档文档，确认后填写定稿戳，再运行 next-stage。",
        )


def active_track_path_or_fail() -> tuple[dict[str, str], Path]:
    info = parse_active_track()
    if not info or info.get("状态") != "active":
        fail_with_fix(
            "没有 active track。",
            "active-track.md 不存在或状态不是 active。",
            "先运行 `python3 -B harness/scripts/lifecycle/track.py open <name>`。",
        )
    track_relative = info.get("Track 路径", "")
    track_path = ROOT / track_relative
    if not track_path.is_dir():
        fail(f"active track 目录不存在：{track_path}")
    return info, track_path


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
            "先 close 当前 track，再 open 新的。",
        )

    today = datetime.now().strftime("%Y-%m-%d")
    slug = f"{today}-{name}"
    track_path = TRACKS_DIR / slug
    if track_path.exists():
        fail(f"track 目录已存在：{track_path}")

    TRACKS_DIR.mkdir(parents=True, exist_ok=True)
    track_path.mkdir(parents=True)
    if args.legacy_all:
        for stage in STAGE_ORDER:
            copy_stage_templates(track_path, stage)
    else:
        copy_stage_templates(track_path, "proposal")

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
    write_active_track(relative, slug, "T1", base_branch)

    print(f"已 open track: {relative}")
    print(f"slug: {slug}")
    if args.legacy_all:
        print("已按 --legacy-all 铺出全部模板；推荐新项目使用 next-stage 逐档推进。")
    else:
        print("下一步：填写 proposal.md，人工确认后补 approved-by / approved-at，再运行 next-stage。")


def cmd_next_stage(args: argparse.Namespace) -> None:
    _info, track_path = active_track_path_or_fail()
    for current, next_stage in NEXT_STAGE.items():
        if not all((track_path / dst).exists() for dst, _template in STAGE_FILES[next_stage]):
            require_stage_approved(track_path, current)
            if next_stage == "archive" and not all_tasks_done(track_path):
                fail_with_fix(
                    "tasks 尚未全部 Done，不能铺出归档文档。",
                    "acceptance.md / learnings.md 应在所有 task 完成后填写。",
                    "先运行 finish-task 推进所有任务；最后一个 task 完成后也会自动铺出归档文档。",
                )
            created = copy_stage_templates(track_path, next_stage)
            append_history(f"next-stage {next_stage}")
            if created:
                print("已创建：")
                for path in created:
                    print(f"- {path.relative_to(ROOT)}")
            else:
                print(f"{next_stage} 档文件已存在。")
            return
    print("所有阶段文件均已存在。")


def cmd_revise_stage(args: argparse.Namespace) -> None:
    _info, track_path = active_track_path_or_fail()
    if args.stage not in STAGE_ORDER:
        fail(f"未知 stage：{args.stage}。可选：{', '.join(STAGE_ORDER)}")
    if not args.confirmed_by:
        fail("revise-stage 必须传入 --confirmed-by <人名>。")

    start = STAGE_ORDER.index(args.stage)
    touched: list[Path] = []
    for stage in STAGE_ORDER[start:]:
        for file_name, _template in STAGE_FILES[stage]:
            path = track_path / file_name
            if path.exists():
                clear_approval_stamp(path)
                touched.append(path)
    append_history(f"revise {args.stage} by {args.confirmed_by}")
    print(f"已清空 {args.stage} 及下游定稿戳：")
    for path in touched:
        print(f"- {path.relative_to(ROOT)}")


def cmd_finish_task(args: argparse.Namespace) -> None:
    info, track_path = active_track_path_or_fail()
    slug = info["Track slug"]

    require_stage_approved(track_path, "tasks")

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

    if args.commit and not args.confirmed_by:
        fail("使用 --commit 必须同时传入 --confirmed-by <人名>。")

    print(f"== finish-task: {task['id']} {task['name']} ==", file=sys.stderr)
    require_implementation_module_map_review(
        git_worktree_changed_files(),
        task_section_text(track_path, task["raw_id"]),
        f"finish-task {task['id']}",
    )

    if not run_verification():
        fail_with_fix(
            f"验证失败，task {task['id']} 未更新状态。",
            "verify-template.sh 或 check-layer-boundaries 未通过。工作区保留以便修复。",
            f"修复后重新运行：python3 -B harness/scripts/lifecycle/track.py finish-task --task {task['id']}",
        )

    mark_task_done(track_path, task["raw_id"])
    next_task = first_undone(track_path)
    if next_task:
        set_field("当前任务", next_task["id"])
    else:
        set_field("当前任务", "（全部 Done，可 close）")
        copy_stage_templates(track_path, "archive")
    append_history(f"finish {task['id']}")

    if args.commit:
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
            print(f"WARN: git push 失败：{push.stderr.strip()}", file=sys.stderr)
            print("commit 已完成，请手动推送或检查 remote 配置。", file=sys.stderr)
        append_history(f"commit {task['id']} by {args.confirmed_by}")
        print(f"task {task['id']} 完成，已提交。")
    else:
        print(f"task {task['id']} 完成，已更新 tasks.md 状态；未执行 git commit。")
        if git_has_changes():
            print("当前工作区仍有变更，请人工确认后再决定是否提交。")

    if next_task:
        print(f"下一个任务：{next_task['id']} {next_task['name']}")
    else:
        print("所有 task Done。已铺出 acceptance.md / learnings.md，请填写并人工定稿后 close。")


def cmd_close(args: argparse.Namespace) -> None:
    info, track_path = active_track_path_or_fail()
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
    elif not is_file_approved(acceptance):
        issues.append("acceptance.md 缺少 approved-by。")
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

    require_implementation_module_map_review(
        git_branch_changed_files(info.get("Base 分支", "main")),
        acceptance.read_text(encoding="utf-8") if acceptance.exists() else "",
        "close",
    )

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
    name = track_name_from_slug(slug)
    base_branch = info.get("Base 分支") or "main"
    print(f"可选下一步：git checkout {base_branch} && git merge --no-ff track/{name}")


def cmd_pre_merge_check(args: argparse.Namespace) -> None:
    info = parse_active_track()
    if info and info.get("状态") == "active":
        fail_with_fix(
            f"合并前检查失败：仍有 active track {info.get('Track 路径', '?')}",
            "代码合并、push 或删除分支前，Track 必须先 close 或 abort。",
            "先运行 `python3 -B harness/scripts/lifecycle/track.py close` 或 `close --abort`。",
        )
    print("pre-merge-check 通过：当前无 active track。")


def cmd_knowledge_status(args: argparse.Namespace) -> None:
    base = TRACKS_DIR if not args.track else TRACKS_DIR / args.track
    if not base.exists():
        print("未找到 Track 目录。")
        return
    paths = [base / "learnings.md"] if base.is_dir() and (base / "learnings.md").exists() else []
    if not paths:
        paths = sorted(TRACKS_DIR.glob("*/learnings.md"))
    pending: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if re.search(r"\bpending\b|待沉淀|待处理", text, flags=re.IGNORECASE):
            pending.append(str(path.relative_to(ROOT)))
    if not pending:
        print("未发现明显 pending learnings。")
        return
    print("发现待处理 learnings：")
    for item in pending:
        print(f"- {item}")


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
    for stage in STAGE_ORDER:
        names = [dst for dst, _template in STAGE_FILES[stage]]
        exists = all((track_path / name).exists() for name in names)
        approved = all(is_file_approved(track_path / name) for name in STAGE_APPROVAL_FILES[stage] if (track_path / name).exists())
        print(f"  {stage}: {'exists' if exists else 'missing'} / {'approved' if approved else 'draft'}")

    tasks = parse_tasks(track_path)
    if tasks:
        done = sum(1 for t in tasks if t["status"].lower() in ("done", "completed", "已完成"))
        print(f"\n任务进度：{done}/{len(tasks)}")
        for t in tasks:
            mark = "✓" if t["status"].lower() in ("done", "completed", "已完成") else "·"
            print(f"  {mark} {t['id']} {t['name']} [{t['status'] or 'Todo'}]")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_open = sub.add_parser("open", help="创建新 track 并标记为 active")
    p_open.add_argument("name", help="track 名（小写字母/数字/横线）")
    p_open.add_argument("--no-branch", action="store_true", help="不自动 git checkout -b")
    p_open.add_argument("--legacy-all", action="store_true", help="兼容旧流程：一次性铺出全部模板")
    p_open.set_defaults(func=cmd_open)

    p_next = sub.add_parser("next-stage", help="定稿后一档一档铺出 Track 文档")
    p_next.set_defaults(func=cmd_next_stage)

    p_revise = sub.add_parser("revise-stage", help="重审某档并清空该档及下游定稿戳")
    p_revise.add_argument("stage", choices=STAGE_ORDER)
    p_revise.add_argument("--confirmed-by", required=True, help="确认重审的人")
    p_revise.set_defaults(func=cmd_revise_stage)

    p_finish = sub.add_parser("finish-task", help="完成当前任务（验证 + 更新状态；提交需人工确认）")
    p_finish.add_argument("--task", help="指定 task id（默认为第一个未 Done 的）")
    p_finish.add_argument("--message", help="自定义 commit message 末尾")
    p_finish.add_argument("--commit", action="store_true", help="验证通过后提交并 push")
    p_finish.add_argument("--confirmed-by", help="人工确认人；使用 --commit 时必填")
    p_finish.set_defaults(func=cmd_finish_task)

    p_close = sub.add_parser("close", help="关闭当前 active track")
    p_close.add_argument("--abort", action="store_true", help="放弃 track（跳过验收）")
    p_close.add_argument("--reason", help="放弃原因（仅 --abort 时使用）")
    p_close.set_defaults(func=cmd_close)

    p_pre_merge = sub.add_parser("pre-merge-check", help="合并 / push / 删除分支前检查")
    p_pre_merge.set_defaults(func=cmd_pre_merge_check)

    p_knowledge = sub.add_parser("knowledge-status", help="扫描待沉淀 learnings")
    p_knowledge.add_argument("--track", help="指定 Track slug")
    p_knowledge.set_defaults(func=cmd_knowledge_status)

    p_status = sub.add_parser("status", help="查看当前 active track 状态")
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
