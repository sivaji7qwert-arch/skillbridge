"""
test_analyze_demand.py
------------------------
Unit tests for the trend classification and normalization functions in
analyze_demand.py. These use small synthetic inputs rather than the
full generated dataset, so they run fast and are deterministic.
"""
import pandas as pd

from analyze_demand import classify_trend, normalize_0_100


def test_classify_trend_emerging():
    assert classify_trend(growth_pct=50, recent_count=20) == "Emerging"


def test_classify_trend_growing():
    assert classify_trend(growth_pct=15, recent_count=20) == "Growing"


def test_classify_trend_stable():
    assert classify_trend(growth_pct=0, recent_count=20) == "Stable"


def test_classify_trend_declining():
    assert classify_trend(growth_pct=-25, recent_count=20) == "Declining"


def test_classify_trend_insufficient_data():
    # even with high growth, too few postings -> not a reliable signal
    assert classify_trend(growth_pct=90, recent_count=2) == "Insufficient Data"


def test_normalize_0_100_range():
    s = pd.Series([10, 20, 30, 40, 50])
    normed = normalize_0_100(s)
    assert normed.min() == 0
    assert normed.max() == 100


def test_normalize_0_100_constant_series():
    s = pd.Series([5, 5, 5])
    normed = normalize_0_100(s)
    assert (normed == 50.0).all()
