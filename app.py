import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="Stock Alert Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .alert-positive { background-color: #10b981; color: white; padding: 0.5rem; border-radius: 5px; }
    .alert-negative { background-color: #ef4444; color: white; padding: 0.5rem; border-radius: 5px; }
    .header-style {
        background: linear-gradient(90deg, #667eea, #764ba2);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Cache functions to prevent API rate limits
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_data(symbol):
    """Fetch stock data with caching"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d", interval="1d")
        info = ticker.info
        
        current_price = hist['Close'].iloc[-1] if len(hist) > 0 else 0
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100 if prev_close != 0 else 0
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'change': change,
            'change_pct': change_pct,
            'volume': hist['Volume'].iloc[-1] if len(hist) > 0 else 0,
            'history': hist,
            'company_name': info.get('longName', symbol)
        }
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return None

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_market_indices():
    """Get major market indices"""
    indices = ['^GSPC', '^DJI', '^IXIC']  # S&P 500, Dow Jones, NASDAQ
    market_data = []
    
    for index in indices:
        data = get_stock_data(index)
        if data:
            market_data.append(data)
    
    return market_data

def create_price_chart(stock_data):
    """Create interactive price chart"""
    if stock_data and len(stock_data['history']) > 0:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=stock_data['history'].index,
            y=stock_data['history']['Close'],
            mode='lines+markers',
            name=f"{stock_
