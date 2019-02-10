import ccxt
import pandas as pd
import time
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
pd.set_option("display.max_rows", 500)
import os

# 创建okex交易所
exchange = ccxt.okex()
exchange.load_markets()

# 获取交易所品种
df = pd.DataFrame(exchange.markets).T

# 找到有期货的交易所
df = df[df['future']]
future_symbol_list = list(df.index)

while True:
    print('*' * 10)
    # 遍历获取tick数据
    for future_symbol in future_symbol_list:
        if future_symbol not in ['EOS/USD', 'BCH/USD']:
            continue

        print(future_symbol)
        symbol = future_symbol.replace('USD', 'USDT')

        # 获取现货数据
        content = exchange.fetchTicker(symbol)
        del content['info']
        df = pd.DataFrame([content])[['timestamp', 'datetime', 'bid', 'ask']]

        # 获取期货数据
        # for contract_type in ['this_week', 'next_week', 'quarter']:
        for contract_type in ['quarter']:
            content = exchange.fetchTicker(future_symbol, {'contract_type': contract_type})
            temp = pd.DataFrame([content])[['timestamp', 'datetime', 'bid', 'ask']]
            # 合并数据
            df = pd.merge(left=df, right=temp, left_index=True, right_index=True, suffixes=['', '_' + contract_type])

            df['revenue_'+contract_type] = df['bid_'+contract_type] / df['ask'] - 1

        # 整理数据
        df['symbol'] = future_symbol
        df = df[['symbol'] + sorted(df.columns)]

        print(df)
        time.sleep(exchange.rateLimit / 1000)

    time.sleep(120)
