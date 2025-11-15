import pandas as pd
from backtest import perform_backtest # <-- (核心) 從 backtest.py 導入我們剛才寫的函式
import time

# --- 1. 定義要優化的參數範圍 ---
# 我們將測試 成交量倍數 vs KD超買線
# (注意：範圍越大，跑得越久)

# 成交量倍數：[1.5, 2.0, 2.5] (3 種)
param_volume_factors = [1.5, 2.0, 2.5]

# KD 超買界線：[70, 80, 90] (3 種)
param_kd_bounds = [70, 80, 90]

# 總共要跑的組合數 = 3 * 3 = 9 次回測
total_combinations = len(param_volume_factors) * len(param_kd_bounds)

print(f"--- 啟動「參數優化器」 ---")
print(f"--- 總共要測試 {total_combinations} 種參數組合... ---")

# --- 2. 準備一個列表，用來存放所有結果 ---
all_results = []
start_time = time.time() # 計時

# --- 3. (核心) 巢狀迴圈，測試所有組合 ---

for vol_factor in param_volume_factors:
    for kd_bound in param_kd_bounds:
        
        print(f"  正在測試: Volume Factor = {vol_factor}, KD Bound = {kd_bound} ...")
        
        # 呼叫 backtest 函式，並傳入參數
        result = perform_backtest(stock_id='2330.TW', 
                                  volume_factor=vol_factor, 
                                  kd_upper_bound=kd_bound)
        
        # 將結果存入列表
        all_results.append(result)

end_time = time.time()
print(f"\n--- 優化完畢！總耗時: {end_time - start_time:.2f} 秒 ---")

# --- 4. 顯示績效排行榜 ---

if not all_results:
    print("錯誤：沒有產生任何回測結果。")
else:
    # 將結果列表轉換為 Pandas DataFrame，方便排序和顯示
    results_df = pd.DataFrame(all_results)
    
    # (可選) 處理沒有交易的結果
    results_df = results_df.dropna() # 移除有 "error" 的行
    results_df = results_df[results_df['total_trades'] > 0] # 只看有交易的

    if results_df.empty:
        print("所有參數組合均未產生有效交易。")
    else:
        # --- (核心) 根據「獲利因子 (Profit Factor)」降冪排序 ---
        sorted_results = results_df.sort_values(by="profit_factor", ascending=False)
        
        print("\n--- 績效排行榜 (依「獲利因子」排序) ---")
        print(sorted_results)

        # 顯示最佳參數
        best_params = sorted_results.iloc[0]
        print("\n--- 🏆 最佳參數組合 🏆 ---")
        print(f"  Volume Factor: {best_params['volume_factor']}")
        print(f"  KD Bound: {best_params['kd_bound']}")
        print(f"  Profit Factor: {best_params['profit_factor']}")
        print(f"  Total Trades: {best_params['total_trades']}")
        print(f"  Total Profit: {best_params['total_profit']}")
