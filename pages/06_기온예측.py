import os
import pandas as pd
import numpy as np
import streamlit as st
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go

# 페이지 기본 설정
st.set_page_config(page_title="월별 기온 예측 시뮬레이터", page_icon="🌡️", layout="wide")

st.title("🌡️ 선형회귀 기반 월별 평균기온 예측")
st.markdown("과거 기상 관측 데이터를 바탕으로 선택한 월의 장기 기온 추세를 분석하고 미래 평균기온을 예측합니다.")

# 1. 데이터 로드 및 전처리 함수
@st.cache_data
def load_data():
    # 파일명 후보 확인 (temperature.csv 또는 업로드된 원본 파일명)
    file_candidates = ["temperature.csv", "temperature (1).csv"]
    file_path = None
    for candidate in file_candidates:
        if os.path.exists(candidate):
            file_path = candidate
            break
            
    if file_path is None:
        return None

    # 인코딩 자동 판별 로드
    for enc in ["cp949", "euc-kr", "utf-8"]:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            break
        except UnicodeDecodeError:
            continue

    # '일시' 컬럼(예: Oct-07)에서 월(Month)과 4자리 연도(Year) 추출
    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }
    parts = df["일시"].str.split("-", expand=True)
    df["Month"] = parts[0].map(month_map)
    year_2d = parts[1].astype(int)

    # 1907년부터 시작하여 99 -> 00 전환 시점에 2000년대로 변경
    years = []
    century = 1900
    prev_y = None
    for y in year_2d:
        if prev_y is not None and prev_y == 99 and y == 0:
            century = 2000
        years.append(century + y)
        prev_y = y

    df["Year"] = years
    # 평균기온 결측치 제거
    df = df.dropna(subset=["평균기온(℃)"]).copy()
    return df

df = load_data()

if df is None:
    st.error("데이터 파일을 찾을 수 없습니다. 저장소에 `temperature.csv` 파일을 함께 업로드해 주세요.")
    st.stop()

# 2. 사용자 입력 UI (사이드바)
st.sidebar.header("⚙️ 예측 조건 설정")
selected_month = st.sidebar.selectbox(
    "예측할 월(Month) 선택",
    options=list(range(1, 13)),
    format_func=lambda x: f"{x}월",
    index=7  # 기본값: 8월
)

max_data_year = int(df[df["Month"] == selected_month]["Year"].max())
target_year = st.sidebar.number_input(
    "예측할 연도(Year) 입력",
    min_value=max_data_year + 1,
    max_value=2150,
    value=2030,
    step=1
)

# 3. 선택된 월 데이터 필터링 및 선형회귀 모델 학습
month_df = df[df["Month"] == selected_month].sort_values("Year")

X = month_df[["Year"]].values
y = month_df["평균기온(℃)"].values

model = LinearRegression()
model.fit(X, y)

slope = model.coef_[0]          # 기울기 (연간 기온 변화량)
intercept = model.intercept_    # y절편
r2_score = model.score(X, y)    # 결정계수 (R²)
predicted_temp = model.predict([[target_year]])[0]

# 4. 핵심 요약 지표 출력
col1, col2, col3 = st.columns(3)
col1.metric(
    label=f"{target_year}년 {selected_month}월 예측 평균기온",
    value=f"{predicted_temp:.2f} ℃"
)
col2.metric(
    label="10년당 평균기온 변화율",
    value=f"{slope * 10:+.2f} ℃ / 10년"
)
col3.metric(
    label=f"최근 관측 기록 ({max_data_year}년 {selected_month}월)",
    value=f"{month_df.iloc[-1]['평균기온(℃)']:.1f} ℃"
)

# 5. 선형회귀 작동 원리를 보여주는 인터랙티브 그래프
fig = go.Figure()

# (1) 실제 과거 관측 데이터 (산점도 + 연한 연결선)
fig.add_trace(go.Scatter(
    x=month_df["Year"],
    y=month_df["평균기온(℃)"],
    mode="lines+markers",
    name="과거 실제 평균기온",
    line=dict(color="rgba(100, 149, 237, 0.35)", width=1.5),
    marker=dict(color="#4A90E2", size=6),
    hovertemplate="<b>%{x}년</b><br>실제 평균기온: %{y:.1f}℃<extra></extra>"
))

# (2) 학습 구간 선형회귀 추세선 (과거 데이터 기반 최적 직선)
y_pred_past = model.predict(X)
fig.add_trace(go.Scatter(
    x=month_df["Year"],
    y=y_pred_past,
    mode="lines",
    name=f"선형회귀 추세선 (y = {slope:.4f}x + {intercept:.2f})",
    line=dict(color="#FF6B6B", width=3),
    hovertemplate="<b>%{x}년 추세값</b><br>회귀선 기온: %{y:.2f}℃<extra></extra>"
))

# (3) 미래 예측 연장선 (마지막 관측 연도 ~ 목표 예측 연도)
future_years = np.arange(max_data_year, target_year + 1).reshape(-1, 1)
future_preds = model.predict(future_years)
fig.add_trace(go.Scatter(
    x=future_years.flatten(),
    y=future_preds,
    mode="lines",
    name="미래 추세 연장선 (Extrapolation)",
    line=dict(color="#FF6B6B", width=3, dash="dash"),
    hoverinfo="skip"
))

# (4) 최종 예측 지점 강조 마커
fig.add_trace(go.Scatter(
    x=[target_year],
    y=[predicted_temp],
    mode="markers+text",
    name=f"{target_year}년 예측값",
    marker=dict(color="#D90429", size=15, symbol="star"),
    text=[f"  {target_year}년 예측: {predicted_temp:.2f}℃"],
    textposition="middle right",
    textfont=dict(size=13, color="#D90429"),
    hovertemplate=f"<b>{target_year}년 {selected_month}월 예측</b><br>예측 기온: {predicted_temp:.2f}℃<extra></extra>"
))

fig.update_layout(
    title=f"역대 {selected_month}월 평균기온 추이 및 {target_year}년 선형회귀 예측",
    xaxis_title="연도 (Year)",
    yaxis_title="평균기온 (℃)",
    hovermode="x unified",
    template="plotly_white",
    height=520,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# 6. 그래프 하단: 선형회귀 알고리즘 설명
st.divider()
st.subheader("📘 선형회귀(Linear Regression) 알고리즘 작동 원리")

st.markdown(f"""
**1. 선형회귀란 무엇인가요?**  
선형회귀는 독립 변수($x$, 여기서는 **연도**)와 종속 변수($y$, 여기서는 **{selected_month}월 평균기온**) 사이의 관계를 가장 잘 설명하는 **하나의 직선(추세선)**을 찾아내는 지도학습(Supervised Learning) 알고리즘입니다.

**2. 그래프에서 선이 그려지는 원리 (최소제곱법)**  
* 그래프의 **파란색 점**들은 과거 관측된 실제 {selected_month}월 평균기온입니다.
* 알고리즘은 모든 파란색 점들과 빨간색 직선 사이의 수직 거리(**오차, Residual**)의 제곱합이 가장 작아지도록 직선의 위치와 각도를 계산합니다. 이를 **최소제곱법(Ordinary Least Squares)**이라고 합니다.

**3. 현재 데이터로 도출된 예측 방정식**  
분석 결과, {selected_month}월 평균기온을 예측하기 위해 만들어진 1차 함수 식은 다음과 같습니다.
$$y = {slope:.4f}x + ({intercept:.2f})$$
* **기울기 ($w = {slope:.4f}$):** 매년 {selected_month}월 평균기온이 평균적으로 **{slope:+.4f}℃**씩 변하고 있음을 의미합니다. (10년 기준 **{slope*10:+.2f}℃**)
* **미래 예측 (붉은 점선과 별표 ★):** 위 방정식의 $x$ 자리에 입력하신 **{target_year}**을 대입하여 직선을 연장한 결과, **{predicted_temp:.2f}℃**라는 예측값이 도출되었습니다.
""")
