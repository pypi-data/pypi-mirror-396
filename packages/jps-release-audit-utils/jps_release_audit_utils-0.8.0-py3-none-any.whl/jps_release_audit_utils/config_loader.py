import logging
import yaml
import typer

from typing import Dict, Optional, Tuple
from pathlib import Path

from .constants import DEFAULT_COLORS, DEFAULT_SHEET_NAMES


logger = logging.getLogger(__name__)

# ============================================================
# CONFIG LOADER
# ============================================================

def load_config(
    config_path: Optional[Path],
    required: bool = False,
) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Load sheet names and colors from a YAML config file.

    YAML example:

    sheets:
      timeline_by_date: "Timeline (by Date)"
      timeline_by_topology: "Timeline (Topology)"
      timeline_hybrid: "Timeline (Hybrid)"
      analytics_summary: "Analytics"

    colors:
      missing: "FFC7CE"
      all_present: "C6EFCE"
      out_of_order: "FFEB9C"
    """
    sheet_names = DEFAULT_SHEET_NAMES.copy()
    colors = DEFAULT_COLORS.copy()

    if config_path is None:
        logger.info("No config path supplied; using built-in defaults.")
        return sheet_names, colors

    if not config_path.is_file():
        if required:
            raise typer.Exit(f"ERROR: Config file not found: {config_path}")
        logger.info("Config file not found at %s; using built-in defaults.", config_path)
        return sheet_names, colors

    logger.info("Loading configuration from %s", config_path)

    with config_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    sheets_cfg = data.get("sheets", {})
    for key, default_name in DEFAULT_SHEET_NAMES.items():
        if key in sheets_cfg and sheets_cfg[key]:
            sheet_names[key] = str(sheets_cfg[key])

    colors_cfg = data.get("colors", {})
    for key, default_color in DEFAULT_COLORS.items():
        if key in colors_cfg and colors_cfg[key]:
            colors[key] = str(colors_cfg[key])

    logger.debug("Effective sheet names: %s", sheet_names)
    logger.debug("Effective colors: %s", colors)

    return sheet_names, colors

