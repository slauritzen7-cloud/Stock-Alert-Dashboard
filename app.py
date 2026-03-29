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
    .alert-positive { 
        background-color: #10b981; 
        color: white; 
        padding: 0.5rem; 
        border-radius: 5px; 
        margin: 0.5rem 0;
    }
    .alert-negative { 
        background-color: #ef4444; 
        color: white; 
        padding: 0.5rem; 
        border-radius: 5px; 
        margin: 0.5rem 0;
    }
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

# Initialize session state
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['RKLB', 'GME', 'SOFI', 'NVDA']
if 'alerts' not in st.session_state:
    st.session_state.alerts = []

# Cache functions to prevent API rate limits
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_data(symbol):
    """Fetch stock data with caching"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d", interval="1d")
        info = ticker.info
        
        if len(hist) == 0:
            return None
            
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100 if prev_close != 0 else 0
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'change': change,
            'change_pct': change_pct,
            'volume': hist['Volume'].iloc[-1],
            'history': hist,
            'company_name': info.get('longName', symbol)
        }
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return None

def create_price_chart(stock_data):
    """Create interactive price chart"""
    if stock_data and len(stock_data['history']) > 0:
        fig = go.Figure()
        
        # Add price line
        fig.add_trace(go.Scatter(
            x=stock_data['history'].index,
            y=stock_data['history']['Close'],
            mode='lines+markers',
            name=f"{stock_data['symbol']} Price",
            line=dict(color='#667eea', width=3),
            marker=dict(size=6)
        ))
        
        # Update layout
        fig.update_layout(
            title=f"{stock_data['symbol']} - {stock_data['company_name

