from polygon import RESTClient
import streamlit as st
from urllib3 import HTTPResponse
from typing import cast
import json
from plotly import graph_objects as go
import pandas as pd
import talib
import numpy as np

st.title("Welcome to Stockishly - Stock Lookup Tool!")

# Take in User's API Key
API_KEY = st.text_input("Enter Your API Key: ")

# Take in Stock Ticker - if they haven't input anything show an error message!
stock_ticker = st.text_input("Enter a Valid Stock Ticker on NYSE or NASDAQ: ")

# Create checkboxes for all the technical indicators
st.subheader("Technical Indicators:")

bbands_check = st.checkbox("Bollinger Bands")
sma_check = st.checkbox("SMA")
rsi_check = st.checkbox("RSI")
wma_check = st.checkbox("Weighted Moving Average")

# Submit Button
submit_button = st.button("Submit")

aggs = []
data = []

# Runs when submit button is clicked
if submit_button:
    # Call Polygon API
    client = RESTClient(api_key=API_KEY)

    # Get basic stock info
    data = client.get_ticker_details(stock_ticker)

    # Display Basic Stock Information
    st.write("Ticker:", data.ticker)
    st.write("Name:", data.name)
    st.write("About:", data.description)
    st.write("Traded Currency:", data.currency_name.upper())
    st.write("Weighted Shares Outstanding:", data.weighted_shares_outstanding)

    # Receiving last two year of stock information
    aggs = cast(
    HTTPResponse,
    client.get_aggs(
        stock_ticker,
        1,
        'day',
        '2024-01-01',
        '2025-06-30',
        raw=True
        ),
    )

    # Convert data received into JSON format
    aggs_data = json.loads(aggs.data)

    closeList = []
    openList = []
    highList = []
    lowList = []
    timeList = []

    # Extract raw data from API
    for item in aggs_data:
        if item == "results":
            rawData = aggs_data[item]
    
    # Extract opening, closing, high and low price/day
    for data in rawData:
        for category in data:
            if category == "c":
                closeList.append(data[category])
            elif category == "h":
                highList.append(data[category])
            elif category == "o":
                openList.append(data[category])
            elif category == "l":
                lowList.append(data[category])
            elif category == "t":
                timeList.append(data[category])

    # Get time values from API call and covert to GMT
    times = []
    for time in timeList:
        times.append(pd.Timestamp(time, tz="GMT", unit="ms"))

    # Getting technical analysis data from TA-Lib
    upper, middle, lower = talib.BBANDS(np.array(closeList), timeperiod=20)
    sma = talib.SMA(np.array(closeList))
    rsi = talib.RSI(np.array(closeList))
    wma = talib.WMA(np.array(closeList))
    
    # Drawing using Plotly
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=times, open=openList, close=closeList, high=highList, low=lowList, name=stock_ticker + "Price Data"))
    if bbands_check:
        fig.add_trace(go.Scatter(x=times, y=sma, line=dict(color='red'), name="SMA"))
    if rsi_check:  
        fig.add_trace(go.Scatter(x=times, y=rsi, line=dict(color='yellow'), name="RSI"))
    if wma_check:
        fig.add_trace(go.Scatter(x=times, y=wma, line=dict(color='blue'), name="WMA"))
    fig.update_layout(xaxis_rangeslider_visible=False)

    st.plotly_chart(fig)