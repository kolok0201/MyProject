# 📈 專業量化選股掃描器與回測框架

這是一個從零到一，使用 Python 打造的「多重指標」量化選股系統。

本專案不僅是一個「訊號掃描器」，更包含一個「事件驅動」的回測引擎，能讓您系統性地開發、測試並優化您的交易策略。

##  專案特色 (Features)

* ** 多重指標策略**：採用嚴謹的 5 因子過濾模型，結合趨勢、動能與量能，非單純的均線交叉。
* ** 互動式 Web App**：使用 `Streamlit` 打造，介面直觀，點擊按鈕即可掃描訊號。
* ** 專業視覺化**：使用 `Plotly` 繪製「價、量、KD」三合一的互動式圖表，並自動標記停損線。
* ** 專業回測引擎**：
    * **事件驅動 (Event-Driven)**：精確模擬「每日檢查」停損單的真實交易行為。
    * **包含交易成本**：回測績效已扣除台股手續費 (0.1425%) 與證交稅 (0.3%)，更接近真實。
    * **動態停損**：採用「N 日低點」作為出場風控，而非簡易的死亡交叉停利。
* ** 參數優化**：內建 `optimize.py` 腳本，可自動化測試不同參數組合（如成交量倍數、KD 邊界）的歷史績效。

##  本專案使用的技術 (Technology Stack)

* **Python 3.10+**
* **Pandas**: 核心數據處理與分析。
* **yfinance**: 下載 Yahoo! Finance 股票數據。
* **Streamlit**: 建立互動式 Web App 介面。
* **Plotly**: 繪製專業的互動式圖表。
* **Numpy**: 輔助
    
    
    數值計算。

## 專案檔案結構

本系統由 4 個核心 Python 檔案組成：

* `download_all_data.py`:
    * **數據下載器 (原料採集)**
    * 負責從 `yfinance` 批次下載股票池的 K 線數據。
    * 預先計算所有必要指標 (MA, MA_Volume, KD, Stop-Loss Level) 並儲存為 CSV 檔。
* `app.py`:
    * **訊號掃描器 App (今日戰情室)**
    * `Streamlit` 主程式。
    * 讀取本地 CSV 檔，掃描「今天」符合所有策略條件的股票。
    * 提供視覺化介面與互動式圖表。
* `backtest.py`:
    * **策略回測器 (歷史分析)**
    * 被封裝成一個 `perform_backtest` 函式。
    * 執行一個完整的「事件驅動」回測，包含成本與停損。
    * 可被 `optimize.py` 呼叫。
* `optimize.py`:
    * **參數優化器 (策略研發)**
    * 定義要測試的參數範圍（例如成交量倍數、KD 邊界）。
    * 自動化迴圈呼叫 `backtest.py` 來測試所有參數組合，並印出績效排行榜。

##  安裝與執行 (Installation & Usage)

### 1. 安裝需求

1.  複製本專案：
    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_PROJECT_NAME.git](https://github.com/YOUR_USERNAME/YOUR_PROJECT_NAME.git)
    cd YOUR_PROJECT_NAME
    ```
2.  (建議) 建立虛擬環境：
    ```bash
    python -m venv venv
    source venv/bin/activate  # macOS/Linux
    .\venv\Scripts\activate   # Windows
    ```
3.  安裝所需的套件 (您可以將以下內容存為 `requirements.txt`):
    ```
    pandas
    yfinance
    streamlit
    plotly
    numpy
    ```
    然後執行：
    ```bash
    pip install -r requirements.txt
    ```

### 2. 如何使用 (Operational Steps)

#### 步驟一：更新數據 (每日收盤後)

首先，執行「數據下載器」來獲取最新的 K 線並預先計算指標。

```bash
python download_all_data.py
這會為您的股票池中（預設 5 檔）的每檔股票，在資料夾中生成一個 ..._data_with_MA.csv 檔案。

步驟二：啟動「訊號掃描器」App
執行 Streamlit App。

Bash

streamlit run app.py
您的瀏覽器將自動開啟 http://localhost:8501。點擊「🚀 開始掃描」按鈕，即可看到「今天」的訊號。

步驟三：(研發用) 執行「策略優化」
如果您想測試策略參數（例如 2330.TW 在不同參數下的表現）：

Bash

python optimize.py
程式將在終端機中運行，並在最後印出所有參數組合的「績效排行榜」。

 本專案採用的「專業版」策略
本 App 掃描的「 高品質專業訊號」，定義為「今天」的數據必須「同時」滿足以下 5 個條件：

短期趨勢 (黃金交叉)：MA5 > MA20 (且昨日 MA5 < MA20)

量能確認 (帶量)：今日成交量 > 1.5 倍 MA5_Volume

長期趨勢 (過濾器)：今日收盤價 > MA60 (季線)

動能確認 (過濾器)：K值 > D值 (動能向上) 且 K值 < 80 (未超買)

(隱含條件)：訊號觸發，並計算「5日低點」作為建議停損。

重要提醒 (Disclaimer)
本專案所有內容僅供教育與學術研究目的。

所有程式碼、策略、回測結果均不構成任何實際的投資買賣建議。

股票市場存在固有風險，過去的回測績效不代表未來的實際表現。

請勿在未經充分驗證（包含樣本外測試）前，將此策略用於真實金錢交易。
