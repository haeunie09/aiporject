import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="국가별 MBTI 분포 시각화", page_icon="🌍", layout="wide"
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

# Title & 설명
st.title("🌍 국가별 MBTI 비율 시각화 대시보드")
st.write(
    "원하는 국가를 선택하면 16가지 MBTI 유형의 비율을 한눈에 확인할 수"
    " 있습니다."
)
st.markdown("---")

# 국가 선택 (기본 선택: South Korea가 있을 경우 지정, 없으면 첫 번째 국가)
default_index = (
    list(df["Country"]).index("South Korea")
    if "South Korea" in df["Country"].values
    else 0
)
selected_country = st.selectbox(
    "📌 국가를 선택하세요:", df["Country"].unique(), index=default_index
)

if selected_country:
  # 선택한 국가 데이터 추출 및 정렬
  country_row = df[df["Country"] == selected_country].iloc[0]
  mbti_series = country_row[mbti_cols].astype(float) * 100  # 퍼센트(%) 변환

  # 데이터프레임으로 정리 및 비율 내림차순 정렬
  data = (
      pd.DataFrame({"MBTI": mbti_series.index, "Percentage": mbti_series.values})
      .sort_values(by="Percentage", ascending=False)
      .reset_index(drop=True)
  )

  # 색상 설정 (1등: 분홍색 #FF69B4 / 2~16등: 순위에 따라 짙은 푸른색 -> 연한 푸른색 그라데이션)
  # 푸른색 계열 15단계 색상 리스트
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

  # 1등 분홍색(#FF69B4) + 나머지 푸른색 그라데이션 조합
  colors = ["#FF69B4"] + blue_shades[: len(data) - 1]
  data["Color"] = colors

  # Plotly 인터랙티브 막대그래프 생성
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

  # 레이아웃 스타일 설정
  fig.update_layout(
      title=dict(
          text=f"<b>[{selected_country}] MBTI 유형별 비율 순위</b>",
          font=dict(size=20),
      ),
      xaxis=dict(title="MBTI 유형", tickfont=dict(size=12)),
      yaxis=dict(title="비율 (%)", gridcolor="LightGray"),
      template="plotly_white",
      height=550,
  )

  # Streamlit 화면에 그래프 출력
  st.plotly_chart(fig, use_container_width=True)

  # 상위 유형 요약 정보 제공
  top_mbti = data.iloc[0]["MBTI"]
  top_pct = data.iloc[0]["Percentage"]

  st.success(
      f"💡 **{selected_country}**에서 가장 높은 비율을 차지하는 MBTI는 **{top_mbti}**입니다."
      f" ({top_pct:.2f}%)"
  )

  # 상세 데이터 테이블 표시
  with st.expander("📄 상세 데이터 확인하기"):
    st.dataframe(
        data[["MBTI", "Percentage"]].rename(
            columns={"Percentage": "비율 (%)"}
        ),
        use_container_width=True,
    )
