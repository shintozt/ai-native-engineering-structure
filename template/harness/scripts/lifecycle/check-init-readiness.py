#!/usr/bin/env python3
"""检查新服务初始化是否具备进入第一个 Track 的证据。

本脚本只判断可机械化的事实，例如文件存在、占位符残留、入口规则、脚本项目化状态
和初始化门禁行为。业务语义是否合理仍需人工确认，并记录到 harness/state/init-status.md。
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


def find_project_root(start: Path | None = None) -> Path:
    """从 start 向上查找最近的 AGENTS.md 所在目录。

    AGENTS.md 是项目根的标志（母版和真实项目都有）。找不到时回退到 cwd 并打印警告。
    """
    current = (start or Path.cwd()).resolve()
    while True:
        if (current / "AGENTS.md").is_file():
            return current
        if current == current.parent:
            print(
                "WARN: 未找到 AGENTS.md，回退到 cwd 作为项目根。建议从项目根目录运行本脚本。",
                file=sys.stderr,
            )
            return Path.cwd().resolve()
        current = current.parent


ROOT = find_project_root()
PLACEHOLDER_PATTERNS = (
    r"<[^>\n]+>",
    r"\bTODO\b",
    r"待填写",
    r"占位",
)
README_FORBIDDEN_PATTERNS = (
    r"项目 README 的初始占位",
)
REQUIRED_CONTEXT_FILES = (
    "context/business/business-map.md",
    "context/domain/ubiquitous-language.md",
    "context/domain/business-rules.md",
    "context/domain/core-capability-design.md",
    "context/domain/knowledge-packages/README.md",
    "context/domain/catalog.md",
    "context/architecture/layered-architecture.md",
    "context/architecture/runtime-dataflow.md",
    "context/architecture/implementation-module-map.md",
    "context/architecture/blueprint/class-design-rules.md",
    "context/architecture/blueprint/domain-capability-design-rules.md",
    "context/architecture/catalog.md",
    "context/engineering/README.md",
    "context/engineering/catalog.md",
    "context/engineering/scaffolds/README.md",
    "context/operations/build-and-test.md",
    "context/operations/cpp-coding-style.md",
    "context/operations/observability.md",
    "context/operations/log-analysis-guide.md",
    "context/operations/performance-risk-analysis.md",
    "context/operations/catalog.md",
)
PROJECTIZED_SCRIPTS = (
    "harness/scripts/verify/verify-template.sh",
    "harness/scripts/verify/check-layer-boundaries-template.sh",
)
TOOL_CONTROL_FILES = (
    ".claude/settings.json",
    ".codex/config.toml",
)
AGENT_NAMES = (
    "planner",
    "generator",
    "evaluator",
    "reviewer",
    "maintainer",
)


@dataclass
class CheckResult:
    name: str
    ok: bool
    evidence: str
    fix: str


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    except UnicodeDecodeError:
        return ""


def nonempty_file(path: Path) -> bool:
    return bool(read_text(path).strip())


def has_pattern(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def block_after_heading(text: str, heading: str) -> str:
    marker = f"## {heading}"
    if marker not in text:
        return ""
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def run_harness_pre_edit(file_name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "harness/scripts/hooks/harness_gate.py", "pre-edit"],
        cwd=ROOT,
        input=f'{{"file":"{file_name}"}}',
        text=True,
        capture_output=True,
        check=False,
    )


def check_readme() -> list[CheckResult]:
    path = ROOT / "README.md"
    text = read_text(path)
    required = ("## 当前阶段", "## 快速入口", "## 服务范围", "## 上下游", "AGENTS.md")
    checks = [
        CheckResult(
            "README.md 存在且非空",
            bool(text.strip()),
            "README.md",
            "原地修改 README.md 占位为真实业务信息。",
        ),
        CheckResult(
            "README.md 无占位符",
            bool(text.strip()) and not has_pattern(text, PLACEHOLDER_PATTERNS),
            "README.md",
            "替换 <服务名称>、TODO、待填写等占位内容。",
        ),
        CheckResult(
            "README.md 不再是母版说明",
            bool(text.strip()) and not has_pattern(text, README_FORBIDDEN_PATTERNS),
            "README.md",
            "用真实项目 README 替换母版说明。",
        ),
        CheckResult(
            "README.md 包含人类入口段落",
            all(item in text for item in required),
            "README.md",
            "补齐当前阶段、快速入口、服务范围、上下游等段落。",
        ),
    ]
    return checks


def check_agents() -> list[CheckResult]:
    text = read_text(ROOT / "AGENTS.md")
    required = (
        "harness/sop/01-新服务初始化SOP.md",
        "harness/lifecycle/gates.md",
        "harness/lifecycle/track-lifecycle.md",
        "context/INDEX.md",
        "context/operations/cpp-coding-style.md",
    )
    reading_order = block_after_heading(text, "必读顺序")
    return [
        CheckResult(
            "AGENTS.md 存在且非空",
            bool(text.strip()),
            "AGENTS.md",
            "按真实项目更新 AGENTS.md。",
        ),
        CheckResult(
            "AGENTS.md 必读顺序不依赖 README.md",
            bool(reading_order) and "README.md" not in reading_order,
            "AGENTS.md: 必读顺序",
            "从 AI 必读顺序中移除 README.md；README.md 只给人类阅读。",
        ),
        CheckResult(
            "AGENTS.md 包含初始化、门禁、Track 生命周期和 C++ 入口",
            all(item in text for item in required),
            "AGENTS.md",
            "补齐初始化 SOP、门禁总览、Track 生命周期、context 索引和 C++ 规范入口。",
        ),
    ]


def check_claude() -> list[CheckResult]:
    text = read_text(ROOT / "CLAUDE.md")
    section_count = len(re.findall(r"^## ", text, flags=re.MULTILINE))
    return [
        CheckResult(
            "CLAUDE.md 只转接 AGENTS.md",
            bool(text.strip()) and "AGENTS.md" in text and section_count == 0,
            "CLAUDE.md",
            "保持 CLAUDE.md 轻量，只指向 AGENTS.md，不复制规则。",
        )
    ]


def check_git_repository() -> list[CheckResult]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=ROOT,
            check=False,
            text=True,
            capture_output=True,
        )
    except FileNotFoundError:
        ok = False
    else:
        ok = result.returncode == 0 and result.stdout.strip() == "true"
    return [
        CheckResult(
            "Git 仓库已初始化",
            ok,
            "git rev-parse --is-inside-work-tree",
            "在项目根目录执行 git init；如团队要求远端分支，进入第一个 Track 前配置 remote。",
        )
    ]


def check_constitution() -> list[CheckResult]:
    text = read_text(ROOT / "constitution.md")
    return [
        CheckResult(
            "constitution.md 包含 AI 执行边界",
            "## AI 执行边界" in text,
            "constitution.md",
            "补充 AI 可自主修改、必须人工确认、禁止执行的范围。",
        ),
        CheckResult(
            "constitution.md 无明显占位符",
            bool(text.strip()) and not has_pattern(text, PLACEHOLDER_PATTERNS),
            "constitution.md",
            "替换 TODO、待填写、<...> 等占位内容。",
        ),
    ]


def check_context() -> list[CheckResult]:
    results: list[CheckResult] = []
    for relative in REQUIRED_CONTEXT_FILES:
        path = ROOT / relative
        text = read_text(path)
        results.append(
            CheckResult(
                f"{relative} 已填写",
                bool(text.strip()) and not has_pattern(text, PLACEHOLDER_PATTERNS),
                relative,
                f"补齐 {relative}，并移除占位符。",
            )
        )
    return results


def check_scripts() -> list[CheckResult]:
    results: list[CheckResult] = []
    for relative in PROJECTIZED_SCRIPTS:
        text = read_text(ROOT / relative)
        results.append(
            CheckResult(
                f"{relative} 已项目化",
                bool(text.strip()) and "尚未项目化" not in text,
                relative,
                f"替换 {relative} 中的母版失败提示，改成真实检查逻辑。",
            )
        )
    return results


def check_tool_control() -> list[CheckResult]:
    results: list[CheckResult] = []
    for relative in TOOL_CONTROL_FILES:
        text = read_text(ROOT / relative)
        results.append(
            CheckResult(
                f"{relative} 已配置",
                bool(text.strip()) and "harness/scripts/hooks/harness_gate.py" in text,
                relative,
                f"补齐 {relative}，确保工具 Hook 调用 harness/scripts/hooks/harness_gate.py。",
            )
        )
    codex_config = read_text(ROOT / ".codex/config.toml")
    results.append(
        CheckResult(
            ".codex/config.toml 已启用 subagents 配置",
            "[agents]" in codex_config and "max_threads" in codex_config,
            ".codex/config.toml",
            "补充 [agents] 配置，设置 max_threads 和 max_depth。",
        )
    )
    for agent_name in AGENT_NAMES:
        claude_path = f".claude/agents/{agent_name}.md"
        codex_path = f".codex/agents/{agent_name}.toml"
        harness_ref = f"harness/agents/{agent_name}.md"
        claude_text = read_text(ROOT / claude_path)
        codex_text = read_text(ROOT / codex_path)
        results.append(
            CheckResult(
                f"{claude_path} 已引用 harness 角色定义",
                bool(claude_text.strip()) and harness_ref in claude_text,
                claude_path,
                f"补齐 {claude_path}，并引用 {harness_ref}。",
            )
        )
        results.append(
            CheckResult(
                f"{codex_path} 已引用 harness 角色定义",
                bool(codex_text.strip()) and harness_ref in codex_text,
                codex_path,
                f"补齐 {codex_path}，并引用 {harness_ref}。",
            )
        )
    return results


def check_harness_gate() -> list[CheckResult]:
    track_result = run_harness_pre_edit("specs/tracks/new-feature/spec.md")
    code_result = run_harness_pre_edit("src/example.cpp")
    readme_result = run_harness_pre_edit("README.md")
    return [
        CheckResult(
            "初始化未完成时阻断创建 Track",
            track_result.returncode == 2,
            "python3 -B harness/scripts/hooks/harness_gate.py pre-edit",
            "检查 harness/state/init-status.md 状态解析和 track 编辑识别规则。",
        ),
        CheckResult(
            "初始化未完成时阻断业务代码编辑",
            code_result.returncode == 2,
            "python3 -B harness/scripts/hooks/harness_gate.py pre-edit",
            "检查 SRC_LIKE_PREFIXES、SRC_LIKE_FILES 和初始化门禁。",
        ),
        CheckResult(
            "初始化阶段允许修改 README.md",
            readme_result.returncode == 0,
            "python3 -B harness/scripts/hooks/harness_gate.py pre-edit",
            "将 README.md 保留在初始化白名单。",
        ),
    ]


def check_init_status(results_so_far: list[CheckResult]) -> list[CheckResult]:
    text = read_text(ROOT / "harness/state/init-status.md")
    status_block = block_after_heading(text, "状态")
    status_lines = [line.strip() for line in status_block.splitlines() if line.strip()]
    status = status_lines[0] if status_lines else ""
    all_auto_ok = all(result.ok for result in results_so_far)
    return [
        CheckResult(
            "init-status 状态与自动检查一致",
            status != "已完成" or all_auto_ok,
            "harness/state/init-status.md",
            "只有所有自动检查通过，并完成人工确认后，才能把状态改为 已完成。",
        ),
        CheckResult(
            "init-status 记录人工确认字段",
            "最近一次自动检查" in text and "人工确认" in text,
            "harness/state/init-status.md",
            "记录自动检查命令、结果、人工确认人和日期。",
        ),
    ]


def print_result(result: CheckResult) -> None:
    status = "PASS" if result.ok else "FAIL"
    print(f"[{status}] {result.name}")
    print(f"  evidence: {result.evidence}")
    if not result.ok:
        print(f"  fix: {result.fix}")


def main() -> int:
    results: list[CheckResult] = []
    results.extend(check_readme())
    results.extend(check_agents())
    results.extend(check_claude())
    results.extend(check_git_repository())
    results.extend(check_constitution())
    results.extend(check_context())
    results.extend(check_scripts())
    results.extend(check_tool_control())
    results.extend(check_harness_gate())
    results.extend(check_init_status(results))

    failed = [result for result in results if not result.ok]
    for result in results:
        print_result(result)

    print()
    print("人工确认项：")
    print("- 业务边界、上下游和不包含范围是否正确。")
    print("- 领域术语和业务规则是否符合真实业务。")
    print("- 架构分层、端口隔离和外部依赖边界是否合理。")
    print("- 工程脚手架是否符合本服务的代码组织方式。")
    print("- 构建、测试、格式化命令是否符合团队实际环境。")

    if failed:
        print()
        print(f"WHAT: 初始化自动检查未通过，共 {len(failed)} 项失败。")
        print("WHY: 失败项缺少可验证证据，不能证明工程已准备好创建第一个 Track。")
        print("HOW: 按每个 FAIL 项的 fix 修复后，重新运行 python3 -B harness/scripts/lifecycle/check-init-readiness.py。")
        return 1

    print()
    print("WHAT: 初始化自动检查通过。")
    print("WHY: 可机械化检查项均已有证据。")
    print("HOW: 完成人工确认后，可在 harness/state/init-status.md 中记录确认人和日期，并将状态改为 已完成。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
