# 📈 AlphaQuant — PVI & RSI Convergence Strategy Engine

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/Plotly-5.x-3F4F75?style=for-the-badge&logo=plotly&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
</p>

> **A professional-grade quantitative trading strategy dashboard** that implements a dual-indicator confluence approach using the **Positive Volume Index (PVI)** and **Relative Strength Index (RSI)** to generate buy/sell signals, manage positions, and backtest performance — all in an interactive web interface.

---

## 🧠 Strategy Overview

This project implements a **two-condition confluence trading strategy** designed to capture momentum shifts confirmed by volume:

| Signal | Indicator | Condition |
|--------|-----------|-----------|
| **Trend Filter** | PVI (Positive Volume Index) | Price of PVI > EMA of PVI → Bullish volume participation |
| **Momentum Trigger** | RSI (Relative Strength Index) | RSI crosses above/below 50 → Momentum confirmation |

### Logic
- **BUY**: RSI crosses **above 50** AND PVI is above its EMA (volume confirms the move)
- **SELL**: RSI crosses **below 50** (momentum loss triggers exit)

This confluence approach filters out false signals by requiring both volume-driven price action (PVI) and momentum confirmation (RSI) before entering a trade.

---

## 🗂️ Project Structure

```
strategy_with_position_management/
│
├── app.py                                  # Streamlit dashboard (interactive UI)
├── strategy_with_position_management.ipynb # Research notebook (strategy development)
├── requirements.txt                        # Python dependencies
├── .gitignore                              # Git exclusions
└── README.md                              # This file
```

---

## ✨ Features

### 📊 Interactive Dashboard (`app.py`)
- **Real-time data fetching** via Yahoo Finance for any ticker symbol
- **CSV upload** support for custom market data
- **Configurable parameters**: PVI lookback, RSI period, starting capital
- **Live backtesting** with equity curve visualization
- **Trade log** with full entry/exit history
- **Glassmorphism dark UI** with premium aesthetic (Inter font, smooth animations)

### 🔬 Research Notebook (`.ipynb`)
- Step-by-step strategy development on `GOOGL` (5-year historical data)
- PVI & RSI indicator construction with `pandas_ta`
- Position management logic with shift-based signal generation
- Visualization with `matplotlib` and `seaborn`

### 🛡️ Robustness
- **Fallback indicator engine**: Pure NumPy/Pandas PVI & RSI if `pandas_ta` is unavailable
- **Multi-index column handling** for newer yfinance API versions
- Full error catching with debug expander in UI

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/strategy_with_position_management.git
cd strategy_with_position_management
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the Streamlit app
```bash
streamlit run app.py
```
The dashboard will open at `http://localhost:8501`.

---

## 📷 Screenshots

> Enter a ticker (e.g. `NVDA`, `AAPL`, `GOOGL`), select a date range, and hit **Initialize Pipeline** to run the strategy.

The dashboard provides:
- Price chart with **▲ BUY / ▼ SELL** markers
- RSI subplot with 50-level crossover visualization
- PVI subplot tracking volume participation
- Equity growth curve
- Trade execution log

---

## 📐 Technical Details

### Positive Volume Index (PVI)
The PVI only updates on days when trading volume *increases* relative to the prior day:

```
PVIₜ = PVIₜ₋₁ × (1 + (Closeₜ - Closeₜ₋₁) / Closeₜ₋₁)   if Volumeₜ > Volumeₜ₋₁
PVIₜ = PVIₜ₋₁                                               otherwise
```

A rising PVI above its EMA indicates **smart money** (institutional) participation.

### RSI (Wilder's Smoothed Moving Average)
```
RSI = 100 - (100 / (1 + RS))
RS  = Avg Gain (n periods) / Avg Loss (n periods)
```

Crossing the **50 midline** is used as a trend-shift trigger rather than traditional overbought/oversold levels.

---

## 🛠️ Technologies Used

| Technology | Role |
|-----------|------|
| `Python 3.9+` | Core language |
| `Streamlit` | Interactive web dashboard |
| `Plotly` | Interactive charts & subplots |
| `yfinance` | Market data acquisition |
| `pandas_ta` | Technical indicators (PVI, RSI) |
| `pandas / numpy` | Data manipulation & fallback calculations |
| `matplotlib / seaborn` | Notebook visualizations |

---

## ⚠️ Disclaimer

> This project is built **for educational and portfolio purposes only**. It does not constitute financial advice. Past performance of a backtested strategy does not guarantee future results. Always conduct your own due diligence before making investment decisions.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

Built by a passionate **Quantitative Finance & Data Science** enthusiast.  
Feel free to connect on [LinkedIn](https://linkedin.com/in/abdellahmaghous) or open an issue for questions!
