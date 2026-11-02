import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="국가별 MBTI 분포 분석 대시보드", page_icon="🌍", layout="wide"
)


# 데이터 불러오기 함수 (캐싱 적용)
@st.cache_data
def load_data():
  df = pd.read_csv("countriesMBTI_16types.csv")
  return df


# 데이터 로드
try:
  df = load_data()
except Exception as e:
  st.error(
      f"데이터 파일을 불러오는 데 실패했습니다. 'countriesMBTI_16types.csv' 파일이"
      f" 동일한 디렉토리에 있는지 확인해주세요. 오류 메시지: {e}"
  )
  st.stop()

# MBTI 16가지 컬럼 리스트
mbti_cols = [
    "INFJ",
    "ISFJ",
    "INTP",
    "ISFP",
    "ENTP",
    "INFP",
    "ENTJ",
    "ISTP",
    "INTJ",
    "ESFP",
    "ESTJ",
    "ENFP",
    "ESTP",
    "ISTJ",
    "ENFJ",
    "ESFJ",
]

# Title & 사이드바 메뉴 설정
st.title("🌍 전 세계 국가별 MBTI 분포 분석 대시보드")
st.sidebar.title("🧭 분석 메뉴")
analysis_mode = st.sidebar.radio(
    "원하는 분석 방식을 선택하세요:",
    ["1️⃣ 국가별 MBTI 분포 보기", "2️⃣ MBTI 유형별 국가 순위 보기"],
)

st.markdown("---")

# ==========================================
# 기능 1: 국가별 MBTI 분포 보기 (기존 기능 유지)
# ==========================================
if analysis_mode == "1️⃣ 국가별 MBTI 분포 보기":
  st.subheader("📊 선택한 국가의 16가지 MBTI 비율 비교")

  default_index = (
      list(df["Country"]).index("South Korea")
      if "South Korea" in df["Country"].values
      else 0
  )
  selected_country = st.selectbox(
      "📌 국가를 선택하세요:", df["Country"].unique(), index=default_index
  )

  if selected_country:
    country_row = df[df["Country"] == selected_country].iloc[0]
    mbti_series = country_row[mbti_cols].astype(float) * 100

    data = (
        pd.DataFrame(
            {"MBTI": mbti_series.index, "Percentage": mbti_series.values}
        )
        .sort_values(by="Percentage", ascending=False)
        .reset_index(drop=True)
    )

    # 색상 설정 (1등: 베이비핑크 #FFB6C1 / 2~16등: 푸른빛 계열 그라데이션)
    blue_shades = [
        "#17BECF",
        "#1F77B4",
        "#2575FC",
        "#3A7BD5",
        "#4A90E2",
        "#5C9CE6",
        "#6EA8EA",
        "#80B4EE",
        "#92C0F2",
        "#A4CCF6",
        "#B6D8FA",
        "#C8E4FE",
        "#DAF0FF",
        "#EBF6FF",
        "#F2F9FF",
    ]
    colors = ["#FFB6C1"] + blue_shades[: len(data) - 1]
    data["Color"] = colors

    fig = go.Figure(
        data=[
            go.Bar(
                x=data["MBTI"],
                y=data["Percentage"],
                marker_color=data["Color"],
                text=data["Percentage"].apply(lambda x: f"{x:.2f}%"),
                textposition="auto",
                hovertemplate=(
                    "<b>MBTI</b>: %{x}<br><b>비율</b>:"
                    " %{y:.2f}%<extra></extra>"
                ),
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text=f"<b>[{selected_country}] MBTI 유형별 비율 순위</b>",
            font=dict(size=18),
        ),
        xaxis=dict(title="MBTI 유형"),
        yaxis=dict(title="비율 (%)", gridcolor="LightGray"),
        template="plotly_white",
        height=520,
    )

    st.plotly_chart(fig, use_container_width=True)

    top_mbti = data.iloc[0]["MBTI"]
    top_pct = data.iloc[0]["Percentage"]
    st.success(
        f"💡 **{selected_country}**에서 가장 높은 비율을 차지하는 MBTI는"
        f" **{top_mbti}**입니다. ({top_pct:.2f}%)"
    )

    with st.expander("📄 상세 데이터 확인하기"):
      st.dataframe(
          data[["MBTI", "Percentage"]].rename(
              columns={"Percentage": "비율 (%)"}
          ),
          use_container_width=True,
      )

# ==========================================
# 기능 2: MBTI 유형별 국가 순위 보기 (신규 추가 기능)
# ==========================================
elif analysis_mode == "2️⃣ MBTI 유형별 국가 순위 보기":
  st.subheader("🏆 특정 MBTI 유형이 높은 국가 순위 (1등부터 나열)")

  selected_mbti = st.selectbox("📌 MBTI 유형을 선택하세요:", mbti_cols)
  top_n = st.slider(
      "표시할 상위 국가 수:", min_value=5, max_value=50, value=15
  )

  # 선택한 MBTI 기준 내림차순 정렬
  ranked_df = (
      df[["Country", selected_mbti]]
      .sort_values(by=selected_mbti, ascending=False)
      .head(top_n)
      .reset_index(drop=True)
  )
  ranked_df["Percentage"] = ranked_df[selected_mbti] * 100

  # 색상 설정: 1등은 베이비핑크(#FFB6C1), 나머지는 민트색 그라데이션
  # 짙은 민트(#008B8B / #20B2AA)에서 연한 민트(#AFEEEE / #E0FFFF)로 흐려지는 그라데이션 생성
  mint_shades = [
      "#008B8B",
      "#008B8B",
      "#20B2AA",
      "#20B2AA",
      "#48D1CC",
      "#48D1CC",
      "#40E0D0",
      "#AFEEEE",
      "#AFEEEE",
      "#BFEFFF",
      "#C6E2FF",
      "#D1EEEE",
      "#E0FFFF",
      "#E0FFFF",
      "#F0FFFF",
  ]
  # 선택된 top_n 수에 맞게 민트색 리스트 조정
  mint_colors = []
  for i in range(top_n - 1):
    idx = int(i * (len(mint_shades) / max(1, top_n - 1)))
    mint_colors.append(mint_shades[min(idx, len(mint_shades) - 1)])

  # 1등 베이비핑크 + 나머지 민트색 그라데이션 조합
  rank_colors = ["#FFB6C1"] + mint_colors

  fig_rank = go.Figure(
      data=[
          go.Bar(
              x=ranked_df["Country"],
              y=ranked_df["Percentage"],
              marker_color=rank_colors,
              text=ranked_df["Percentage"].apply(lambda x: f"{x:.2f}%"),
              textposition="auto",
              hovertemplate=(
                  "<b>국가</b>: %{x}<br><b>비율</b>:"
                  " %{y:.2f}%<extra></extra>"
              ),
          )
      ]
  )

  fig_rank.update_layout(
      title=dict(
          text=(
              f"<b>[{selected_mbti}] 유형 비율 상위 {top_n개}개 국가 순위"
              " (1등부터)</b>"
          ),
          font=dict(size=18),
      ),
      xaxis=dict(title="국가", tickangle=-45),
      yaxis=dict(title="비율 (%)", gridcolor="LightGray"),
      template="plotly_white",
      height=550,
  )

  st.plotly_chart(fig_rank, use_container_width=True)

  top_country = ranked_df.iloc[0]["Country"]
  top_country_pct = ranked_df.iloc[0]["Percentage"]
  st.success(
      f"💡 **{selected_mbti}** 유형 비율이 전 세계에서 가장 높은 국가는"
      f" **{top_country}**입니다. ({top_country_pct:.2f}%)"
  )

  with st.expander("📄 전체 순위 데이터 테이블 보기"):
    st.dataframe(
        ranked_df[["Country", "Percentage"]].rename(
            columns={"Country": "국가", "Percentage": "비율 (%)"}
        ),
        use_container_width=True,
    )
