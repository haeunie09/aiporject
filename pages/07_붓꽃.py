import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

# 페이지 설정
st.set_page_config(
    page_title="봄날의 붓꽃 찾기", page_icon="🌷", layout="wide"
)

st.title("🌷 봄날의 붓꽃 정원: 내 마음속 품종 찾기")
st.write(
    "꽃잎의 너비와 길이를 조절해 보세요. 따스한 봄의 색감으로 AI가 붓꽃의 운명을 점쳐드립니다! ✨"
)


# 1. 데이터 로드 및 모델 학습
@st.cache_resource
def load_data_and_model():
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df["species"] = iris.target
    # 범례나 결과에서 사용할 품종명 (영문 조합으로 글자 깨짐 방지)
    df["species_name"] = df["species"].map(
        {0: "Setosa (세토사)", 1: "Versicolor (버시컬러)", 2: "Virginica (버지니카)"}
    )

    X = df[["petal width (cm)", "petal length (cm)"]]
    y = df["species"]

    model = RandomForestClassifier(random_state=42)
    model.fit(X, y)

    return df, model, [
        "Setosa (세토사)",
        "Versicolor (버시컬러)",
        "Virginica (버지니카)",
    ]


df, model, target_names = load_data_and_model()

# 2. 사이드바 - 사용자 입력 (가로: 너비, 세로: 길이)
st.sidebar.header("🌿 봄 정원 꽃잎 스펙 설정소")
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

# 3. 예측 수행
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

    # 4. 시각화 (봄 느낌의 화사한 색상 적용 & 폰트 깨짐 방지용 안전 영문/기호 조합)
    fig, ax = plt.subplots(figsize=(7, 5))

    # 봄 느낌 파스텔톤 팔레트
    spring_palette = {
        "Setosa (세토사)": "#85E3FF",  # 싱그러운 하늘빛
        "Versicolor (버시컬러)": "#FFB3BA",  # 따스한 핑크빛
        "Virginica (버지니카)": "#BAABFF",  # 은은한 라벤더빛
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

    # 사용자가 입력한 값 표시 (진분홍색 별표 마커)
    ax.scatter(
        [petal_width],
        [petal_length],
        color="#FF1493",
        s=300,
        marker="*",
        label="My Spring Pick (나의 픽)",
        zorder=5,
    )

    # 그래프 내부 텍스트는 영문으로 작성하여 클라우드 환경에서 깨짐 현상 원천 차단
    ax.set_xlabel("Petal Width (cm) [꽃잎 너비]")
    ax.set_ylabel("Petal Length (cm) [꽃잎 길이]")
    ax.set_title(
        "Spring Garden Iris Map (Width vs Length)", fontsize=12, pad=12
    )
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    ax.grid(True, linestyle="--", alpha=0.3)

    st.pyplot(fig)

# 5. 분류 이유 설명
st.markdown("---")
st.subheader("🌷 AI 정원사의 따스한 추리 리포트")
st.info(
    f"""
- **가로축(너비)** {petal_width}cm, **세로축(길이)** {petal_length}cm인 자리에 예쁜 꽃잎을 심어보았습니다[cite: 1, 2, 3, 4].
- 이 위치는 봄 정원에서 **`{predicted_species}`** 품종들이 햇살을 받으며 모여 있는 구역과 완벽하게 맞아떨어집니다!
- 싱그러운 봄의 기운을 담아 AI가 이 품종으로 다정하게 추천해 드립니다. 🌸✨
"""
)
