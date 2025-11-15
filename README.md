# 📈 專業量化選股掃描器與回測框架

這是一個從零到一，使用 Python 打造的「多重指標」量化選股系統。

本專案不僅是一個「訊號掃描器」，更包含一個「事件驅動」的回測引擎，能讓您系統性地開發、測試並優化您的交易策略。

## 💡 專案特色 (Features)

* **📈 多重指標策略**：採用嚴謹的 5 因子過濾模型，結合趨勢、動能與量能，非單純的均線交叉。
* **🌐 互動式 Web App**：使用 `Streamlit` 打造，介面直觀，點擊按鈕即可掃描訊號。
* **📊 專業視覺化**：使用 `Plotly` 繪製「價、量、KD」三合一的互動式圖表，並自動標記停損線。
* **🚀 專業回測引擎**：
    * **事件驅動 (Event-Driven)**：精確模擬「每日檢查」停損單的真實交易行為。
    * **包含交易成本**：回測績效已扣除台股手續費 (0.1425%) 與證交稅 (0.3%)，更接近真實。
    * **動態停損**：採用「N 日低點」作為出場風控，而非簡易的死亡交叉停利。
* **⚙️ 參數優化**：內建 `optimize.py` 腳本，可自動化測試不同參數組合（如成交量倍數、KD 邊界）的歷史績效。

## 📸 App 介面截圖


*（請在此貼上您的 app.py 運行截圖）*


*（請在此貼上您的 Plotly 圖表截圖）*

## 🛠️ 本專案使用的技術 (Technology Stack)

* **Python 3.10+**
* **Pandas**: 核心數據處理與分析。
* **yfinance**: 下載 Yahoo! Finance 股票數據。
* **Streamlit**: 建立互動式 Web App 介面。
* **Plotly**: 繪製專業的互動式圖表。
* **Numpy**: 輔助
    
    
    數值計算。

## 🗂️ 專案檔案結構

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

## 🚀 安裝與執行 (Installation & Usage)

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
