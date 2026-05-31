import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import os

# 讀取 Excel 文件
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(
    BASE_DIR,
    "simulator_clean_frontend_backend_package.xlsx"
)

coef_df = pd.read_excel(
    file_path,
    sheet_name="後端係數"
)

center_df = pd.read_excel(
    file_path,
    sheet_name="中心化參數",
    header=2
)

event_df = pd.read_excel(
    file_path,
    sheet_name="事件類型文案",
    header=2
)

window_df = pd.read_excel(
    file_path,
    sheet_name="窗口說明"
)

# 取得中心化數值
MARKET_CAP_MEAN = (
    center_df.loc[
        center_df["變項"]
        == "log_market_cap",
        "mean_used_for_centering"
    ].iloc[0]
)

YOUTUBE_MEAN = (
    center_df.loc[
        center_df["變項"]
        == "log_youtube_channel_subscribers",
        "mean_used_for_centering"
    ].iloc[0]
)

## 建立輸入介面

st.title("K-pop 事件市場反應模擬器")

# 公司市值輸入
market_cap = st.number_input( 
    "公司市值", 
    min_value=0.0, 
    value=0.0,)

# YouTube 訂閱數輸入
youtube_subs = st.number_input(
    "YouTube 訂閱數",
    min_value=0,
    value=0
)

# 事件類型選擇
event_options = [
    "positive_activity",
    "positive_comeback",
    "positive_concert",
    "positive_resolution",
    "negative_PR_crisis",
    "negative_contract_crisis",
    "dating",
    "artist_transition"
]

event_type = st.selectbox(
    "事件類型",
    event_options
)

# 窗口選擇
window_options = [
    "AR[0]",
    "CAR[-1,+1]",
    "CAR[0,+1]",
    "CAR[0,+3]",
    "CAR[0,+5]",
    "CAR[-5,+5]",
    "CAR[-10,+10]"
]

window = st.selectbox(
    "事件窗口",
    window_options
)

# 計算中心化數值
import numpy as np

log_market_cap_c = (
    np.log(market_cap + 1)
    - MARKET_CAP_MEAN
)

log_youtube_c = (
    np.log(youtube_subs + 1)
    - YOUTUBE_MEAN
)

# 取得事件類型的係數
# 建立小工具函數
def get_coef(window, component):

    row = coef_df[
        (coef_df["窗口"] == window)
        &
        (coef_df["component_key"] == component)
    ]

    if row.empty:
        return 0

    return float(
        row["coefficient_pp"].iloc[0]
    )

# 取得係數
intercept = get_coef(
    window,
    "Intercept"
)

event_coef = get_coef(
    window,
    event_type
)

market_coef = get_coef(
    window,
    "log_market_cap_c"
)

youtube_coef = get_coef(
    window,
    "log_youtube_channel_subscribers_c"
)

# 計算預測CAR
predicted_car = (
    intercept
    + event_coef
    + market_coef * log_market_cap_c
    + youtube_coef * log_youtube_c
)

# 查詢市場訊號強度
row = coef_df[
    (coef_df["窗口"] == window)
    &
    (coef_df["component_key"] == event_type)
]

if row.empty:
    signal = " "
else:
    signal = row["市場訊號強度"].iloc[0]

# 顯示結果
st.metric(
    "Predicted CAR (%)",
    round(predicted_car,2)
)

if signal == "高穩健訊號":
    st.success(f"市場訊號強度：{signal}")

elif signal == "明確市場訊號":
    st.info(f"市場訊號強度：{signal}")

elif signal == "初步市場訊號":
    st.warning(f"市場訊號強度：{signal}")

else:
    st.error(f"市場訊號強度：{signal}")

# Plotly 圖表
fig = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=predicted_car,
        title={
            "text":"Predicted CAR (%)"
        },
        gauge={
            "axis":{
                "range":[-25,25]
            }
        }
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# 顯示商業解讀和管理建議
event_row = event_df[
    event_df["事件類型"] == event_type
].iloc[0]

st.subheader("商業解讀")

st.write(
    event_row["商業解讀"]
)

st.subheader("管理建議")

st.write(
    event_row["管理建議"]
)
