import os
import pandas as pd
import numpy as np
import streamlit as st
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor
import plotly.graph_objects as go

# 페이지 기본 설정
st.set_page_config(page_title="월별 기온 예측 시뮬레이터", page_icon="🌡️", layout="wide")

st.title("🌡️ 머신러닝 회귀 알고리즘 기반 월별 평균기온 예측")
st.markdown("선택한 회귀 알고리즘에 따라 과거 기온 데이터를 학습하는 방식과 미래 예측값이 어떻게 달라지는지 비교해 보세요.")

# 1. 데이터 로드 및 전처리 함수
@st.cache_data
def load_data():
    file_candidates = ["temperature.csv", "temperature (1).csv"]
    file_path = None
    for candidate in file_candidates:
        if os.path.exists(candidate):
            file_path = candidate
            break
            
    if file_path is None:
        return None

    for enc in ["cp949", "euc-kr", "utf-8"]:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            break
        except UnicodeDecodeError:
            continue

    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }
    parts = df["일시"].str.split("-", expand=True)
    df["Month"] = parts[0].map(month_map)
    year_2d = parts[1].astype(int)

    years = []
    century = 1900
    prev_y = None
    for y in year_2d:
        if prev_y is not None and prev_y == 99 and y == 0:
            century = 2000
        years.append(century + y)
        prev_y = y

    df["Year"] = years
    df = df.dropna(subset=["평균기온(℃)"]).copy()
    return df

df = load_data()

if df is None:
    st.error("데이터 파일을 찾을 수 없습니다. 저장소에 `temperature.csv` 파일을 함께 업로드해 주세요.")
    st.stop()

# 2. 사용자 입력 UI (사이드바)
st.sidebar.header("⚙️ 예측 조건 설정")

selected_month = st.sidebar.selectbox(
    "1️⃣ 예측할 월(Month) 선택",
    options=list(range(1, 13)),
    format_func=lambda x: f"{x}월",
    index=7  # 기본값: 8월
)

max_data_year = int(df[df["Month"] == selected_month]["Year"].max())
target_year = st.sidebar.number_input(
    "2️⃣ 예측할 연도(Year) 입력",
    min_value=max_data_year + 1,
    max_value=2150,
    value=2030,
    step=1
)

algo_options = [
    "선형회귀 (Linear Regression)",
    "다항회귀 (Polynomial Regression)",
    "랜덤 포레스트 회귀 (Random Forest)"
]
selected_algo = st.sidebar.selectbox(
    "3️⃣ 회귀 알고리즘 선택",
    options=algo_options,
    index=0
)

show_all_compare = st.sidebar.checkbox("그래프에 다른 알고리즘 예측점 함께 표시", value=True)

# 3. 선택된 월 데이터 필터링 및 3가지 모델 학습
month_df = df[df["Month"] == selected_month].sort_values("Year")
X = month_df[["Year"]].values
y = month_df["평균기온(℃)"].values

models = {
    "선형회귀 (Linear Regression)": LinearRegression(),
    "다항회귀 (Polynomial Regression)": make_pipeline(PolynomialFeatures(degree=2), LinearRegression()),
    "랜덤 포레스트 회귀 (Random Forest)": RandomForestRegressor(n_estimators=100, random_state=42)
}

predictions = {}
for name, m in models.items():
    m.fit(X, y)
    predictions[name] = m.predict([[target_year]])[0]

active_model = models[selected_algo]
active_pred = predictions[selected_algo]

# 알고리즘별 시각화 스타일 지정
algo_colors = {
    "선형회귀 (Linear Regression)": "#FF6B6B",        # 코랄 레드
    "다항회귀 (Polynomial Regression)": "#9B5DE5",     # 퍼플
    "랜덤 포레스트 회귀 (Random Forest)": "#00BBF9"    # 스카이 블루
}
active_color = algo_colors[selected_algo]

# 4. 상단 핵심 요약 지표 출력
col1, col2, col3 = st.columns(3)
col1.metric(
    label=f"선택 모델 예측 ({selected_algo.split(' ')[0]})",
    value=f"{active_pred:.2f} ℃",
    delta=f"최근 관측 대비 {active_pred - month_df.iloc[-1]['평균기온(℃)']:+.2f} ℃"
)
col2.metric(
    label=f"최근 관측 기록 ({max_data_year}년 {selected_month}월)",
    value=f"{month_df.iloc[-1]['평균기온(℃)']:.1f} ℃"
)
col3.metric(
    label=f"역대 {selected_month}월 전체 평균",
    value=f"{y.mean():.2f} ℃"
)

# 5. 메인 그래프 생성
fig = go.Figure()

# (1) 실제 과거 관측 데이터
fig.add_trace(go.Scatter(
    x=month_df["Year"],
    y=month_df["평균기온(℃)"],
    mode="lines+markers",
    name="과거 실제 평균기온",
    line=dict(color="rgba(120, 120, 120, 0.3)", width=1.5),
    marker=dict(color="#5C6B73", size=6),
    hovertemplate="<b>%{x}년</b><br>실제 평균기온: %{y:.1f}℃<extra></extra>"
))

# (2) 선택된 모델의 과거 학습 곡선(직선)
y_pred_past = active_model.predict(X)
fig.add_trace(go.Scatter(
    x=month_df["Year"],
    y=y_pred_past,
    mode="lines",
    name=f"{selected_algo.split(' ')[0]} 학습 패턴",
    line=dict(color=active_color, width=3),
    hovertemplate="<b>%{x}년 학습값</b><br>모델 기온: %{y:.2f}℃<extra></extra>"
))

# (3) 선택된 모델의 미래 예측 연장선
future_years = np.arange(max_data_year, target_year + 1).reshape(-1, 1)
future_preds = active_model.predict(future_years)
fig.add_trace(go.Scatter(
    x=future_years.flatten(),
    y=future_preds,
    mode="lines",
    name=f"{selected_algo.split(' ')[0]} 미래 예측 경로",
    line=dict(color=active_color, width=3, dash="dash"),
    hoverinfo="skip"
))

# (4) 선택된 모델의 최종 예측 지점 강조 (별표 ★)
fig.add_trace(go.Scatter(
    x=[target_year],
    y=[active_pred],
    mode="markers+text",
    name=f"★ {selected_algo.split(' ')[0]} 예측값",
    marker=dict(color=active_color, size=16, symbol="star", line=dict(color="black", width=1)),
    text=[f"  {selected_algo.split(' ')[0]}: {active_pred:.2f}℃"],
    textposition="middle right",
    textfont=dict(size=13, color=active_color),
    hovertemplate=f"<b>{target_year}년 {selected_month}월 ({selected_algo.split(' ')[0]})</b><br>예측 기온: {active_pred:.2f}℃<extra></extra>"
))

# (5) 비교용: 나머지 2개 알고리즘의 예측 지점도 함께 표시 (체크박스 활성화 시)
if show_all_compare:
    for name, pred_val in predictions.items():
        if name != selected_algo:
            short_name = name.split(" ")[0]
            fig.add_trace(go.Scatter(
                x=[target_year],
                y=[pred_val],
                mode="markers+text",
                name=f"비교: {short_name} 예측값",
                marker=dict(color=algo_colors[name], size=11, symbol="diamond", opacity=0.8),
                text=[f"  {short_name}: {pred_val:.2f}℃"],
                textposition="middle right",
                textfont=dict(size=11, color=algo_colors[name]),
                hovertemplate=f"<b>{target_year}년 {selected_month}월 ({short_name})</b><br>예측 기온: {pred_val:.2f}℃<extra></extra>"
            ))

fig.update_layout(
    title=f"역대 {selected_month}월 평균기온 추이 및 {target_year}년 회귀 모델별 예측 ({selected_algo})",
    xaxis_title="연도 (Year)",
    yaxis_title="평균기온 (℃)",
    hovermode="x unified",
    template="plotly_white",
    height=540,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# 6. 알고리즘별 예측값 한눈에 비교하기 (표)
st.subheader(f"📊 {target_year}년 {selected_month}월 알고리즘별 예측 결과 비교")
compare_df = pd.DataFrame({
    "회귀 알고리즘": list(predictions.keys()),
    f"{target_year}년 예측 평균기온 (℃)": [round(v, 2) for v in predictions.values()],
    "선형회귀 대비 차이 (℃)": [round(v - predictions["선형회귀 (Linear Regression)"], 2) for v in predictions.values()],
    "예측 형태 특징": [
        "일정한 기울기의 직선으로 장기 추세 반영",
        "2차 곡선으로 최근 기온 상승 가속도 반영",
        "과거 최근 구간 패턴을 유지하는 계단형 예측"
    ]
})
st.dataframe(compare_df, use_container_width=True, hide_index=True)

# 7. 그래프 하단: 선택된 알고리즘 상세 원리 설명
st.divider()
st.subheader(f"📘 선택한 알고리즘 작동 원리: {selected_algo}")

if selected_algo == "선형회귀 (Linear Regression)":
    slope = active_model.coef_[0]
    intercept = active_model.intercept_
    st.markdown(f"""
    * **작동 방식:** 과거 관측 점들과 직선 사이의 오차 제곱합이 최소가 되는 **단 하나의 직선(1차 함수)**을 찾습니다.
    * **도출된 수식:** $y = {slope:.4f}x + ({intercept:.2f})$ (매년 평균 **{slope:+.4f}℃**, 10년당 **{slope*10:+.2f}℃** 변화)
    * **특징 및 한계:** 장기적인 상승/하락 방향을 직관적으로 파악하기 좋지만, 최근 들어 기온이 더 가파르게 오르는 비선형적 가속도는 반영하지 못하고 일정한 속도로만 미래를 예측합니다.
    """)

elif selected_algo == "다항회귀 (Polynomial Regression)":
    poly_reg = active_model.named_steps["linearregression"]
    c1, c2 = poly_reg.coef_[1], poly_reg.coef_[2]
    intercept = poly_reg.intercept_
    st.markdown(f"""
    * **작동 방식:** 입력 변수인 연도($x$)에 제곱항($x^2$)을 추가하여 데이터가 휘어지는 추세를 **부드러운 2차 곡선(포물선)**으로 학습합니다.
    * **도출된 수식:** $y = {c2:.6f}x^2 + ({c1:.4f})x + ({intercept:.2f})$
    * **특징 및 한계:** 1900년대 초반보다 최근 20~30년 동안 기온이 더 빠르게 상승한 경우, 그 **가속도**를 반영해 선형회귀보다 높거나 낮은 곡선형 예측값을 내놓습니다. 단, 너무 먼 미래 연도를 입력하면 곡선이 과도하게 급상승(또는 급하락)할 수 있습니다.
    """)

else:
    st.markdown(f"""
    * **작동 방식:** 데이터를 여러 조건(연도 구간)으로 나누어 예측하는 **결정 트리(Decision Tree) 100개**를 만든 뒤, 각 트리가 예측한 기온의 평균을 내는 **앙상블(Ensemble) 알고리즘**입니다.
    * **그래프 모양의 이유:** 과거 연도 구간별 기온 변화를 세밀하게 따라가기 때문에 그래프가 **계단 모양**으로 꺾이며 그려집니다.
    * **특징 및 한계:** 과거 데이터의 복잡한 변동성을 매우 잘 학습하지만, 트리 기반 모델은 학습한 데이터 범위($\\sim${max_data_year}년) 밖의 미래 연도에 대해서는 **가장 최근 구간의 학습값(마지막 계단 높이)을 그대로 유지**하며 수평으로 예측하는 특성이 있습니다.
    """)
