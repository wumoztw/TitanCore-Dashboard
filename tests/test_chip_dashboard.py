import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import archive_old_reports
import components
import data_loader

MOCK = ROOT / "tests" / "mock_chip.csv"
SAMPLE = Path("/home/wuminchin/TitanCore/titan_core_chip/reports/2026-10-19.csv")


def _isna(value) -> bool:
    return bool(data_loader.pd.isna(value))


class ChipDashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frame, cls.meta = data_loader.load_chip_data(csv_path=str(MOCK))

    def row(self, symbol):
        return self.frame.loc[self.frame["symbol"] == symbol].iloc[0]

    def test_meta(self):
        self.assertEqual(self.meta["rows"], 4)
        self.assertEqual(self.meta["bull"], 2)  # 2454 resonance + 3008 label "多頭"
        self.assertEqual(self.meta["bear"], 1)
        self.assertEqual(self.meta["as_of"], "2026-10-19")

    def test_resonance_flags(self):
        bull, bear, neutral = self.row("2454"), self.row("2330"), self.row("2409")
        self.assertTrue(bull["is_resonance_bull"] and not bull["is_resonance_bear"])
        self.assertTrue(bear["is_resonance_bear"] and not bear["is_resonance_bull"])
        self.assertFalse(neutral["is_resonance_bull"] or neutral["is_resonance_bear"])

    def test_streak_and_nan(self):
        self.assertEqual(int(self.row("2454")["trust_streak"]), 5)
        self.assertEqual(int(self.row("2330")["trust_streak"]), -4)
        neutral = self.row("2409")
        for col in ("trust_net_lots", "trust_streak", "short_margin_ratio", "adx"):
            self.assertTrue(_isna(neutral[col]), col)
        self.assertEqual(neutral["resonance"], "")

    def test_bool_parsing(self):
        self.assertTrue(self.row("2409")["data_stale"])
        self.assertFalse(self.row("2454")["data_stale"])
        self.assertFalse(self.row("3008")["data_stale"])

    def test_empty_and_missing_columns(self):
        empty = data_loader.enrich_chip_frame(data_loader.pd.DataFrame())
        self.assertTrue(empty.empty)
        self.assertIn("is_resonance_bull", empty.columns)
        self.assertEqual(components.render_kpi_metrics(empty)["scanned"], 0)

    def test_real_sample_if_present(self):
        if not SAMPLE.is_file():
            self.skipTest("sample report missing")
        frame, meta = data_loader.load_chip_data(csv_path=str(SAMPLE))
        self.assertGreater(meta["rows"], 0)
        self.assertIn("is_resonance_bull", frame.columns)

    def test_card_bull_bear_neutral(self):
        bull = components.render_chip_card(self.row("2454").to_dict())
        for text in ("2454", "聯發科", "雙共振多頭", "ADX", "TWSE%3A2454", "tc-card bull"):
            self.assertIn(text, bull)
        bear = components.render_chip_card(self.row("2330").to_dict())
        self.assertIn("雙共振空頭", bear)
        self.assertIn("tc-card bear", bear)
        neutral = components.render_chip_card(self.row("2409").to_dict())
        self.assertIn("2409", neutral)
        self.assertIn("NEUTRAL", neutral)
        self.assertIn("—", neutral)

    def test_card_escapes_html(self):
        card = components.render_chip_card(self.row("3008").to_dict())
        self.assertNotIn("<script>", card)
        self.assertNotIn("<b>大立光", card)
        self.assertIn("&lt;script&gt;", card)

    def test_card_modal_view(self):
        card = components.render_chip_card(self.row("2454").to_dict(), modal_view=True)
        self.assertIn("資料日", card)

    def test_tradingview_url(self):
        self.assertEqual(components.tradingview_url("2330"),
                         "https://tw.tradingview.com/chart/?symbol=TWSE%3A2330")
        self.assertEqual(components.tradingview_url(" 2330 "), components.tradingview_url("2330"))
        self.assertNotIn("/", components.tradingview_url("a/b").split("symbol=")[1])

    def test_kpis(self):
        kpis = components.render_kpi_metrics(self.frame)
        self.assertEqual(kpis, {"scanned": 4, "bull": 2, "bear": 1, "trust_active": 2})

    def test_palette(self):
        self.assertEqual(components.apply_palette("tw"), components.DASHBOARD_CSS)
        self.assertIn("--tc-bull: #10b981;", components.apply_palette("intl"))

    def test_resolve_latest_label(self):
        latest = data_loader.DATA_DIR / "latest.csv"
        self.assertEqual(data_loader.resolve_csv_path(as_of="最新 (Latest)"), latest)
        self.assertEqual(data_loader.resolve_csv_path(as_of="latest"), latest)
        self.assertEqual(data_loader.resolve_csv_path(), latest)

    def test_available_dates_latest_first(self):
        dates = data_loader.get_available_dates()
        self.assertEqual(dates[0], "最新 (Latest)")
        self.assertIn("2026-10-22", dates)
        _, meta = data_loader.load_chip_data(as_of=dates[0])
        self.assertEqual(meta["as_of"], data_loader.latest_csv_date())

    def test_render_kpi_cards(self):
        html_out = components.render_kpi_cards({"scanned": 111, "bull": 22, "bear": 33, "trust_active": 44})
        self.assertIn("tc-kpi-grid", html_out)
        for v in ("111", "22", "33", "44"):
            self.assertIn(f">{v}<", html_out)


class ArchiveOldReportsTests(unittest.TestCase):
    def _make(self, tmp, n):
        for i in range(n):
            (Path(tmp) / f"2026-01-{i + 1:02d}.csv").write_text("a\n")
        (Path(tmp) / "latest.csv").write_text("a\n")

    def test_skips_when_under_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make(tmp, 5)
            self.assertEqual(archive_old_reports.archive_old_reports(Path(tmp), keep=10), [])
            self.assertFalse((Path(tmp) / "archive").exists())

    def test_archives_oldest(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make(tmp, 5)
            moved = archive_old_reports.archive_old_reports(Path(tmp), keep=3)
            self.assertEqual([p.name for p in moved], ["2026-01-01.csv", "2026-01-02.csv"])
            remaining = sorted(p.name for p in Path(tmp).glob("*.csv"))
            self.assertEqual(remaining, ["2026-01-03.csv", "2026-01-04.csv", "2026-01-05.csv", "latest.csv"])
            with zipfile.ZipFile(Path(tmp) / "archive" / archive_old_reports.ARCHIVE_NAME) as zf:
                self.assertEqual(sorted(zf.namelist()), ["2026-01-01.csv", "2026-01-02.csv"])


if __name__ == "__main__":
    unittest.main()
