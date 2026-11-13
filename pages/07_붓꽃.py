import os
import platform
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import seaborn as sns
import streamlit as str_lit
import streamlit as st
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

# 1. 맷플롯립 한글 폰트 설정 (운영체제별 자동 감지 및 리눅스 클라우드 대응)
if platform.system() == "Windows":
    plt.rc("font", family="Malgun Gothic")
elif platform.system() == "Darwin":
    plt.rc("font", family="AppleGothic")
else:  # Linux (Streamlit Cloud 등)
    # 우분투/리눅스 환경에 NanumGothic이 설치되어 있는 경우 자동 적용
    font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    if os.path.exists(font_path):
        font_name = fm.FontProperties(fname=font_path).get_name()
        plt.rc("font", family=font_name)
    else:
        # 폰트가 없을 경우 기본 폰트로 설정하되 깨짐 방지 대책
        plt.rc("font", family="DejaVu Sans")

plt.rcParams["axes.unicode_minus"] = False

# 페이지 설정
st.set_page_config(
    page_title="봄날의 붓꽃 찾기", page_icon="🌷", layout="wide"
)

st.title("🌷 봄날의 붓꽃 정원: 내 마음속 품종 찾기")
st.write(
    "꽃잎의 너비와 길이를 조절해 보세요. 따스한 봄의 색감으로 AI가 붓꽃의 운명을 점쳐드립니다! ✨"
)


# 2. 데이터 로드 및 모델 학습
@st.cache_resource
def load_data_and_model():
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df["species"] = iris.target
    # 품종명도 예쁜 한글로 매핑
    df["species_name"] = df["species"].map(
        {0: "세토사 (Setosa)", 1: "버시컬러 (Versicolor)", 2: "버지니카 (Virginica)"}
    )

    X = df[["petal width (cm)", "petal length (cm)"]]
    y = df["species"]

    model = RandomForestClassifier(random_state=42)
    model.fit(X, y)

    return df, model, [
        "세토사 (Setosa)",
        "버시컬러 (Versicolor)",
        "버지니카 (Virginica)",
    ]


df, model, target_names = load_data_and_model()

# 3. 사이드바 - 사용자 입력 (가로: 너비, 세로: 길이)
st.sidebar.header("🌿 봄 정원 꽃잎 스펙 설정소")
petal_width = st.sidebar.slider(
    "꽃잎 너비 (cm) [가로축]",
    float(df["petal width (cm)"].min()),
    float(df["petal width (cm)"].max()),
    float(df["petal width (cm)"].mean()),
)
petal_length = st.sidebar.slider(
    "꽃잎 길이 (cm) [세로축]",
    float(df["petal length (cm)"].min()),
    float(df["petal length (cm)"].max()),
    float(df["petal length (cm)"].mean()),
)

# 4. 예측 수행
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
    st.subheader("🎯 봄바람 타고 온 품종 판독 결과")
    st.success(
        f"살랑살랑 봄바람을 타고온 이 꽃의 정체는 바로 **'{predicted_species}'**!"
    )

    st.write("**품종별 적중 확률 분석:**")
    for i, name in enumerate(target_names):
        st.write(f"- `{name}`: {prediction_proba[i]*100:.2f}%")

with col2:
    st.subheader("🌸 핑크빛 봄 정원 지형도 (너비 vs 길이)")

    # 5. 시각화 (봄 느낌의 화사한 커스텀 팔레트 적용)
    fig, ax = plt.subplots(figsize=(7, 5))

    # 봄 느낌을 주는 색상 지정 (연두, 코랄핑크, 연보라)
    spring_palette = {
        "세토사 (Setosa)": "#85E3FF",  # 싱그러운 하늘빛
        "버시컬러 (Versicolor)": "#FFB3BA",  # 따스한 핑크빛
        "버지니카 (Virginica)": "#BAABFF",  # 은은한 라벤더빛
    }

    sns.scatterplot(
        data=df,
        x="petal width (cm)",
        y="petal length (cm)",
        hue="species_name",
        palette=spring_palette,
        s=80,
        ax=ax,
        alpha=0.8,
    )

    # 사용자가 입력한 값 표시 (강렬하고 화사한 진분홍색 별표 마커)
    ax.scatter(
        [petal_width],
        [petal_length],
        color="#FF1493",
        s=300,
        marker="*",
        label="나의 봄날 픽",
        zorder=5,
    )

    # 축 이름과 제목을 완벽한 한국어로 설정
    ax.set_xlabel("꽃잎 너비 (Petal Width, cm)")
    ax.set_ylabel("꽃잎 길이 (Petal Length, cm)")
    ax.set_title("봄 정원 속 붓꽃들의 만남의 장소", fontsize=13, pad=12)
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    # 배경을 부드러운 화이트/연한 톤으로 맞춤
    ax.grid(True, linestyle="--", alpha=0.3)

    st.pyplot(fig)

# 6. 분류 이유 설명
st.markdown("---")
st.subheader("🌷 AI 정원사의 따스한 추리 리포트")
st.info(
    f"""
- **가로축(너비)** {petal_width}cm, **세로축(길이)** {petal_length}cm인 자리에 예쁜 꽃잎을 심어보았습니다[cite: 1, 2, 3].
- 이 위치는 봄 정원에서 **`{predicted_species}`** 품종들이 햇살을 받으며 모여 있는 구역과 완벽하게 맞아떨어집니다!
- 싱그러운 봄의 기운을 담아 AI가 이 품종으로 다정하게 추천해 드립니다. 🌸✨
"""
)
