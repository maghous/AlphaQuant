import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import traceback

# Try to import pandas_ta, providing a fallback if not available
try:
    import pandas_ta as ta
    HAS_PANDAS_TA = True
except ImportError:
    HAS_PANDAS_TA = False

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="AlphaQuant | PVI & RSI Strategy",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [data-testid="stapp"] {
        font-family: 'Inter', sans-serif;
        background-color: #05070A;
    }
    
    /* Elegant Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0B0E14;
        border-right: 1px solid #1E232D;
    }
    
    /* Glassmorphism Cards */
    .metric-card {
        background: rgba(20, 26, 35, 0.8);
        border: 1px solid #1E232D;
        border-radius: 12px;
        padding: 24px;
        transition: transform 0.2s ease, border-color 0.2s ease;
        margin-bottom: 1rem;
    }
    
    .metric-card:hover {
        border-color: #3B82F6;
        transform: translateY(-2px);
    }
    
    /* Global Text & Labels */
    .stText, label, .stMarkdown p, .stMarkdown span, [data-testid="stWidgetLabel"] p {
        color: #E2E8F0 !important;
    }
    
    /* Ensure Sidebar labels are extremely legible */
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] p {
        color: #F8FAFC !important;
        font-weight: 500;
    }
    
    .metric-label {
        color: #94A3B8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    
    .metric-value {
        color: #F8FAFC;
        font-size: 1.75rem;
        font-weight: 700;
    }
    
    .profit-positive { color: #10B981 !important; }
    .profit-negative { color: #F87171 !important; }
    
    /* Styled Headers - Covering all levels */
    h1, h2, h3, h4, h5, h6 {
        color: #F8FAFC !important;
        font-weight: 700 !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #0B0E14 !important;
        color: #F8FAFC !important;
    }
    .streamlit-expanderContent {
        background-color: #0B0E14 !important;
        color: #E2E8F0 !important;
    }
    
    /* Dividers */
    hr {
        border-color: #1E232D !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #94A3B8 !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #F8FAFC !important;
        border-bottom: 2px solid #3B82F6 !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #05070A;
    }
    ::-webkit-scrollbar-thumb {
        background: #1E232D;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #334155;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# INDICATOR LOGIC (WITH FALLBACK)
# ==========================================
def calculate_pvi(close, volume):
    """Fallback PVI calculation if pandas_ta is unavailable."""
    pvi = [1000.0]  # Starting value
    for i in range(1, len(close)):
        if volume.iloc[i] > volume.iloc[i-1]:
            ret = (close.iloc[i] - close.iloc[i-1]) / close.iloc[i-1]
            pvi.append(pvi[-1] * (1 + ret))
        else:
            pvi.append(pvi[-1])
    return pd.Series(pvi, index=close.index)

def calculate_rsi(close, length=14):
    """Fallback RSI calculation if pandas_ta is unavailable."""
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=length).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=length).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ==========================================
# CORE FUNCTIONS
# ==========================================
@st.cache_data(show_spinner=False)
def load_market_data(ticker, start, end):
    try:
        df = yf.download(ticker, start=start, end=end, progress=False)
        if df.empty: return None
        # Handle multi-index columns from yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception:
        return None

def generate_simulated_data(ticker, start, end):
    """Generates synthetic market data when yfinance fails or for testing."""
    dates = pd.date_range(start=start, end=end, freq='B')
    n = len(dates)
    
    # Base price (random starting point between 50 and 200)
    base_price = np.random.uniform(50, 200)
    
    # Geometric Brownian Motion for realistic price movement
    # mu (drift) and sigma (volatility)
    mu = 0.0005
    sigma = 0.02
    
    # Calculate returns
    returns = np.random.normal(mu, sigma, n)
    prices = base_price * np.exp(np.cumsum(returns))
    
    # Generate OHLC
    data = {
        'Close': prices,
        'Adj Close': prices,
        'High': prices * (1 + np.abs(np.random.normal(0, 0.005, n))),
        'Low': prices * (1 - np.abs(np.random.normal(0, 0.005, n))),
        'Open': prices * (1 + np.random.normal(0, 0.003, n)),
        'Volume': np.random.uniform(1000000, 10000000, n).astype(int)
    }
    
    df = pd.DataFrame(data, index=dates)
    return df

def apply_strategy(df, pvi_len=20, rsi_len=20):
    df = df.copy()
    close_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
    
    if HAS_PANDAS_TA:
        df['PVI'] = ta.pvi(close=df[close_col], volume=df['Volume'], length=pvi_len)
        df['RSI'] = ta.rsi(close=df[close_col], length=rsi_len)
    else:
        df['PVI'] = calculate_pvi(df[close_col], df['Volume'])
        # PVI EMA for smoothing/signal
        df['PVI_EMA'] = df['PVI'].ewm(span=pvi_len).mean()
        df['RSI'] = calculate_rsi(df[close_col], length=rsi_len)
    
    df['RSI_Lag'] = df['RSI'].shift(1)
    df = df.dropna()
    
    # Signal Generation
    if HAS_PANDAS_TA:
        pvi_ema = df['PVI'].ewm(span=pvi_len).mean()
        df['Sig_PVI'] = np.where(df['PVI'] > pvi_ema, 1, -1)
    else:
        df['Sig_PVI'] = np.where(df['PVI'] > df['PVI_EMA'], 1, -1)
        
    # Condition 2: RSI Crossover
    df['Sig_RSI'] = 0
    df.loc[(df['RSI_Lag'] < 50) & (df['RSI'] >= 50), 'Sig_RSI'] = 1
    df.loc[(df['RSI_Lag'] > 50) & (df['RSI'] <= 50), 'Sig_RSI'] = -1
    
    # Position Determination
    df['Position'] = 0
    current_pos = 0
    positions = []
    
    for i in range(len(df)):
        if df['Sig_RSI'].iloc[i] == 1 and df['Sig_PVI'].iloc[i] == 1:
            current_pos = 1
        elif df['Sig_RSI'].iloc[i] == -1:
            current_pos = 0
            
        positions.append(current_pos)
    
    df['Position'] = positions
    df['Signals'] = df['Position'].diff()
    
    return df, close_col

def run_backtest(df, initial_capital, close_col):
    cash = initial_capital
    position = 0
    trade_history = []
    equity_history = []
    
    for date, row in df.iterrows():
        price = row[close_col]
        
        # BUY Signal
        if row['Signals'] == 1 and cash > price:
            num_shares = int(cash // price)
            if num_shares > 0:
                cost = num_shares * price
                cash -= cost
                position += num_shares
                trade_history.append({"Date": date, "Type": "BUY", "Price": price, "Shares": num_shares, "Cash": cash})
        
        # SELL Signal
        elif row['Signals'] == -1 and position > 0:
            proceeds = position * price
            cash += proceeds
            trade_history.append({"Date": date, "Type": "SELL", "Price": price, "Shares": position, "Cash": cash})
            position = 0
            
        current_equity = cash + (position * price)
        equity_history.append({"Date": date, "Equity": current_equity})
        
    equity_df = pd.DataFrame(equity_history).set_index("Date")
    trade_df = pd.DataFrame(trade_history)
    
    return equity_df, trade_df

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>⚙️ AlphaQuant</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("Data Acquisition")
    source_type = st.radio(
        "Source",
        ["Market", "Simulated", "Upload"],
        index=1,  # Default to Simulated as requested
        horizontal=True
    )
    
    if source_type == "Market":
        ticker = st.text_input("Ticker Symbol", value="NVDA").upper()
        col_A, col_B = st.columns(2)
        with col_A: start_date = st.date_input("Start", datetime.date(2023, 1, 1))
        with col_B: end_date = st.date_input("End", datetime.date.today())
        fetch_data = st.button("Initialize Pipeline", use_container_width=True, type="primary")
    elif source_type == "Simulated":
        ticker = st.text_input("Simulation Symbol", value="SIM_CO").upper()
        col_A, col_B = st.columns(2)
        with col_A: start_date = st.date_input("Start", datetime.date(2023, 1, 1))
        with col_B: end_date = st.date_input("End", datetime.date.today())
        fetch_data = st.button("Generate Simulated Data", use_container_width=True, type="primary")
    else:
        uploaded_file = st.file_uploader("Upload Market Data (CSV)", type=["csv"])
        fetch_data = uploaded_file is not None

    st.markdown("---")
    st.subheader("Strategy Config")
    pvi_p = st.slider("PVI Lookback", 5, 100, 20)
    rsi_p = st.slider("RSI Lookback", 5, 100, 14)
    capital = st.number_input("Starting Capital ($)", min_value=1000, value=10000, step=1000)

    if not HAS_PANDAS_TA:
        st.warning("⚠️ Using built-in indicator engine (pandas_ta not found).")

# ==========================================
# MAIN INTERFACE
# ==========================================
st.markdown("<h1 style='color: #F8FAFC;'>System Intelligence Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #F8FAFC;'>Advanced RSI & PVI Convergence Strategy Engine</p>", unsafe_allow_html=True)

df_raw = None
if source_type == "Market":
    df_raw = load_market_data(ticker, start_date, end_date)
elif source_type == "Simulated":
    df_raw = generate_simulated_data(ticker, start_date, end_date)
elif source_type == "Upload" and uploaded_file:
    df_raw = pd.read_csv(uploaded_file, index_col=0, parse_dates=True)

if df_raw is not None:
    try:
        # Process Strategy
        df_proc, close_c = apply_strategy(df_raw, pvi_len=pvi_p, rsi_len=rsi_p)
        equity_curve, trades = run_backtest(df_proc, capital, close_c)
        
        # Summary Metrics
        total_ret = ((equity_curve['Equity'].iloc[-1] - capital) / capital) * 100
        net_profit = equity_curve['Equity'].iloc[-1] - capital
        
        # UI Metrics Layout
        c1, c2, c3, c4 = st.columns(4)
        
        def render_metric(col, label, value, is_profit=None):
            val_class = "profit-positive" if is_profit == True else ("profit-negative" if is_profit == False else "")
            col.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value {val_class}">{value}</div>
            </div>
            """, unsafe_allow_html=True)

        render_metric(c1, "Net Portfolio P/L", f"${net_profit:,.2f}", net_profit >= 0)
        render_metric(c2, "Total Return %", f"{total_ret:+.2f}%", total_ret >= 0)
        render_metric(c3, "Total Trades", f"{len(trades)}")
        render_metric(c4, "Final Valuation", f"${equity_curve['Equity'].iloc[-1]:,.2f}")

        # Primary Visualization
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                            row_heights=[0.5, 0.25, 0.25])
        
        # Price & Signals
        fig.add_trace(go.Scatter(x=df_proc.index, y=df_proc[close_c], name="Price", line=dict(color='#3B82F6', width=1.5)), row=1, col=1)
        
        # Add Buy/Sell Markers
        if not trades.empty:
            buys = trades[trades['Type'] == 'BUY']
            sells = trades[trades['Type'] == 'SELL']
            fig.add_trace(go.Scatter(x=buys['Date'], y=buys['Price'], mode='markers', marker=dict(symbol='triangle-up', size=10, color='#10B981'), name='Entry'), row=1, col=1)
            fig.add_trace(go.Scatter(x=sells['Date'], y=sells['Price'], mode='markers', marker=dict(symbol='triangle-down', size=10, color='#EF4444'), name='Exit'), row=1, col=1)

        # RSI
        fig.add_trace(go.Scatter(x=df_proc.index, y=df_proc['RSI'], name="RSI", line=dict(color='#8B5CF6', width=1)), row=2, col=1)
        fig.add_hline(y=50, line_dash="dash", line_color="#475569", row=2, col=1)
        
        # PVI
        fig.add_trace(go.Scatter(x=df_proc.index, y=df_proc['PVI'], name="PVI", line=dict(color='#F59E0B', width=1)), row=3, col=1)

        fig.update_layout(height=800, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig, use_container_width=True)

        # Lower Panels
        t1, t2, t3 = st.tabs(["📊 Performance Equity", "📜 Execution Log", "🔍 Data Inspector"])
        
        with t1:
            eq_fig = go.Figure()
            eq_fig.add_trace(go.Scatter(x=equity_curve.index, y=equity_curve['Equity'], fill='tozeroy', line=dict(color='#10B981', width=2), name="Equity"))
            eq_fig.update_layout(height=400, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', title="Equity Growth Curve")
            st.plotly_chart(eq_fig, use_container_width=True)
            
        with t2:
            if not trades.empty:
                st.dataframe(trades, use_container_width=True)
            else:
                st.info("No trades executed with current parameters.")
                
        with t3:
            st.dataframe(df_proc.tail(100), use_container_width=True)

    except Exception as e:
        st.error(f"Execution Error: {str(e)}")
        with st.expander("Debug Details"):
            st.code(traceback.format_exc())
else:
    st.info("👋 Welcome! Please configure the sidebar settings and select a ticker to begin analysis.")
    st.image("https://images.unsplash.com/photo-1611974717484-7da00ff7345c?auto=format&fit=crop&q=80&w=2070", use_container_width=True)