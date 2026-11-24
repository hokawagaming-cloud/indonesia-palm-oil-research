"""Checks of quant/levy_duty.py against values read directly from primary regulation
texts (PMK annexes) and, for the Nov 2026 reference price, the Kemendag decree."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "quant"))
from levy_duty import duty_usd_t, levy_usd_t  # noqa: E402


def test_nov_2026_duty_and_levy():
    # HRef Nov 2026 = USD 978.90 (Kepmendag 2064/2026); PMK 68/2025 band 930-980 -> col 7 = 124
    d, rid = duty_usd_t("2026-11-15", 978.90)
    assert (d, rid) == (124, "D11")
    lv, lrid = levy_usd_t("2026-11-15", 978.90)
    assert lrid == "L19" and lv == pytest.approx(122.36, abs=0.01)  # 12.5% (PMK 9/2026)


def test_oct_2026_duty_band():
    assert duty_usd_t("2026-10-15", 1042.15)[0] == 178  # band 1030-1080 -> col 9


def test_duty_band_edges_pmk38():
    assert duty_usd_t("2024-07-01", 680.0)[0] == 0      # <= 680 -> col 1
    assert duty_usd_t("2024-07-01", 680.01)[0] == 3     # > 680 -> col 2
    assert duty_usd_t("2024-07-01", 1500)[0] == 288     # > 1430 -> col 17


def test_old_duty_regime_12_bands():
    assert duty_usd_t("2018-06-15", 760)[0] == 3        # PMK 13/2017, 750-800 -> 3
    assert duty_usd_t("2018-06-15", 1300)[0] == 200     # > 1250


def test_levy_episodes():
    assert levy_usd_t("2016-05-01", None)[0] == 50       # fixed USD 50 (PMK 133/2015 as amended)
    assert levy_usd_t("2019-04-15", 650)[0] == 0         # PMK 23/2019 zero window to 31 May 2019
    assert levy_usd_t("2019-07-15", 600)[0] == 25        # 570-619 band
    assert levy_usd_t("2020-07-15", None)[0] == 55       # PMK 57/2020 flat
    assert levy_usd_t("2020-12-15", 680)[0] == 60        # PMK 191/2020, 670-695
    assert levy_usd_t("2022-04-15", 1600)[0] == 375      # PMK 23/2022 top band
    assert levy_usd_t("2022-08-15", 1200)[0] == 0        # suspension (PMK 115/2022)
    assert levy_usd_t("2022-10-15", 900)[0] == 0         # suspension extended (PMK 130/2022)
    assert levy_usd_t("2022-11-15", 790)[0] == 0         # PMK 154/2022: HRef < 800 -> 0 until 31 Dec 2022
    assert levy_usd_t("2022-11-15", 810)[0] == 85        # >= 800
    assert levy_usd_t("2023-03-15", 900)[0] == 95        # 880-930 band from 1 Jan 2023
    assert levy_usd_t("2025-01-15", 1000)[0] == pytest.approx(75.0)   # 7.5% (PMK 62/2024)
    assert levy_usd_t("2025-06-15", 900)[0] == pytest.approx(90.0)    # 10% (PMK 30/2025)


def test_no_regime_before_coverage():
    v, rid = duty_usd_t("2015-03-15", 700)
    assert rid is None  # PMK 75/2012-era duty regimes not reconstructed


def test_monthly_series_matches_independent_press_reports():
    """Secondary cross-checks (DDTC / Katadata / Kontan, S-010) against the built series."""
    import pandas as pd
    m = pd.read_csv(Path(__file__).resolve().parents[1] / "data" / "reference" / "cpo_levy_duty_monthly.csv").set_index("month")
    assert m.loc["2026-11", "duty_usd_t"] == 124 and abs(m.loc["2026-11", "levy_usd_t"] - 122.36) < 0.01
    assert m.loc["2026-10", "duty_usd_t"] == 178 and m.loc["2026-10", "hrf_usd_t"] == 1042.15
    assert m.loc["2026-09", "duty_usd_t"] == 148 and abs(m.loc["2026-09", "levy_usd_t"] - 125.9389) < 0.01
    assert m.loc["2026-08", "duty_usd_t"] == 148 and m.loc["2026-08", "hrf_usd_t"] == 996.52
    assert m.loc["2026-05", "duty_usd_t"] == 178
    assert m.loc["2026-03", "hrf_usd_t"] == 938.87
