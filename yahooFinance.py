import pandas as pd
import mplfinance as mpf
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
 
GetInformation = yf.Ticker("TSLA")
end_date = datetime.today().strftime('%Y-%m-%d')
 
# Download data from Yahoo Finance
df = yf.download('TSLA', start='2024-12-01', end=end_date)
# Flatten the multi-level columns
df.columns = df.columns.droplevel(1)


# Create a candlestick chart with volume
mpf.plot(df, type='candle', volume=True)



# Create the candlestick chart
fig = go.Figure(data=[go.Candlestick(
    x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close']
)])

fig.update_layout(title="TSLA Candlestick Chart", xaxis_rangeslider_visible=False)
fig.show()
