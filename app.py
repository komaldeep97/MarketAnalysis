from flask import Flask, render_template, request, jsonify
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

app = Flask(__name__)
import numpy as np

def calculate_trendline(data):
    x = np.arange(len(data))
    y = data['Close'].values
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    return x, p(x)

def calculate_channel_lines(data, trendline):
    differences = data['Close'].values - trendline
    upper_channel = trendline + np.max(differences)
    lower_channel = trendline + np.min(differences)
    return upper_channel, lower_channel


def create_stock_chart(ticker, show_ma20=False, show_ma50=False):
    try:
        data = yf.download(ticker, period="1y")
        data.columns = data.columns.droplevel(1)
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.03, subplot_titles=(f'{ticker} Stock Price', 'Volume'),
                            row_heights=[0.7, 0.3])
        
        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=data.index, open=data['Open'], high=data['High'],
            low=data['Low'], close=data['Close'], name='Price'),
            row=1, col=1
        )
        # Calculate and add trendline
        x, trendline = calculate_trendline(data)
        fig.add_trace(go.Scatter(x=data.index, y=trendline, name='Trendline', line=dict(color='purple', width=2)), row=1, col=1)
        
        # Calculate and add channel lines
        upper_channel, lower_channel = calculate_channel_lines(data, trendline)
        fig.add_trace(go.Scatter(x=data.index, y=upper_channel, name='Upper Channel', line=dict(color='green', width=1, dash='dash')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=lower_channel, name='Lower Channel', line=dict(color='red', width=1, dash='dash')), row=1, col=1)
        
        # Volume chart
        fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name='Volume'), row=2, col=1)
        
        # Add moving averages if requested
        if show_ma20:
            data['MA20'] = data['Close'].rolling(window=20).mean()
            fig.add_trace(go.Scatter(x=data.index, y=data['MA20'], name='20-day MA', line=dict(color='orange')), row=1, col=1)
        
        if show_ma50:
            data['MA50'] = data['Close'].rolling(window=50).mean()
            fig.add_trace(go.Scatter(x=data.index, y=data['MA50'], name='50-day MA', line=dict(color='red')), row=1, col=1)
        
        fig.update_layout(height=600, width=800, title_text=f"{ticker} Stock Analysis")
        fig.update_xaxes(rangeslider_visible=False)
        
        return fig.to_html(full_html=False)
    except Exception as e:
        return str(e)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        charts = {}
        for i in range(1, 6):
            ticker = request.form.get(f'stock{i}')
            if ticker:
                chart = create_stock_chart(ticker)
                if not chart.startswith("Exception"):
                    charts[ticker] = chart
                else:
                    charts[ticker] = f"Error: {chart}"
        return render_template('index.html', charts=charts)
    return render_template('index.html')

@app.route('/update_chart', methods=['POST'])
def update_chart():
    ticker = request.form.get('ticker')
    show_ma20 = request.form.get('show_ma20') == 'true'
    show_ma50 = request.form.get('show_ma50') == 'true'
    
    chart = create_stock_chart(ticker, show_ma20, show_ma50)
    if not chart.startswith("Exception"):
        return jsonify({'success': True, 'chart': chart})
    else:
        return jsonify({'success': False, 'error': chart})

if __name__ == '__main__':
    app.run(debug=True)
