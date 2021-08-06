import ccxt

if __name__ == '__main__':
    binance_exchange = ccxt.binance({
        'timeout': 15000,
        'enableRateLimit': True,
        'proxies': {'https': "http://127.0.0.1:7890", 'http': "http://127.0.0.1:7890"}
    })

    symbol = 'BTC/USDT'

    print('交易所当前时间：', binance_exchange.iso8601(binance_exchange.milliseconds()))
    # print(binance_exchange.load_markets())
    ticker_data = binance_exchange.fetchTicker(symbol)
    print(ticker_data)
    print('Ticker时刻：', binance_exchange.iso8601(ticker_data['datetime']))
    print('Ticker价格：', ticker_data['last'])

    if binance_exchange.has['fetchOHLCV']:
        print(binance_exchange.fetch_ohlcv(symbol, timeframe='1d'))

