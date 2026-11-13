import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import seaborn as sns
import streamlit as st
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

# 페이지 설정
st.set_page_config(
    page_title="꽃잎 미인도: 붓꽃 품종 맞히기", page_icon="🌸", layout="wide"
)

# 폰트 깨짐 방지 설정 (시스템 폰트 자동 감지)
import platform

if platform.system() == "Windows":
    plt.rc("font", family="Malgun Gothic")
elif platform.system() == "Darwin":
    plt.rc("font", family="AppleGothic")
else:  # Linux (Streamlit Cloud 등)
    # 우분투 환경 등에서 한글 폰트가 없을 경우 영문 레이블로 안전하게 대체하거나 기본 폰트 사용
    plt.rc("font", family="DejaVu Sans")

plt.rcParams["axes.unicode_minus"] = False

st.title("🌸 꽃잎 미인도: 내 마음속에 꽂힌 붓꽃 찾기")
st.write(
    "꽃잎의 너비와 길이를 조절해 보세요. AI가 당신이 고른 붓꽃의 운명을 점쳐드립니다! ✨"
)


# 1. 데이터 로드 및 모델 학습
@st.cache_resource
def load_data_and_model():
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df["species"] = iris.target
    df["species_name"] = df["species"].map(
        {0: "setosa", 1: "versicolor", 2: "virginica"}
    )

    X = df[["petal width (cm)", "petal length (cm)"]]  # 너비, 길이 순서 학습
    y = df["species"]

    model = RandomForestClassifier(random_state=42)
    model.fit(X, y)

    return df, model, iris.target_names


df, model, target_names = load_data_and_model()

# 2. 사이드바 - 사용자 입력 (가로: 너비, 세로: 길이로 배치 매칭)
st.sidebar.header("🌿 꽃잎 스펙 설정소")
petal_width = st.sidebar.slider(
    "꽃잎 너비 (Petal Width, cm) [가로축]",
    float(df["petal width (cm)"].min()),
    float(df["petal width (cm)"].max()),
    float(df["petal width (cm)"].mean()),
)
petal_length = st.sidebar.slider(
    "꽃잎 길이 (Petal Length, cm) [세로축]",
    float(df["petal length (cm)"].min()),
    float(df["petal length (cm)"].max()),
    float(df["petal length (cm)"].mean()),
)

# 3. 예측 수행 (너비, 길이 순서 입력)
input_data = pd.DataFrame(
    [[petal_width, petal_length]],
    columns=["petal width (cm)", "petal length (cm)"],
)
prediction = model.predict(input_data)[0]
prediction_proba = model.predict_proba(input_data)[0]

predicted_species = target_names[prediction]

# 메인 화면 결과 출력
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 운명의 품종 판독 결과")
    st.success(f"두근두근... 이 꽃의 정체는 바로 **'{predicted_species.upper()}'**!")

    st.write("**품종별 적중 확률 분석:**")
    for i, name in enumerate(target_names):
        st.write(f"- `{name}`: {prediction_proba[i]*100:.2f}%")

with col2:
    st.subheader("🎨 꽃잎 지형도 (너비 vs 길이)")

    # 4. 시각화 (가로축: 꽃잎 너비, 세로축: 꽃잎 길이)
    fig, ax = plt.subplots(figsize=(7, 5))

    sns.scatterplot(
        data=df,
        x="petal width (cm)",
        y="petal length (cm)",
        hue="species_name",
        palette="Set2",
        s=70,
        ax=ax,
        alpha=0.7,
    )

    # 사용자 입력값 표시 (별표 마커)
    ax.scatter(
        [petal_width],
        [petal_length],
        color="crimson",
        s=250,
        marker="*",
        label="나의 픽 (Input)",
        zorder=5,
    )

    # 축 이름 변경 (가로: 너비, 세로: 길이)
    ax.set_xlabel("Petal Width (cm) [꽃잎 너비]")
    ax.set_ylabel("Petal Length (cm) [꽃잎 길이]")
    ax.set_title("너비와 길이로 본 붓꽃들의 미팅 장소", fontsize=12, pad=10)
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    st.pyplot(fig)

# 5. 분류 이유 설명
st.markdown("---")
st.subheader("🕵️‍♂️ AI 탐정의 추리 리포트")
st.info(
    f"""
- **가로축(너비)**에 {petal_width}cm, **세로축(길이)**에 {petal_length}cm인 지점을 콕 찍어보았습니다[cite: 1].
- 이 좌표는 방구석 붓꽃 백과사전의 데이터 중 **`{predicted_species}`** 군집이 알콩달콩 모여 있는 구역과 정확히 겹칩니다!
- 그래서 AI 모델이 망설임 없이 이 품종으로 낙점하게 되었답니다. 🌸
"""
)
