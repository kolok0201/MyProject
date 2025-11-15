import pandas as pd
import numpy as np

# --- 1. 策略參數 (現在變成了「預設值」) ---
STOCK_ID_DEFAULT = '2330.TW'
FEE_RATE = 0.001425
TAX_RATE = 0.003
STOP_LOSS_COL = "Stop_Loss_5D_Low"
STOP_LOSS_DAYS_N = 5

# --- 2. (核心) 將所有邏輯封裝成一個函式 ---
def perform_backtest(stock_id=STOCK_ID_DEFAULT, 
                     volume_factor=1.5, 
                     kd_upper_bound=80):
    """
    執行專業版回測的函式
    Args:
        stock_id (str): 股票代號
        volume_factor (float): 成交量暴增倍數 (可優化的參數)
        kd_upper_bound (int): KD 超買界線 (可優化的參數)
        
    Returns:
        dict: 包含所有績效指標的字典
    """
    
    input_file = f"{stock_id}_data_with_MA.csv"
    
    # --- 2a. 讀取數據 ---
    try:
        data = pd.read_csv(input_file, index_col="Date", parse_dates=True)
        if 'K' not in data.columns or STOP_LOSS_COL not in data.columns:
            return {"error": f"數據檔 {input_file} 不完整"}
    except FileNotFoundError:
        return {"error": f"找不到數據檔 {input_file}"}

    # --- 2b. 產生訊號 (使用傳入的參數) ---
    buy_cond_1 = (data['MA5'] > data['MA20'])
    buy_cond_2 = (data['MA5'].shift(1) < data['MA20'].shift(1))
    # (優化點) 使用傳入的 volume_factor
    buy_cond_3 = (data['Volume'] > (data['MA5_Volume'] * volume_factor)) 
    buy_cond_4 = (data['Close'] > data['MA60'])
    # (優化點) 使用傳入的 kd_upper_bound
    buy_cond_5 = (data['K'] > data['D']) & (data['K'] < kd_upper_bound) 
    
    data['Buy_Signal'] = (buy_cond_1 & buy_cond_2 & buy_cond_3 & buy_cond_4 & buy_cond_5)
    
    sell_cond_1 = (data['MA5'] < data['MA20'])
    sell_cond_2 = (data['MA5'].shift(1) > data['MA20'].shift(1))
    data['Sell_Signal_DeathCross'] = (sell_cond_1 & sell_cond_2)

    # --- 2c. 事件驅動迴圈 ---
    in_position = False
    entry_price_raw = 0.0
    entry_price_with_cost = 0.0
    current_stop_loss_price = 0.0
    entry_date = None
    trades = []

    for i in range(STOP_LOSS_DAYS_N, len(data)):
        today = data.iloc[i]
        yesterday = data.iloc[i-1]
        
        if in_position:
            exit_price_raw = 0.0
            exit_reason = None
            if today['Low'] <= current_stop_loss_price:
                exit_price_raw = current_stop_loss_price
                exit_reason = "Stop-Loss"
            elif yesterday['Sell_Signal_DeathCross']:
                exit_price_raw = today['Open']
                exit_reason = "Death Cross"
            
            if exit_reason:
                exit_price_net = exit_price_raw * (1 - FEE_RATE - TAX_RATE)
                profit = exit_price_net - entry_price_with_cost
                trades.append((entry_date, entry_price_raw, today.name, exit_price_raw, profit, exit_reason))
                in_position = False
                
        if not in_position:
            if yesterday['Buy_Signal']:
                entry_price_raw = today['Open']
                entry_price_with_cost = entry_price_raw * (1 + FEE_RATE)
                current_stop_loss_price = yesterday[STOP_LOSS_COL]
                
                if entry_price_raw >= current_stop_loss_price:
                    in_position = True
                    entry_date = today.name
                    
    if in_position:
        last_day = data.iloc[-1]
        exit_price_raw = last_day['Close']
        exit_price_net = exit_price_raw * (1 - FEE_RATE - TAX_RATE)
        profit = exit_price_net - entry_price_with_cost
        trades.append((entry_date, entry_price_raw, last_day.name, exit_price_raw, profit, "End of Test"))

    # --- 2d. 結算績效 ---
    if not trades:
        return {
            "stock_id": stock_id, "volume_factor": volume_factor, "kd_bound": kd_upper_bound,
            "total_trades": 0, "total_profit": 0, "win_rate": 0, "profit_factor": 0,
            "error": "No trades generated"
        }

    trade_df = pd.DataFrame(trades, columns=["進場日", "進場價", "出場日", "出場價", "淨損益(元)", "出場原因"])
    
    total_trades = len(trade_df)
    total_profit = trade_df['淨損益(元)'].sum()
    
    win_trades = trade_df[trade_df['淨損益(元)'] > 0]
    loss_trades = trade_df[trade_df['淨損益(元)'] <= 0]
    
    win_rate = len(win_trades) / total_trades if total_trades > 0 else 0
    
    total_gross_profit = win_trades['淨損益(元)'].sum()
    total_gross_loss = abs(loss_trades['淨損益(元)'].sum())
    profit_factor = total_gross_profit / total_gross_loss if total_gross_loss > 0 else np.inf
    
    # 回傳一個包含所有績效的字典
    return {
        "stock_id": stock_id,
        "volume_factor": volume_factor,
        "kd_bound": kd_upper_bound,
        "total_trades": total_trades,
        "total_profit": round(total_profit, 2),
        "win_rate": round(win_rate, 4),
        "profit_factor": round(profit_factor, 2)
    }

# --- 3. (核心) 讓這個檔案可以被「單獨執行」 ---
# 只有在「直接執行 python backtest.py」時，這段程式碼才會運行
# 如果是「被 optimize.py 導入 (import)」，這段不會運行
if __name__ == "__main__":
    
    print("--- 正在以「單獨執行」模式運行 backtest.py ---")
    
    # 呼叫函式，使用預設參數
    results = perform_backtest(stock_id=STOCK_ID_DEFAULT, 
                               volume_factor=1.5, 
                               kd_upper_bound=80)
    
    # 漂亮地印出結果
    if "error" in results:
        print(f"錯誤: {results['error']}")
    else:
        print("\n--- 績效報告 (單次執行) ---")
        for key, value in results.items():
            print(f"  {key}: {value}")
