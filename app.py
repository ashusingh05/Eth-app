import pandas as pd
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Function to fetch historical data from Binance
def fetch_klines(symbol, interval, start_time, end_time):
    api_url = "https://api.binance.com/api/v3/klines"
    params = {
        'symbol': symbol,
        'interval': interval,
        'startTime': start_time,
        'endTime': end_time,
        'limit': 1000
    }
    response = requests.get(api_url, params=params)
    return response.json() if response.status_code == 200 else []

# Function to generate buy/sell signals based on SMA crossover
def generate_signals(data, short_window=9, long_window=21):
    data['SMA_Short'] = data['Close'].rolling(window=short_window).mean()
    data['SMA_Long'] = data['Close'].rolling(window=long_window).mean()

    # Generate signals
    data['Signal'] = 0
    data.loc[data['SMA_Short'] > data['SMA_Long'], 'Signal'] = 1  # Buy
    data.loc[data['SMA_Short'] < data['SMA_Long'], 'Signal'] = -1  # Sell

    return data

# Prepare data fetch
symbol = 'BTCUSDT'
interval = '1h'  # Hourly interval for more frequent signals
end_time = int(datetime.now().timestamp() * 1000)
start_time = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)  # 30 days of data

# Fetch data
klines = fetch_klines(symbol, interval, start_time, end_time)

# Process data into a DataFrame
data_list = []
for entry in klines:
    data_list.append({
        'Date': datetime.utcfromtimestamp(entry[0] / 1000),
        'Open': float(entry[1]),
        'High': float(entry[2]),
        'Low': float(entry[3]),
        'Close': float(entry[4]),
        'Volume': float(entry[5])
    })
data = pd.DataFrame(data_list)

# Generate buy/sell signals
data = generate_signals(data)

# Display recent signals
recent_signals = data[['Date', 'Close', 'Signal']].tail(10)
print(recent_signals)

# Plot the data and signals
plt.figure(figsize=(12, 6))
plt.plot(data['Date'], data['Close'], label='Close Price', color='blue', alpha=0.5)
plt.plot(data['Date'], data['SMA_Short'], label='Short SMA', color='green', alpha=0.7)
plt.plot(data['Date'], data['SMA_Long'], label='Long SMA', color='red', alpha=0.7)
buy_signals = data[data['Signal'] == 1]
sell_signals = data[data['Signal'] == -1]
plt.scatter(buy_signals['Date'], buy_signals['Close'], label='Buy Signal', color='green', marker='^', alpha=1)
plt.scatter(sell_signals['Date'], sell_signals['Close'], label='Sell Signal', color='red', marker='v', alpha=1)
plt.title(f"Buy/Sell Signals for {symbol}")
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.grid()
plt.show()
