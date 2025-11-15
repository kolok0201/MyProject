import pandas as pd
import glob # 匯入 glob 模組，用於「自動搜尋檔案」
import os   # 匯入 os 模組，用於處理檔案路徑

# --- 1. 設定均線名稱 (必須與 download_all_data.py 一致) ---
short_ma_col = "MA5"
long_ma_col = "MA20"

# --- 2. 自動搜尋所有符合條件的 CSV 檔案 ---
# glob.glob 會找出所有符合 '..._data_with_MA.csv' 格式的檔案
# 這比我們手動維護 stock_list 更聰明、更自動化！
file_pattern = "*_data_with_MA.csv"
all_csv_files = glob.glob(file_pattern)

if not all_csv_files:
    print(f"錯誤：在目前資料夾中找不到任何 {file_pattern} 檔案。")
    print("請先執行 download_all_data.py 來產生數據檔。")
    exit()

print(f"--- 1. 發現 {len(all_csv_files)} 個股票數據檔案，開始掃描 ---")

# --- 3. 準備一個列表，用來存放觸發訊號的股票 ---
signal_stocks = []

# --- 4. 迴圈遍歷所有檔案 ---
for file_path in all_csv_files:
    
    # 從檔案路徑中，萃取出股票代號 (例如 "2330.TW")
    # os.path.basename(file_path) 會得到 "2330.TW_data_with_MA.csv"
    # .split('_')[0] 會以 "_" 切割，並取第 [0] 個元素
    stock_id = os.path.basename(file_path).split('_')[0]

    try:
        # --- 4a. 讀取 CSV 檔案 ---
        data = pd.read_csv(file_path, index_col="Date", parse_dates=True)
        
        # 檢查資料筆數是否足夠 (至少要有2筆才能比較 "今天" 和 "昨天")
        if len(data) < 2:
            print(f"  [{stock_id}] 數據不足 (<2筆)，跳過...")
            continue # 繼續下一個迴圈

        # --- 4b. 核心！只取最後兩筆資料 ---
        # .iloc[-1] 代表選取「最後一列」 (今天)
        # .iloc[-2] 代表選取「倒數第二列」 (昨天)
        last_row = data.iloc[-1]
        yesterday_row = data.iloc[-2]

        # --- 4c. 檢查黃金交叉邏輯 ---
        # 條件1: 昨天，短均線在長均線之下
        condition1 = (yesterday_row[short_ma_col] < yesterday_row[long_ma_col])
        
        # 條件2: 今天，短均線在長均線之上
        condition2 = (last_row[short_ma_col] > last_row[long_ma_col])

        # --- 4d. 判斷訊號 ---
        if condition1 and condition2:
            print(f"  *** 訊號觸發! *** -> {stock_id}")
            signal_stocks.append(stock_id)
        else:
            # (可選) 印出未觸發的股票，方便除錯
            # print(f"  [{stock_id}] 未觸發訊號。")
            pass

    except Exception as e:
        print(f"處理 {stock_id} (檔案: {file_path}) 時發生錯誤: {e}")

# --- 5. 總結報告 ---
print("\n--- 掃描完畢 ---")
if not signal_stocks:
    print("今日 (最新資料日) 沒有任何股票觸發「黃金交叉」訊號。")
else:
    print(f"恭喜！今日 (最新資料日) 共 {len(signal_stocks)} 檔股票觸發訊號：")
    for stock in signal_stocks:
        print(f"  - {stock}")
