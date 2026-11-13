import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

# 페이지 설정
st.set_page_config(
    page_title="Iris Species Prediction", page_icon="🌸", layout="wide"
)

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

    # X 학습: [너비, 길이] 순서
    X = df[["petal width (cm)", "petal length (cm)"]]
    y = df["species"]

    model = RandomForestClassifier(random_state=42)
    model.fit(X, y)

    return df, model, iris.target_names


df, model, target_names = load_data_and_model()

# 2. 사이드바 - 사용자 입력 (가로: 너비, 세로: 길이)
st.sidebar.header("🌿 꽃잎 스펙 설정소")
petal_width = st.sidebar.slider(
    "Petal Width (cm) [가로축: 너비]",
    float(df["petal width (cm)"].min()),
    float(df["petal width (cm)"].max()),
    float(df["petal width (cm)"].mean()),
)
petal_length = st.sidebar.slider(
    "Petal Length (cm) [세로축: 길이]",
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
    st.subheader("🎯 운명의 품종 판독 결과")
    st.success(f"두근두근... 이 꽃의 정체는 바로 **'{predicted_species.upper()}'**!")

    st.write("**품종별 적중 확률 분석:**")
    for i, name in enumerate(target_names):
        st.write(f"- `{name}`: {prediction_proba[i]*100:.2f}%")

with col2:
    st.subheader("🎨 꽃잎 지형도 (Width vs Length)")

    # 4. 시각화 (폰트 깨짐 방지를 위해 영문 레이블 사용 / 가로: 너비, 세로: 길이)
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
        label="My Input",
        zorder=5,
    )

    # 그래프 내부 텍스트 영문 처리 (깨짐 원천 차단)
    ax.set_xlabel("Petal Width (cm)")
    ax.set_ylabel("Petal Length (cm)")
    ax.set_title("Iris Cluster Map (Width vs Length)", fontsize=12, pad=10)
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    st.pyplot(fig)

# 5. 분류 이유 설명
st.markdown("---")
st.subheader("🕵️‍♂️ AI 탐정의 추리 리포트")
st.info(
    f"""
- **가로축(Width)**에 {petal_width}cm, **세로축(Length)**에 {petal_length}cm인 지점을 콕 찍어보았습니다.
- 이 좌표는 붓꽃 데이터 중 **`{predicted_species}`** 군집이 알콩달콩 모여 있는 구역과 정확히 일치합니다!
- 그래서 AI 모델이 망설임 없이 이 품종으로 낙점하게 되었답니다. 🌸
"""
)
