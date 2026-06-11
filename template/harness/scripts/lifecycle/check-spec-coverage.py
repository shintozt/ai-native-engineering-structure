#!/usr/bin/env python3
"""Spec 不变式 / 业务规则覆盖度检查。

把 spec.md 的 INV-XXX 与 RULE-XXX 标识抽出来，校验 design.md / tasks.md 是否给出显式锚点。

通过标准：
- 每个 spec.md 的 INV-XXX 至少在 design.md 中出现一次。
- 每个 spec.md 的 RULE-XXX 至少在 design.md 或 tasks.md 中出现一次。
- spec.md 顶部"业务不变式速览"段非占位（至少 1 条 INV）。
- spec.md 业务规则表的每一行命中至少 1 条 INV-ID。

使用方式：
    python3 -B harness/scripts/lifecycle/check-spec-coverage.py
    python3 -B harness/scripts/lifecycle/check-spec-coverage.py --track <relative-track-path>
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


def find_project_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    while True:
        if (current / "AGENTS.md").is_file():
            return current
        if current == current.parent:
            return Path.cwd().resolve()
        current = current.parent


ROOT = find_project_root()
ACTIVE_TRACK_FILE = ROOT / "harness" / "state" / "active-track.md"

INV_RE = re.compile(r"INV-\d+")
RULE_RE = re.compile(r"RULE-\d+")
RULE_TABLE_HIT_INV_HEADER_RE = re.compile(r"命中\s*INV")
PLACEHOLDER_MARKERS = ("<", ">", "TODO", "待填写", "占位")


@dataclass
class CheckResult:
    name: str
    ok: bool
    evidence: str
    fix: str


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        return ""


def has_placeholder(text: str) -> bool:
    upper = text.upper()
    return any(marker.upper() in upper for marker in PLACEHOLDER_MARKERS)


def resolve_track_path(arg_value: str | None) -> Path | None:
    if arg_value:
        candidate = (ROOT / arg_value).resolve() if not Path(arg_value).is_absolute() else Path(arg_value)
        return candidate if candidate.is_dir() else None
    if not ACTIVE_TRACK_FILE.exists():
        return None
    for line in ACTIVE_TRACK_FILE.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("- ") and "Track 路径" in s:
            _, _, value = s.partition("：")
            if not value:
                _, _, value = s.partition(":")
            value = value.strip()
            if value:
                return (ROOT / value).resolve()
    return None


def extract_section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    if marker not in text:
        return ""
    body = text.split(marker, 1)[1]
    return body.split("\n## ", 1)[0].lstrip("\n")


def check_invariant_summary(spec_text: str) -> CheckResult:
    section = extract_section(spec_text, "业务不变式速览")
    if not section.strip():
        return CheckResult(
            "spec.md 含「业务不变式速览」段",
            False,
            "spec.md: ## 业务不变式速览",
            "在 spec.md 顶部新增「业务不变式速览」段，至少列出 1 条 INV-XXX。",
        )
    invs = sorted(set(INV_RE.findall(section)))
    if not invs:
        return CheckResult(
            "「业务不变式速览」段至少含 1 条 INV-XXX",
            False,
            "spec.md: ## 业务不变式速览",
            "在「业务不变式速览」表中至少写 1 条 INV-XXX。",
        )
    body_clean = "\n".join(
        line for line in section.splitlines() if not line.lstrip().startswith(">")
    )
    if has_placeholder(body_clean):
        return CheckResult(
            "「业务不变式速览」段内容非占位",
            False,
            "spec.md: ## 业务不变式速览",
            "把 TODO / 待填写 / <...> / 占位 替换成真实不变式条目。",
        )
    return CheckResult(
        "「业务不变式速览」段非占位且含 INV-XXX",
        True,
        f"spec.md 段落，含 {', '.join(invs)}",
        "",
    )


def check_rule_table_hits_inv(spec_text: str) -> CheckResult:
    section = extract_section(spec_text, "业务规则")
    if not section.strip():
        return CheckResult(
            "spec.md 含「业务规则」段",
            False,
            "spec.md: ## 业务规则",
            "新增「业务规则」段，并贴模板的业务规则表。",
        )
    lines = section.splitlines()
    header_idx = None
    for i, line in enumerate(lines):
        if line.startswith("|") and "规则" in line and "条件" in line:
            header_idx = i
            break
    if header_idx is None:
        return CheckResult(
            "「业务规则」段含表头",
            False,
            "spec.md: ## 业务规则",
            "使用模板提供的业务规则表（含「规则 ID / 命中 INV / 条件 / ...」表头）。",
        )
    if not RULE_TABLE_HIT_INV_HEADER_RE.search(lines[header_idx]):
        return CheckResult(
            "「业务规则」表含「命中 INV」列",
            False,
            "spec.md: ## 业务规则",
            "把业务规则表升级为新版（含「命中 INV」列），每行命中至少 1 条 INV-ID。",
        )

    bad_rows: list[str] = []
    for line in lines[header_idx + 2 :]:
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or all(not c for c in cells):
            continue
        rule_id = cells[0] if cells else ""
        if rule_id and not RULE_RE.fullmatch(rule_id):
            continue
        joined = " ".join(cells)
        if not INV_RE.search(joined):
            bad_rows.append(rule_id or line[:60])
    if bad_rows:
        return CheckResult(
            "业务规则表每行命中至少 1 条 INV-ID",
            False,
            f"spec.md 业务规则表: {', '.join(bad_rows[:5])}",
            "为这些规则补「命中 INV」列；若规则不命中任何不变式，说明该规则不该存在。",
        )
    return CheckResult(
        "业务规则表每行命中至少 1 条 INV-ID",
        True,
        "spec.md 业务规则表",
        "",
    )


def check_inv_anchored_in_design(spec_text: str, design_text: str) -> list[CheckResult]:
    invs = sorted(set(INV_RE.findall(spec_text)))
    if not invs:
        return [
            CheckResult(
                "spec.md 至少含 1 条 INV-XXX",
                False,
                "spec.md",
                "spec.md 必须含至少 1 条 INV-XXX；否则下游 design / tasks 无锚点。",
            )
        ]
    results: list[CheckResult] = []
    for inv in invs:
        if inv in design_text:
            results.append(CheckResult(f"{inv} 在 design.md 中有锚点", True, f"design.md 含 {inv}", ""))
        else:
            results.append(
                CheckResult(
                    f"{inv} 在 design.md 中有锚点",
                    False,
                    f"design.md 未出现 {inv}",
                    f"在 design.md 接口表「命中 INV」列、关键算法段或验证方案中显式引用 {inv}。",
                )
            )
    return results


def check_rule_anchored(spec_text: str, design_text: str, tasks_text: str) -> list[CheckResult]:
    rules = sorted(set(RULE_RE.findall(spec_text)))
    if not rules:
        return [
            CheckResult(
                "spec.md 至少含 1 条 RULE-XXX",
                False,
                "spec.md",
                "spec.md 必须含至少 1 条业务规则 RULE-XXX。",
            )
        ]
    results: list[CheckResult] = []
    for rule in rules:
        if rule in design_text or rule in tasks_text:
            results.append(
                CheckResult(
                    f"{rule} 在 design.md 或 tasks.md 中有锚点",
                    True,
                    f"design.md / tasks.md 含 {rule}",
                    "",
                )
            )
        else:
            results.append(
                CheckResult(
                    f"{rule} 在 design.md 或 tasks.md 中有锚点",
                    False,
                    f"design.md 与 tasks.md 均未出现 {rule}",
                    f"在 design.md 或 tasks.md 中显式引用 {rule}。",
                )
            )
    return results


def print_result(result: CheckResult) -> None:
    status = "PASS" if result.ok else "FAIL"
    print(f"[{status}] {result.name}")
    print(f"  evidence: {result.evidence}")
    if not result.ok and result.fix:
        print(f"  fix: {result.fix}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--track", help="指定 track 路径（相对项目根）；默认读 active-track.md")
    args = parser.parse_args(argv)

    track = resolve_track_path(args.track)
    if track is None:
        print(
            "WHAT: 找不到 track 路径。\n"
            "WHY: --track 未指定，且 active-track.md 没有有效路径。\n"
            "HOW: 用 --track <relative-path> 指定，或先 `track.py open <name>`。",
            file=sys.stderr,
        )
        return 1

    spec = read_text(track / "spec.md")
    design = read_text(track / "design.md")
    tasks = read_text(track / "tasks.md")

    if not spec.strip():
        print(
            f"WHAT: {track / 'spec.md'} 不存在或为空。\n"
            "WHY: 没有 Spec 就无法做覆盖度检查。\n"
            "HOW: 先完成 Spec 起草，并写入「业务不变式速览」段。",
            file=sys.stderr,
        )
        return 1

    results: list[CheckResult] = []
    results.append(check_invariant_summary(spec))
    results.append(check_rule_table_hits_inv(spec))
    results.extend(check_inv_anchored_in_design(spec, design))
    results.extend(check_rule_anchored(spec, design, tasks))

    for result in results:
        print_result(result)

    failed = [result for result in results if not result.ok]
    print()
    if failed:
        print(f"WHAT: Spec 不变式 / 业务规则覆盖度检查未通过，共 {len(failed)} 项失败。")
        print("WHY: 失败项缺少 design / tasks 显式锚点；表示 Spec 与下游契约脱节。")
        print("HOW: 按每个 FAIL 项的 fix 修复后，重新运行本脚本。")
        return 1
    print("WHAT: Spec 不变式 / 业务规则覆盖度检查通过。")
    print("WHY: 每条 INV / RULE 都有显式锚点。")
    print("HOW: 进入下一道门禁（Evaluator Spec 合规 / 人工 Review）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
