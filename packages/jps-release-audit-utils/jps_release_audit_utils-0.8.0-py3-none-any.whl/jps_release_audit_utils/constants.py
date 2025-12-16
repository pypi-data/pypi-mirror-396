import re

from pathlib import Path


# Default config path: src/jps_release_audit_utils/conf/config.yaml
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "conf" / "config.yaml"

DEFAULT_SHEET_NAMES = {
    "timeline_by_date": "timeline_by_date",
    "timeline_by_topology": "timeline_by_topology",
    "timeline_hybrid": "timeline_hybrid",
    "analytics_summary": "analytics_summary",
}

DEFAULT_COLORS = {
    "missing": "FFC7CE",      # light red
    "all_present": "C6EFCE",  # light green
    "out_of_order": "FFEB9C", # light yellow
}


PR_REGEX = re.compile(r"#(\d+)")
