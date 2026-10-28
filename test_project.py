import math

import pytest

from project import (
    compute_returns,
    annualized_volatility,
    pairwise_correlation,
    max_drawdown,
    calculate_yield_spread,
)


def test_compute_returns():
    assert compute_returns([100, 110, 121]) == pytest.approx([0.1, 0.1])
    assert compute_returns([]) == []
    assert compute_returns([100]) == []


def test_annualized_volatility_valid():
    # Cas zéro : rendements nuls
    assert annualized_volatility([0.0, 0.0, 0.0]) == 0.0
    # Cas connu : [0.1, -0.1]
    expected_vol = math.sqrt(0.02) * math.sqrt(252)
    assert annualized_volatility([0.1, -0.1]) == pytest.approx(expected_vol)


def test_annualized_volatility_invalid():
    # Liste vide -> lève ValueError
    with pytest.raises(ValueError):
        annualized_volatility([])
    # Un seul élément -> lève ValueError
    with pytest.raises(ValueError):
        annualized_volatility([0.01])


def test_pairwise_correlation_valid():
    # Corrélation parfaite positive (b = 2a + 1)
    a = [1, 2, 3, 4]
    b = [3, 5, 7, 9]
    assert pairwise_correlation(a, b) == pytest.approx(1.0)
    # Corrélation parfaite négative (b = -a)
    c = [1, 2, 3, 4]
    d = [-1, -2, -3, -4]
    assert pairwise_correlation(c, d) == pytest.approx(-1.0)


def test_pairwise_correlation_invalid():
    # 1. Longueurs différentes
    with pytest.raises(ValueError):
        pairwise_correlation([1, 2, 3], [1, 2])
    # 2. Moins de 2 observations
    with pytest.raises(ValueError):
        pairwise_correlation([1], [2])
    # 3. Variance nulle (série constante)
    with pytest.raises(ValueError):
        pairwise_correlation([2, 2, 2], [1, 3, 5])


def test_max_drawdown_valid():
    # Cas de référence : baisse maximale de 130 à 80 (-38.46%)
    prices = [100, 120, 90, 130, 80]
    expected_dd = (80 / 130) - 1.0
    assert max_drawdown(prices) == pytest.approx(expected_dd)
    # Série strictement croissante -> aucun drawdown (0.0)
    assert max_drawdown([100, 110, 120, 130]) == 0.0
    # Cas rebond : le pire creux (-50%) est conservé malgré la remontée après 200
    assert max_drawdown([100, 50, 200, 150]) == pytest.approx(-0.5)


def test_max_drawdown_invalid():
    # Liste vide -> lève ValueError
    with pytest.raises(ValueError):
        max_drawdown([])


def test_calculate_yield_spread():
    # Cas nominal : taux 10 ans > 2 ans (50 bps)
    assert calculate_yield_spread(4.5, 4.0) == pytest.approx(50.0)

    # Inversion de courbe : taux 2 ans > 10 ans (-50 bps)
    assert calculate_yield_spread(4.0, 4.5) == pytest.approx(-50.0)

    # Taux identiques : spread nul (0 bps)
    assert calculate_yield_spread(4.2, 4.2) == pytest.approx(0.0)
