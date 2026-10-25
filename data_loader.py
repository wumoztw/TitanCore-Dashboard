"""Load titan_core_chip CSV/Markdown reports for the dashboard."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd

try:
    import streamlit as st
except Exception:  # pragma: no cover - tests may run without streamlit
    st = None

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
FALLBACK_REPORTS = Path("/home/wuminchin/TitanCore/titan_core_chip/reports")
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")

NUMERIC_COLS = [
    "close", "adx", "atr", "trust_net_lots", "trust_streak", "trust_5d_lots",
    "trust_capital_ratio_pct", "foreign_net_lots", "foreign_streak", "foreign_5d_lots",
    "dealer_hedge_lots", "margin_diff_5d", "short_diff_5d", "short_margin_ratio",
    "whale_1000_pct", "whale_diff_pct", "small_holder_people_diff", "volume_lots",
]
DATE_COLS = ["date", "inst_date", "margin_date"]
BOOL_COLS = ["trust_first_buy", "squeeze", "data_stale"]


def _report_dirs() -> list[Path]:
    dirs = [DATA_DIR]
    if FALLBACK_REPORTS.is_dir():
        dirs.append(FALLBACK_REPORTS)
    return dirs


def _dated_csvs(directories: Iterable[Path] | None = None) -> list[tuple[str, Path]]:
    found: list[tuple[str, Path]] = []
    for directory in directories or _report_dirs():
        if not directory.is_dir():
            continue
        for path in directory.glob("*.csv"):
            match = DATE_RE.fullmatch(path.stem)
            if match:
                found.append((match.group(1), path))
    found.sort(key=lambda item: (item[0], 0 if "TitanCore-Dashboard" in str(item[1].parent) or item[1].parent == DATA_DIR else 1))
    return found


def get_available_dates() -> list[str]:
    """Return report dates newest first."""
    dates = sorted({day for day, _ in _dated_csvs()}, reverse=True)
    return dates


def resolve_csv_path(csv_path: str | Path | None = None, as_of: str | None = None) -> Path | None:
    if csv_path:
        path = Path(csv_path)
        return path if path.is_file() else None
    if as_of:
        for day, path in _dated_csvs():
            if day == as_of:
                return path
    latest = DATA_DIR / "latest.csv"
    if latest.is_file():
        return latest
    dated = _dated_csvs()
    if dated:
        return dated[-1][1]
    for directory in _report_dirs():
        candidate = directory / "latest.csv"
        if candidate.is_file():
            return candidate
    return None


def resolve_markdown_path(md_path: str | Path | None = None) -> Path | None:
    if md_path:
        path = Path(md_path)
        return path if path.is_file() else None
    for directory in _report_dirs():
        candidate = directory / "latest.md"
        if candidate.is_file():
            return candidate
    return None


def _to_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "y"}


def _label_has(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


def enrich_chip_frame(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy()
    for col in NUMERIC_COLS:
        if col not in frame.columns:
            frame[col] = pd.NA
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    for col in DATE_COLS:
        if col not in frame.columns:
            frame[col] = pd.NaT
        frame[col] = pd.to_datetime(frame[col], errors="coerce")
    for col in BOOL_COLS:
        if col not in frame.columns:
            frame[col] = False
        frame[col] = frame[col].map(_to_bool)
    for col in ("symbol", "name", "category", "chip_category", "resonance", "resonance_label",
                "tech_action", "ema_trend", "ichimoku_trend", "bollinger_signal", "signals", "summary_note"):
        if col not in frame.columns:
            frame[col] = ""
        frame[col] = frame[col].fillna("").astype(str)
    resonance = frame["resonance"].str.upper()
    label = frame["resonance_label"]
    bull_code = (resonance == "RESONANCE_BULL").astype(bool)
    bear_code = (resonance == "RESONANCE_BEAR").astype(bool)
    bull_label = label.map(lambda text: _label_has(text, ("多頭", "💎"))).astype(bool)
    bear_label = label.map(lambda text: _label_has(text, ("空頭", "💀"))).astype(bool)
    frame["is_resonance_bull"] = bull_code | bull_label
    frame["is_resonance_bear"] = bear_code | bear_label
    frame["trust_streak"] = frame["trust_streak"].astype("Float64")
    return frame


def _read_csv(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, encoding="utf-8-sig")
    # Backtest trade dumps are not chip radar rows.
    if "chip_category" not in frame.columns and "resonance" not in frame.columns and "group" in frame.columns:
        raise ValueError(f"not a chip radar CSV: {path}")
    return enrich_chip_frame(frame)


def load_chip_data(csv_path: str | None = None, as_of: str | None = None):
    """Return ``(dataframe, metadata)``. Cached for 5 minutes inside Streamlit."""
    path = resolve_csv_path(csv_path, as_of=as_of)
    if path is None:
        empty = enrich_chip_frame(pd.DataFrame())
        return empty, {"source": None, "as_of": None, "rows": 0, "loaded_at": datetime.now().isoformat(timespec="seconds")}
    frame = _read_csv(path)
    as_of_date = None
    if not frame.empty and frame["date"].notna().any():
        as_of_date = frame["date"].dropna().max().strftime("%Y-%m-%d")
    else:
        match = DATE_RE.search(path.stem)
        as_of_date = match.group(1) if match else None
    meta = {
        "source": str(path),
        "as_of": as_of_date,
        "rows": int(len(frame)),
        "bull": int(frame["is_resonance_bull"].sum()) if not frame.empty else 0,
        "bear": int(frame["is_resonance_bear"].sum()) if not frame.empty else 0,
        "loaded_at": datetime.now().isoformat(timespec="seconds"),
    }
    return frame, meta


def load_latest_summary_md(md_path: str | None = None) -> str:
    path = resolve_markdown_path(md_path)
    if path is None:
        return "_尚無盤後 Markdown 報告。請先執行 titan_core_chip 或 sync_chip_report.sh。_"
    return path.read_text(encoding="utf-8")


def _cache(func):
    if st is None:
        return func
    return st.cache_data(ttl=300)(func)


load_chip_data = _cache(load_chip_data)
load_latest_summary_md = _cache(load_latest_summary_md)
