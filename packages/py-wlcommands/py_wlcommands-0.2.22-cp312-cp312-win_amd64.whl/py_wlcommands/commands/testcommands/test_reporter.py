from __future__ import annotations

from ...utils.logging import log_info
from .utils import (
    coverage_totals,
    file_entries,
    fmt_pct,
    get_env_info,
    parse_junit,
    read_json,
    read_xml,
    write_md,
)

# Re-export private functions for backward compatibility (used in tests)
_coverage_totals = coverage_totals
_file_entries = file_entries
_fmt_pct = fmt_pct
_get_env_info = get_env_info
_parse_junit = parse_junit
_read_json = read_json
_read_xml = read_xml
_write_md = write_md


def generate_reports(
    coverage_json_path: str,
    junit_xml_path: str,
    out_cov: str,
    out_err: str,
    project_root: str,
) -> str:
    try:
        log_info(f"Generating coverage report to: {out_cov}", lang="en")
        log_info(f"Generating error report to: {out_err}", lang="en")
        log_info(f"Coverage JSON source: {coverage_json_path}", lang="en")
        log_info(f"JUnit XML source: {junit_xml_path}", lang="en")
        log_info(f"生成覆盖率报告到: {out_cov}", lang="zh")
        log_info(f"生成错误报告到: {out_err}", lang="zh")
        log_info(f"覆盖率JSON来源: {coverage_json_path}", lang="zh")
        log_info(f"JUnit XML来源: {junit_xml_path}", lang="zh")
    except Exception:
        pass
    cov = _read_json(coverage_json_path)
    junit = _read_xml(junit_xml_path)
    env_info = _get_env_info()

    line_pct, branch_pct, num_lines, num_branches, num_files = _coverage_totals(cov)
    files = _file_entries(cov, project_root)
    top_files = sorted(files, key=lambda x: (x[1] or 0.0), reverse=True)[:10]
    low_files = sorted(files, key=lambda x: (x[1] or 0.0))[:10]

    cov_lines: list[str] = []
    cov_lines.append("# WL 测试覆盖率报告")
    cov_lines.append("")
    cov_lines.append("## 测试环境")
    cov_lines.extend([f"- {x}" for x in env_info])
    cov_lines.append("")
    cov_lines.append("## 总览")
    cov_lines.append(f"- 行覆盖率: {fmt_pct(line_pct)}")
    cov_lines.append(f"- 分支覆盖率: {fmt_pct(branch_pct)}")
    cov_lines.append(f"- 语句数: {num_lines if num_lines else 'N/A'}")
    cov_lines.append(f"- 分支数: {num_branches if num_branches else 'N/A'}")
    cov_lines.append(f"- 文件数: {num_files}")
    cov_lines.append("")
    cov_lines.append("## Top 文件")
    for rel, lp, bp in top_files:
        cov_lines.append(f"- `{rel}` | 行 {fmt_pct(lp)} | 分支 {fmt_pct(bp)}")
    cov_lines.append("")
    cov_lines.append("## 低覆盖率文件")
    for rel, lp, bp in low_files:
        cov_lines.append(f"- `{rel}` | 行 {fmt_pct(lp)} | 分支 {fmt_pct(bp)}")

    _write_md(out_cov, cov_lines)
    try:
        log_info(f"Coverage Markdown written: {out_cov}", lang="en")
        log_info(f"覆盖率Markdown已写入: {out_cov}", lang="zh")
    except Exception:
        pass

    tests, failures, errors, skipped, warnings, time_spent, cases = _parse_junit(junit)
    err_lines: list[str] = []
    err_lines.append("# WL 测试错误报告")
    err_lines.append("")
    err_lines.append("## 测试环境")
    err_lines.extend([f"- {x}" for x in env_info])
    err_lines.append("")
    err_lines.append("## 测试统计")
    err_lines.append(f"- 总用例: {tests}")
    err_lines.append(f"- 失败: {failures}")
    err_lines.append(f"- 错误: {errors}")
    err_lines.append(f"- 跳过: {skipped}")
    err_lines.append(f"- 警告: {warnings}")
    err_lines.append(f"- 总时长: {time_spent:.2f}s")
    err_lines.append("")

    # 分别收集不同类型的问题
    failure_cases = [c for c in cases if c.get("kind") == "failure"]
    error_cases = [c for c in cases if c.get("kind") == "error"]
    warning_cases = [c for c in cases if c.get("kind") == "warning"]

    # 显示失败明细
    if failure_cases:
        err_lines.append("## 失败明细")
        for c in failure_cases:
            loc = c.get("file") or c.get("classname") or ""
            err_lines.append(
                f"- 用例: `{c.get('name', '')}` @ `{loc}` [{c.get('kind', '')}]"
            )
            err_lines.append("")
            err_lines.append("```")
            err_lines.append(c.get("text", ""))
            err_lines.append("```")
            err_lines.append("")

    # 显示错误明细
    if error_cases:
        err_lines.append("## 错误明细")
        for c in error_cases:
            loc = c.get("file") or c.get("classname") or ""
            err_lines.append(
                f"- 用例: `{c.get('name', '')}` @ `{loc}` [{c.get('kind', '')}]"
            )
            err_lines.append("")
            err_lines.append("```")
            err_lines.append(c.get("text", ""))
            err_lines.append("```")
            err_lines.append("")

    # 显示警告明细
    if warning_cases:
        err_lines.append("## 警告明细")
        for c in warning_cases:
            loc = c.get("file") or c.get("classname") or ""
            err_lines.append(
                f"- 用例: `{c.get('name', '')}` @ `{loc}` [{c.get('kind', '')}]"
            )
            err_lines.append("")
            err_lines.append("```")
            err_lines.append(c.get("text", ""))
            err_lines.append("```")
            err_lines.append("")

    _write_md(out_err, err_lines)
    try:
        log_info(f"Error Markdown written: {out_err}", lang="en")
        log_info(f"错误Markdown已写入: {out_err}", lang="zh")
    except Exception:
        pass

    summary = f"总行覆盖率 {fmt_pct(line_pct)} | 分支覆盖率 {fmt_pct(branch_pct)} | 文件数 {num_files} | 失败用例 {failures + errors}"
    return summary
