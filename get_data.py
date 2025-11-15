import yfinance as yf
import pandas as pd
import time

# --- 1. 股票池 (範例) ---
stock_list = ['2330.TW', '2317.TW', '2454.TW', '2881.TW', '1301.TW']

# --- 2. 均線設定 ---
ma_short = 5
ma_long = 20
ma_trend = 60    
vol_ma = 5
kd_period = 9
stop_loss_days = 5 # <-- (新增) 停損的天期

print(f"--- 開始批次下載 {len(stock_list)} 檔股票數據 (包含停損點) ---")

for stock_id in stock_list:
    print(f"\n--- 正在處理: {stock_id} ---")
    try:
        stock = yf.Ticker(stock_id)
        data = stock.history(period="2y", interval="1d")

        if data.empty:
            print(f"無法獲取 {stock_id} 的數據，跳過...")
            continue

        # --- 3. 計算價格均線 ---
        data[f'MA{ma_short}'] = data['Close'].rolling(window=ma_short).mean()
        data[f'MA{ma_long}'] = data['Close'].rolling(window=ma_long).mean()
        data[f'MA{ma_trend}'] = data['Close'].rolling(window=ma_trend).mean()
        
        # --- 4. 計算成交量均線 ---
        data[f'MA{vol_ma}_Volume'] = data['Volume'].shift(1).rolling(window=vol_ma).mean()
        
        # --- 5. 計算 KD 指標 ---
        low_min = data['Low'].rolling(window=kd_period).min()
        high_max = data['High'].rolling(window=kd_period).max()
        data['RSV'] = (data['Close'] - low_min) / (high_max - low_min) * 100
        data['K'] = data['RSV'].ewm(com=2, adjust=False).mean()
        data['D'] = data['K'].ewm(com=2, adjust=False).mean()
        
        # --- 6. (全新) 計算「每日」的停損水平 ---
        # 停損點 = 「今天(含)往前 N 天」的最低價
        data[f'Stop_Loss_{stop_loss_days}D_Low'] = data['Low'].rolling(window=stop_loss_days).min()

        # --- 7. 儲存檔案 ---
        output_filename = f"{stock_id}_data_with_MA.csv"
        data.dropna().to_csv(output_filename)
        
        print(f"成功儲存至 {output_filename} (已包含MA60, KD, 5D_Low)")

        time.sleep(1) 
    except Exception as e:
        print(f"處理 {stock_id} 時發生錯誤: {e}")

print("\n--- 所有股票數據下載處理完畢 ---")
