import math
import statistics
import sys

import pandas as pd


def main():
    df = load_data("data/market_data.csv")
    report = generate_report(df)
    print(report)


def load_data(path):
    """Lit le CSV et renvoie un DataFrame propre.
    pandas vit UNIQUEMENT ici. Colonnes attendues :
    date, spx, gold, dxy, ust2y, ust10y, oil
    'date' est parsée en datetime et triée croissant.
    """
    try:
        df = pd.read_csv(path, parse_dates=["date"])
        df = df.sort_values("date").reset_index(drop=True)
        return df
    except FileNotFoundError:
        sys.exit(f"Erreur : le fichier '{path}' est introuvable.")


def compute_returns(prices):
    """Rendements simples à partir d'une liste de niveaux/prix.
    [p0, p1, p2] -> [p1/p0 - 1, p2/p1 - 1]
    Moins de 2 éléments -> liste vide [].
    """
    returns = []

    for i in range(1, len(prices)):
        returns.append(prices[i] / prices[i - 1] - 1)

    return returns


def annualized_volatility(returns, periods=252):
    """Volatilité annualisée = stdev(returns, ddof=1) * sqrt(periods).
    Raises:
        ValueError: si returns est vide.
        ValueError: si returns contient un seul rendement.
    [0.0, 0.0, 0.0] -> 0.0
    """
    if len(returns) < 2:
        raise ValueError("Au moins deux rendements sont requis.")
    mean = sum(returns) / len(returns)
    squared_deviations = [(r - mean) ** 2 for r in returns]
    variance = sum(squared_deviations) / (len(returns) - 1)
    standard_deviation = math.sqrt(variance)
    return standard_deviation * math.sqrt(periods)


def pairwise_correlation(a, b):
    """Corrélation de Pearson (plein échantillon) entre deux listes -> float.
    Raises:
        ValueError: si len(a) != len(b).
        ValueError: si moins de 2 observations.
        ValueError: si la variance de a ou de b est nulle.
    """
    # 1. Vérification des longueurs égales
    if len(a) != len(b):
        raise ValueError("Les deux listes doivent avoir la même longueur.")
    # 2. Vérification du nombre minimum d'observations
    if len(a) < 2:
        raise ValueError("Au moins 2 observations sont requises.")
    mean_a = statistics.mean(a)
    mean_b = statistics.mean(b)
    # 3. Calcul du numérateur et du dénominateur (Pearson)
    num = sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b))
    denom_a = sum((x - mean_a) ** 2 for x in a)
    denom_b = sum((y - mean_b) ** 2 for y in b)
    denom = math.sqrt(denom_a * denom_b)
    # 4. Détection d'une variance nulle (dénominateur == 0)
    if denom == 0:
        raise ValueError("La variance de l'une des séries est nulle.")
    return num / denom


def max_drawdown(prices):
    """Drawdown maximal en décimal (valeur <= 0.0).
    Pour chaque t : price_t / running_max_t - 1 ; on renvoie le minimum.
    Ex : [100, 120, 90, 130, 80] -> -0.3846
    """
    # Garde-fou : liste vide
    if not prices:
        raise ValueError("La liste de prix ne peut pas être vide.")
    running_max = prices[0]
    max_dd = 0.0
    for price in prices:
        # 1. Mise à jour du sommet historique courant
        running_max = max(running_max, price)
        # 2. Calcul du drawdown au point courant
        drawdown = (price / running_max) - 1.0
        # 3. Conservation de la perte la plus sévère (le minimum)
        if drawdown < max_dd:
            max_dd = drawdown
    return max_dd


def calculate_yield_spread(y10, y2):
    """Spread de taux en points de base : (y10 - y2) * 100.
    Ex : (4.5, 4.0) -> 50
    """
    # Les taux y10 et y2 sont attendus en pourcentage (ex: 4.5 pour 4.5%)
    return (y10 - y2) * 100


def generate_report(df):
    """Orchestration : extrait les colonnes du df en listes,
    appelle les fonctions pures, met en forme le bloc texte et
    renvoie une chaîne (c'est ici qu'on convertit décimal -> %).
    """
    # 0. Période analysée
    start_date = df["date"].iloc[0].strftime("%Y-%m-%d")
    end_date = df["date"].iloc[-1].strftime("%Y-%m-%d")
    # 1. Extraction des colonnes Pandas sous forme de listes Python
    spx = df["spx"].tolist()
    gold = df["gold"].tolist()
    dxy = df["dxy"].tolist()
    ust2y = df["ust2y"].tolist()
    ust10y = df["ust10y"].tolist()
    oil = df["oil"].tolist()
    # 2. Calculs du S&P 500 (SPX)
    spx_perf = (spx[-1] / spx[0]) - 1.0
    spx_ret = compute_returns(spx)
    spx_vol = annualized_volatility(spx_ret)
    spx_mdd = max_drawdown(spx)
    # 3. Calculs de l'Or (Gold)
    gold_perf = (gold[-1] / gold[0]) - 1.0
    gold_ret = compute_returns(gold)
    gold_vol = annualized_volatility(gold_ret)
    gold_mdd = max_drawdown(gold)
    oil_perf = (oil[-1] / oil[0]) - 1.0
    # 4. Calculs du US Dollar Index (DXY)
    dxy_perf = (dxy[-1] / dxy[0]) - 1.0
    dxy_ret = compute_returns(dxy)
    dxy_vol = annualized_volatility(dxy_ret)
    dxy_mdd = max_drawdown(dxy)
    # 5. Macro & Corrélations
    ust2y_level = ust2y[-1]
    ust10y_level = ust10y[-1]
    current_spread = calculate_yield_spread(ust10y_level, ust2y_level)
    corr_dxy_gold = pairwise_correlation(dxy, gold)
    corr_rates_spx = pairwise_correlation(ust10y, spx)
    corr_rates_dxy = pairwise_correlation(ust10y, dxy)
    # 6. Formatage du rapport en texte brut
    report = f"""==================================================
              RAPPORT FINANCIER CS50P
Période : du {start_date} au {end_date}
==================================================
1. ACTIONS (S&P 500)
--------------------------------------------------
  • Performance : {spx_perf * 100:+.2f}%
  • Volatilité  : {spx_vol * 100:.2f}%
  • Max Drawdown: {spx_mdd * 100:.2f}%
2. MATIÈRES PREMIÈRES
--------------------------------------------------
  • Or (Perf / Vol / MaxDD) : {gold_perf * 100:+.2f}% | {gold_vol * 100:.2f}% | {gold_mdd * 100:.2f}%
  • Pétrole (Performance)   : {oil_perf * 100:+.2f}%
3. DEVISES (US Dollar Index - DXY)
--------------------------------------------------
  • Performance : {dxy_perf * 100:+.2f}%
  • Volatilité  : {dxy_vol * 100:.2f}%
  • Max Drawdown: {dxy_mdd * 100:.2f}%
4. TAUX & MACRO
--------------------------------------------------
  • Niveaux récents     : US2Y = {ust2y_level:.2f}% | US10Y = {ust10y_level:.2f}%
  • Spread US10Y - US2Y : {current_spread:+.1f} bps
5. CORRÉLATIONS CROSS-ASSET
--------------------------------------------------
  • Dollar / Or (DXY vs Gold)      : {corr_dxy_gold:+.2f}
  • Taux 10Y / Actions (10Y vs SPX): {corr_rates_spx:+.2f}
  • Taux 10Y / Dollar (10Y vs DXY) : {corr_rates_dxy:+.2f}
==================================================
"""
    return report


if __name__ == "__main__":
    main()
