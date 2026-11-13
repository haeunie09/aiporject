import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

# 페이지 설정
st.set_page_config(
    page_title="Spring Garden Iris Classifier", page_icon="🌷", layout="wide"
)

st.title("🌷 봄날의 붓꽃 정원: AI 품종 판독소")
st.write(
    "꽃잎의 너비와 길이를 조절해 보세요. 화사한 봄의 색감 속에서 AI 알고리즘들이 붓꽃의 운명을 점쳐드립니다! ✨"
)


# 1. 데이터 로드
@st.cache_resource
def load_data():
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df["species"] = iris.target
    # 폰트 깨짐 방지를 위해 범례도 깔끔한 영문으로 통일
    df["species_name"] = df["species"].map(
        {0: "Setosa", 1: "Versicolor", 2: "Virginica"}
    )
    return df, iris.target_names


df, target_names = load_data()

# 2. 사이드바 - 사용자 입력 및 알고리즘 선택
st.sidebar.header("🌿 봄 정원 설정소")

# 알고리즘 선택 옵션
algorithm_choice = st.sidebar.selectbox(
    "AI 알고리즘 선택",
    [
        "Random Forest (랜덤 포레스트)",
        "K-NN (K-최근접 이웃)",
        "SVM (서포트 벡터 머신)",
    ],
)

petal_width = st.sidebar.slider(
    "Petal Width (cm) [Width / 가로]",
    float(df["petal width (cm)"].min()),
    float(df["petal width (cm)"].max()),
    float(df["petal width (cm)"].mean()),
)
petal_length = st.sidebar.slider(
    "Petal Length (cm) [Length / 세로]",
    float(df["petal length (cm)"].min()),
    float(df["petal length (cm)"].max()),
    float(df["petal length (cm)"].mean()),
)

# 3. 선택한 알고리즘에 따른 모델 학습 및 예측
X = df[["petal width (cm)", "petal length (cm)"]]
y = df["species"]

if algorithm_choice == "Random Forest (랜덤 포레스트)":
    model = RandomForestClassifier(random_state=42)
    algo_desc = (
        "**랜덤 포레스트 (Random Forest)**: 여러 개의 의사결정 나무(Decision Tree)들이 모여 다수결로 똑똑하게 정답을 맞히는 앙상블 알고리즘입니다. 숲처럼 든든하고 안정적인 예측을 보여줘요!"
    )
elif algorithm_choice == "K-NN (K-최근접 이웃)":
    model = KNeighborsClassifier(n_neighbors=5)
    algo_desc = (
        "**K-NN (K-Nearest Neighbors)**: '내 이웃의 주민을 보면 나를 알 수 있다!'는 철학을 가진 알고리즘입니다. 내 주변에서 가장 가까운 5마리의 붓꽃 친구들을 살펴보고 가장 많은 품종으로 줄을 세워요."
    )
else:
    model = SVC(probability=True, random_state=42)
    algo_desc = (
        "**SVM (Support Vector Machine)**: 품종들 사이에 가장 완벽하고 안전한 철벽 방어선(경계면)을 그어서, 새로운 꽃이 어느 구역에 안전하게 안착할지 냉철하게 분석하는 알고리즘입니다."
    )

model.fit(X, y)

# 예측 수행
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
        f"선택하신 알고리즘이 분석한 결과, 이 꽃은 **'{predicted_species.upper()}'** 품종입니다!"
    )

    st.write("**품종별 적중 확률 분석:**")
    for i, name in enumerate(target_names):
        st.write(f"- `{name}`: {prediction_proba[i]*100:.2f}%")

    st.markdown("---")
    st.subheader("💡 선택한 AI 알고리즘 이야기")
    st.info(algo_desc)

with col2:
    st.subheader("🌸 Spring Garden Iris Map")

    # 4. 시각화 (폰트 깨짐을 완벽히 막기 위해 순수 영문 레이블 사용)
    fig, ax = plt.subplots(figsize=(7, 5))

    spring_palette = {
        "Setosa": "#85E3FF",  # 싱그러운 하늘빛
        "Versicolor": "#FFB3BA",  # 따스한 핑크빛
        "Virginica": "#BAABFF",  # 은은한 라벤더빛
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

    # 사용자 입력값 표시 (진분홍색 별표 마커)
    ax.scatter(
        [petal_width],
        [petal_length],
        color="#FF1493",
        s=300,
        marker="*",
        label="My Spring Pick",
        zorder=5,
    )

    # 100% 깨지지 않는 영문 축 및 타이틀
    ax.set_xlabel("Petal Width (cm)")
    ax.set_ylabel("Petal Length (cm)")
    ax.set_title("Iris Cluster Map (Width vs Length)", fontsize=12, pad=12)
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    ax.grid(True, linestyle="--", alpha=0.3)

    st.pyplot(fig)

# 5. 하단 탐정 리포트
st.markdown("---")
st.subheader("🌷 AI 정원사의 따스한 추리 리포트")
st.write(
    f"너비 **{petal_width}cm**, 길이 **{petal_length}cm** 위치에 피어난 꽃잎을 **{algorithm_choice}** 모델이 정성껏 진단했습니다. 화사한 봄 정원 속에서 이 꽃이 어떤 군집과 어울리는지 지형도에서 확인해보세요! ✨"
)
