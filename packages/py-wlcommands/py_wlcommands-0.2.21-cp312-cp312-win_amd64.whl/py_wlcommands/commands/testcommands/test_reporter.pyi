from ...utils.logging import log_info as log_info
from .utils import coverage_totals as coverage_totals, file_entries as file_entries, fmt_pct as fmt_pct, get_env_info as get_env_info, parse_junit as parse_junit, read_json as read_json, read_xml as read_xml, write_md as write_md

def generate_reports(coverage_json_path: str, junit_xml_path: str, out_cov: str, out_err: str, project_root: str) -> str: ...
