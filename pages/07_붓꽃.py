import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

# 페이지 설정
st.set_page_config(
    page_title="Iris 품종 예측 및 시각화", page_icon="🌸", layout="wide"
)

st.title("🌸 붓꽃(Iris) 품종 예측 앱")
st.write(
    "꽃잎의 길이와 너비를 입력하면, 가장 널리 쓰이는 **랜덤 포레스트(Random Forest)** 알고리즘이 어떤 품종인지 예측하고 시각화해 줍니다."
)


# 1. 데이터 로드 및 모델 학습 (캐싱 활용)
@st.cache_resource
def load_data_and_model():
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df["species"] = iris.target
    df["species_name"] = df["species"].map(
        {0: "setosa", 1: "versicolor", 2: "virginica"}
    )

    # 꽃잎(Petal) 특성만 활용 (시각화 및 예측용)
    X = df[["petal length (cm)", "petal width (cm)"]]
    y = df["species"]

    model = RandomForestClassifier(random_state=42)
    model.fit(X, y)

    return df, model, iris.target_names


df, model, target_names = load_data_and_model()

# 2. 사이드바 - 사용자 입력
st.sidebar.header("🌿 꽃잎 특성 입력")
petal_length = st.sidebar.slider(
    "꽃잎 길이 (Petal Length, cm)",
    float(df["petal length (cm)"].min()),
    float(df["petal length (cm)"].max()),
    float(df["petal length (cm)"].mean()),
)
petal_width = st.sidebar.slider(
    "꽃잎 너비 (Petal Width, cm)",
    float(df["petal width (cm)"].min()),
    float(df["petal width (cm)"].max()),
    float(df["petal width (cm)"].mean()),
)

# 3. 예측 수행
input_data = pd.DataFrame(
    [[petal_length, petal_width]],
    columns=["petal length (cm)", "petal width (cm)"],
)
prediction = model.predict(input_data)[0]
prediction_proba = model.predict_proba(input_data)[0]

predicted_species = target_names[prediction]

# 메인 화면 결과 출력
col1, col2 = st.columns(2)

with col1:
    st.subheader("📌 예측 결과")
    st.success(
        f"입력하신 꽃은 **'{predicted_species.upper()}'** 품종으로 예측됩니다!"
    )

    # 확률 표시
    st.write("**품종별 예측 확률:**")
    for i, name in enumerate(target_names):
        st.write(f"- `{name}`: {prediction_proba[i]*100:.2f}%")

with col2:
    st.subheader("📊 꽃잎 기준 품종 분포 및 입력값 시각화")

    # 4. 시각화 (가로축: 꽃잎 길이, 세로축: 꽃잎 너비)
    fig, ax = plt.subplots(figsize=(7, 5))

    # 기존 데이터 산점도 그리기
    sns.scatterplot(
        data=df,
        x="petal length (cm)",
        y="petal width (cm)",
        hue="species_name",
        palette="Set2",
        s=70,
        ax=ax,
        alpha=0.7,
    )

    # 사용자가 입력한 값 표시 (별표 마커)
    ax.scatter(
        [petal_length],
        [petal_width],
        color="red",
        s=200,
        marker="*",
        label="사용자 입력값",
        zorder=5,
    )

    ax.set_xlabel("Petal Length (cm) [꽃잎 길이]")
    ax.set_ylabel("Petal Width (cm) [꽃잎 너비]")
    ax.set_title("꽃잎 크기에 따른 품종 분포와 입력 위치")
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    st.pyplot(fig)

# 5. 왜 이 품종으로 분류되었는지 설명
st.markdown("---")
st.subheader("💡 분류 이유 설명")
st.info(
    f"""
- 이 앱에서 사용한 **랜덤 포레스트** 모델은 기존 붓꽃 데이터셋의 꽃잎 길이와 너비 패턴을 학습했습니다.
- 시각화 그래프에서 보시는 바와 같이, 입력하신 **꽃잎 길이({petal_length}cm)**와 **너비({petal_width}cm)**가 위치한 영역은 기존에 학습된 **`{predicted_species}`** 품종 데이터들이 모여 있는 영역과 가장 일치합니다.
- 특히 붓꽃 데이터는 **꽃잎(Petal)의 크기**가 품종을 구분하는 가장 결정적인 요인(Feature)이기 때문에 이와 같은 결과를 도출했습니다.
"""
)
