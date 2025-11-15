import streamlit as st
import pandas as pd
import glob
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. 頁面基礎設定 ---
st.set_page_config(page_title="量化選股小幫手", layout="wide")
st.title('📈 專業版多重過濾掃描器 (趨勢+動能+量能)')
with st.expander("點此查看「專業版」策略定義"):
    st.markdown("""
    **一個高品質的「帶量黃金交叉」訊號，必須同時滿足以下所有條件：**
    1.  **短期趨勢**：MA5 > MA20 (昨日 MA5 < MA20)
    2.  **量能確認**：今日成交量 > 1.5 倍 MA5_Volume
    3.  **長期趨勢 (過濾器)**：今日收盤價 > MA60 (季線)
    4.  **動能確認 (過濾器)**：K值 > D值 (動能向上) 且 K值 < 80 (未超買)
    5.  **風險計算**：自動計算 5 日低點作為建議停損。
    """)

# --- 策略參數 ---
SHORT_MA_COL = "MA5"
LONG_MA_COL = "MA20"
TREND_MA_COL = "MA60"     # <-- (新增)
VOL_MA_COL = "MA5_Volume"
VOLUME_SPIKE_FACTOR = 1.5
STOP_LOSS_DAYS = 5 

# --- 2. 掃描函式 (終極升級) ---
def scan_all_stocks():
    file_pattern = "*_data_with_MA.csv"
    all_csv_files = glob.glob(file_pattern)

    if not all_csv_files:
        return None, None, "錯誤：在資料夾中找不到任何 *_data_with_MA.csv 檔案。\n請先執行 'download_all_data.py' (最新版本)。"

    signal_stocks_data = []
    all_stocks_data = []   
    all_stock_ids = []     

    for file_path in all_csv_files:
        stock_id = os.path.basename(file_path).split('_')[0]
        all_stock_ids.append(stock_id)
        
        try:
            data = pd.read_csv(file_path, index_col="Date", parse_dates=True)
            # 檢查 K, D, MA60 是否都存在
            if len(data) < 2 or 'K' not in data.columns or TREND_MA_COL not in data.columns:
                continue 

            last_row = data.iloc[-1]
            yesterday_row = data.iloc[-2]
            last_date = last_row.name.strftime('%Y-%m-%d')
            
            # --- (核心修改) 五大條件 ---
            condition1_price = (yesterday_row[SHORT_MA_COL] < yesterday_row[LONG_MA_COL])
            condition2_price = (last_row[SHORT_MA_COL] > last_row[LONG_MA_COL])
            condition3_volume = (last_row['Volume'] > (last_row[VOL_MA_COL] * VOLUME_SPIKE_FACTOR))
            condition4_trend = (last_row['Close'] > last_row[TREND_MA_COL]) # <-- (新增)
            condition5_momentum = (last_row['K'] > last_row['D']) and (last_row['K'] < 80) # <-- (新增)

            suggested_stop_loss = data.tail(STOP_LOSS_DAYS)['Low'].min()
            
            signal_status = "---"
            
            # 必須「同時」滿足所有條件
            if (condition1_price and condition2_price and condition3_volume and 
                condition4_trend and condition5_momentum):
                
                signal_status = "🔥 專業訊號 (全中)"
                signal_stocks_data.append({
                    "股票代號": stock_id, "訊號": signal_status,
                    "最新收盤價": last_row['Close'],
                    "建議停損價": round(suggested_stop_loss, 2),
                    "K值": round(last_row['K'], 1), # <-- (新增)
                    "D值": round(last_row['D'], 1), # <-- (新增)
                    "資料日期": last_date
                })
            # 幫您找出「差一點點」的訊號 (方便除錯)
            elif condition1_price and condition2_price and condition3_volume:
                 if not condition4_trend:
                     signal_status = "黃金交叉 (逆勢!)"
                 elif not condition5_momentum:
                     signal_status = "黃金交叉 (動能不足)"
                 else:
                     signal_status = "黃金交叉 (帶量)"
            
            all_stocks_data.append({
                "股票代號": stock_id, "訊號": signal_status, "最新收盤價": last_row['Close'],
                "建議停損價": round(suggested_stop_loss, 2), "K值": round(last_row['K'], 1),
                "MA60": round(last_row[TREND_MA_COL], 2)
            })
        except Exception as e:
            st.error(f"處理 {stock_id} 時發生錯誤: {e}")

    all_df = pd.DataFrame(all_stocks_data)
    signal_df = pd.DataFrame(signal_stocks_data)
    
    return all_df, signal_df, all_stock_ids

# --- 3. 繪圖函式 (終極升級 - 三圖表) ---
def create_stock_chart(stock_id):
    file_path = f"{stock_id}_data_with_MA.csv"
    try:
        data = pd.read_csv(file_path, index_col="Date", parse_dates=True)
        data_plot = data.tail(90) # 近3個月

        recent_5_day_low = data.tail(STOP_LOSS_DAYS)['Low'].min()

        # --- (核心修改) 建立「三張子圖表」 ---
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.03, 
                           row_heights=[0.6, 0.2, 0.2]) # K線圖(60%) + 成交量(20%) + KD(20%)

        # --- 3a. K線 + 均線 (Row 1) ---
        fig.add_trace(go.Candlestick(x=data_plot.index,
                        open=data_plot['Open'], high=data_plot['High'],
                        low=data_plot['Low'], close=data_plot['Close'],
                        name='K線'), row=1, col=1)
        fig.add_trace(go.Scatter(x=data_plot.index, y=data_plot[SHORT_MA_COL],
                                mode='lines', name=SHORT_MA_COL,
                                line=dict(color='orange', width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=data_plot.index, y=data_plot[LONG_MA_COL],
                                mode='lines', name=LONG_MA_COL,
                                line=dict(color='blue', width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=data_plot.index, y=data_plot[TREND_MA_COL],
                                mode='lines', name=TREND_MA_COL, # <-- (新增)
                                line=dict(color='green', width=1, dash='dot')), row=1, col=1) # 綠色點狀線
        # 停損線
        fig.add_hline(y=recent_5_day_low, line_dash="dash", line_color="red",
                      annotation_text=f"建議停損點: {recent_5_day_low}", 
                      row=1, col=1)

        # --- 3b. 成交量 (Row 2) ---
        fig.add_trace(go.Bar(x=data_plot.index, y=data_plot['Volume'],
                             name='成交量'), row=2, col=1)
        fig.add_trace(go.Scatter(x=data_plot.index, y=data_plot[VOL_MA_COL],
                                mode='lines', name=VOL_MA_COL,
                                line=dict(color='purple', width=1, dash='dash')), row=2, col=1)
        
        # --- 3c. (全新) KD 指標 (Row 3) ---
        fig.add_trace(go.Scatter(x=data_plot.index, y=data_plot['K'],
                                mode='lines', name='K值',
                                line=dict(color='blue', width=2)), row=3, col=1)
        fig.add_trace(go.Scatter(x=data_plot.index, y=data_plot['D'],
                                mode='lines', name='D值',
                                line=dict(color='red', width=2)), row=3, col=1)
        # 繪製 80 (超買) 和 20 (超賣) 的水平線
        fig.add_hline(y=80, line_dash="dash", line_color="gray", row=3, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="gray", row=3, col=1)

        # --- 3d. 圖表美化 ---
        fig.update_layout(
            title=f'{stock_id} 多重指標分析圖 (價/量/KD)',
            yaxis_title='股價',
            yaxis2_title='成交量',
            yaxis3_title='KD值', # <-- (新增)
            xaxis_rangeslider_visible=False,
            legend_title_text='圖例',
            height=700 # 拉高圖表，容納三張子圖
        )
        return fig
    except Exception as e:
        st.error(f"繪製圖表時出錯: {e}")
        return None

# --- 4. Streamlit App 主體 ---
if st.button('🚀 開始掃描 (專業版)'):
    with st.spinner('正在執行多重過濾掃描 (趨勢+動能+量能)...'):
        all_stocks_df, signal_stocks_df, all_stock_ids = scan_all_stocks()

    if all_stock_ids is None:
        st.error(signal_stocks_df) 
    else:
        st.success('掃描完畢！')
        
        st.subheader(f'🔥 高品質專業訊號 ({len(signal_stocks_df)} 檔)')
        if signal_stocks_df.empty:
            st.info("今日 (最新資料日) 沒有任何股票同時滿足「所有」嚴格條件。")
        else:
            cols_to_show = ["訊號", "最新收盤價", "建議停損價", "K值", "D值", "資料日期"]
            st.dataframe(signal_stocks_df.set_index("股票代號")[cols_to_show])
            
        st.subheader('📊 股票 K 線圖查詢 (價/量/KD三圖)')
        
        signal_stock_ids = signal_stocks_df['股票代號'].tolist() if not signal_stocks_df.empty else []
        other_stock_ids = sorted(list(set(all_stock_ids) - set(signal_stock_ids)))
        
        selected_stock = st.selectbox(
            '從所有掃描過的股票中選擇一檔來查看圖表：',
            options = ['- 請選擇 -'] + signal_stock_ids + other_stock_ids
        )

        if selected_stock != '- 請選擇 -':
            fig = create_stock_chart(selected_stock)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
        st.subheader(f'所有已掃描股票狀態總表 ({len(all_stocks_df)} 檔)')
        cols_total_show = ["訊號", "最新收盤價", "建議停損價", "K值", "MA60"]
        st.dataframe(all_stocks_df.set_index("股票代號")[cols_total_show])
