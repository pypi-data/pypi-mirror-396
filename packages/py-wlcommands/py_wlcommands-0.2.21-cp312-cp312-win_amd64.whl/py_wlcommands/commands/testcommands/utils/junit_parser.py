from __future__ import annotations

import xml.etree.ElementTree
from pathlib import Path


def read_xml(path: str) -> xml.etree.ElementTree.Element | None:
    """读取XML文件并返回其根元素。"""
    p = Path(path)
    if not p.exists():
        return None
    try:
        tree = xml.etree.ElementTree.parse(str(p))
        return tree.getroot()
    except Exception:
        return None


def parse_junit(
    root: xml.etree.ElementTree.Element | None,
) -> tuple[int, int, int, int, int, float, list[dict[str, str]]]:
    """解析JUnit XML数据并返回测试统计信息。"""
    if root is None:
        return (0, 0, 0, 0, 0, 0.0, [])
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    tests = failures = errors = skipped = warnings = 0
    time = 0.0
    cases: list[dict[str, str]] = []
    for ts in suites:
        tests += int(ts.attrib.get("tests", 0))
        failures += int(ts.attrib.get("failures", 0))
        errors += int(ts.attrib.get("errors", 0))
        skipped += int(ts.attrib.get("skipped", 0))
        # 增加warnings计数
        warnings += int(ts.attrib.get("warnings", 0))
        try:
            time += float(ts.attrib.get("time", 0.0))
        except Exception:
            pass
        for tc in ts.findall("testcase"):
            name = tc.attrib.get("name", "")
            classname = tc.attrib.get("classname", "")
            file_attr = tc.attrib.get("file", "")
            text = ""
            kind = ""
            fail = tc.find("failure")
            err = tc.find("error")
            # 增加warning元素的查找
            warn = tc.find("warning")
            if fail is not None:
                kind = "failure"
                text = (
                    fail.attrib.get("message", "") + "\n" + (fail.text or "")
                ).strip()
            elif err is not None:
                kind = "error"
                text = (err.attrib.get("message", "") + "\n" + (err.text or "")).strip()
            elif warn is not None:
                kind = "warning"
                text = (
                    warn.attrib.get("message", "") + "\n" + (warn.text or "")
                ).strip()
            if kind:
                if len(text) > 1200:
                    text = text[:1200] + "\n..."
                cases.append(
                    {
                        "name": name,
                        "classname": classname,
                        "file": file_attr,
                        "kind": kind,
                        "text": text,
                    }
                )
    return (tests, failures, errors, skipped, warnings, time, cases)
