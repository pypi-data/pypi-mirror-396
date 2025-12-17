"""Format reporter module."""

from pathlib import Path


class FormatReporter:
    """Reporter for format command."""

    def generate_format_report(self, quiet, unsafe, paths, env):
        """Generate format report."""
        # Create todos directory if it doesn't exist
        todos_dir = Path("todos")
        todos_dir.mkdir(exist_ok=True)

        # Generate report content
        report_lines = []
        report_lines.append("# Format Report\n")
        report_lines.append("## Configuration\n")
        report_lines.append(f"- Quiet mode: {quiet}\n")
        report_lines.append(f"- Unsafe fixes: {unsafe}\n")
        report_lines.append(
            f"- Custom paths: {paths if paths else 'None (using defaults)'}\n"
        )

        # Save report
        report_path = todos_dir / "format_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

        if not quiet:
            print(f"Format report generated at {report_path}")
