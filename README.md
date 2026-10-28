# Macro Market Analytics

A Python command-line tool for analyzing cross-asset market data and basic macro-financial relationships.

#### Video Demo: https://youtu.be/8rP2XmuVmOM 

## Overview

Macro Market Analytics reads daily market data from a CSV file and generates a report covering equities, commodities, the US dollar and Treasury yields.

The report includes performance, annualized volatility, maximum drawdown, the 10Y-2Y Treasury spread and correlations between selected assets.

This project was originally built as my final project for Harvard's **CS50P (Introduction to Programming with Python)**. The first version uses a local CSV file rather than an API, which keeps the project simple and reproducible.

## Example output

Running the program on the sample dataset produces a plain-text report:

```
==================================================
              RAPPORT FINANCIER CS50P
Période : du 2026-08-20 au 2026-08-27
==================================================
1. ACTIONS (S&P 500)
--------------------------------------------------
  • Performance : +1.10%
  • Volatilité  : 9.76%
  • Max Drawdown: -0.82%
2. MATIÈRES PREMIÈRES
--------------------------------------------------
  • Or (Perf / Vol / MaxDD) : +2.29% | 9.24% | -0.31%
  • Pétrole (Performance)   : +3.26%
3. DEVISES (US Dollar Index - DXY)
--------------------------------------------------
  • Performance : -0.49%
  • Volatilité  : 4.88%
  • Max Drawdown: -0.88%
4. TAUX & MACRO
--------------------------------------------------
  • Niveaux récents     : US2Y = 4.05% | US10Y = 4.30%
  • Spread US10Y - US2Y : +25.0 bps
5. CORRÉLATIONS CROSS-ASSET
--------------------------------------------------
  • Dollar / Or (DXY vs Gold)      : -0.65
  • Taux 10Y / Actions (10Y vs SPX): -0.57
  • Taux 10Y / Dollar (10Y vs DXY) : +0.97
==================================================
```

## Project structure

| File                   | Purpose                                    |
| ---------------------- | ------------------------------------------ |
| `project.py`           | Main program and analytics functions       |
| `test_project.py`      | Pytest tests for the calculation functions |
| `data/market_data.csv` | Sample cross-asset market data             |
| `requirements.txt`     | Python dependencies                        |
| `README.md`            | Project documentation                      |

The CSV contains the following columns:

`date, spx, gold, dxy, ust2y, ust10y, oil`

## How to run

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the program:

```bash
python project.py
```

Run the tests:

```bash
pytest
```

## Functions

* **`main()`** — Loads the data, generates the report and prints it.
* **`load_data(path)`** — Reads the CSV with pandas, converts the date column to datetime and sorts the data chronologically.
* **`compute_returns(prices)`** — Calculates simple period-to-period returns from a list of prices.
* **`annualized_volatility(returns, periods=252)`** — Calculates annualized volatility using the sample standard deviation and a 252-period convention.
* **`pairwise_correlation(a, b)`** — Calculates the Pearson correlation between two series.
* **`max_drawdown(prices)`** — Finds the largest peak-to-trough decline in a price series.
* **`calculate_yield_spread(y10, y2)`** — Calculates the difference between the 10-year and 2-year Treasury yields in basis points.
* **`generate_report(df)`** — Combines the calculations and formats the final report.

The calculation functions use regular Python lists rather than pandas Series. Pandas is mainly used when loading and preparing the CSV data.

## Design decisions

One of the main design choices was to keep the calculation functions independent from pandas. This makes them easier to test with small inputs and keeps the calculations separate from data loading and report formatting.

Volatility uses the sample standard deviation (`ddof=1`) and is annualized using 252 periods.

The functions also handle invalid inputs explicitly. For example, volatility requires at least two observations, correlation requires series of the same length, and drawdown cannot be calculated from an empty series.

For the first version, correlations are calculated on the original price or yield levels. This is a simplification; for financial analysis, correlations between returns are generally more useful. This is one of the areas that could be improved in a future version.

## Testing

The project uses `pytest` to test the main calculation functions. All tests currently pass:

```
........                                                                 [100%]
8 passed
```

The tests cover both normal cases and invalid inputs, including:

* return calculations;
* annualized volatility;
* Pearson correlation;
* maximum drawdown;
* Treasury yield spreads;
* empty inputs;
* mismatched series lengths;
* zero-variance series.

`pytest.approx` is used where necessary because of normal floating-point differences in Python calculations.

## Limitations and future improvements

The current version uses a static CSV dataset. Possible improvements include:

* retrieving market data through APIs such as FRED or `yfinance`;
* calculating correlations using returns;
* adding rolling volatility and correlations;
* studying market reactions around events such as FOMC, CPI and NFP releases;
* adding simple macro-regime classification;
* adding charts and exporting the report.

The goal of these improvements would be to turn the current command-line tool into a more complete macro research tool.
