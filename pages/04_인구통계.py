import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.font_manager as fm
import os
import platform

st.set_page_config(
    page_title="서울시 인구 통계 분석",
    page_icon="📊",
    layout="wide"
)

def setup_korean_font():
    current_os = platform.system()
    if current_os == 'Windows':
        plt.rc('font', family='Malgun Gothic')
    elif current_os == 'Darwin':
        plt.rc('font', family='AppleGothic')
    else:
        font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
        if os.path.exists(font_path):
            fm.fontManager.addfont(font_path)
            plt.rc('font', family='NanumGothic')
        else:
            plt.rc('font', family='sans-serif')
            
    plt.rc('axes', unicode_minus=False)

setup_korean_font()

@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'population.csv')
    df = pd.read_csv(file_path, encoding='cp949')
    
    num_cols = [c for c in df.columns if c != '행정구역']
    for col in num_cols:
        df[col] = df[col].astype(str).str.replace(',', '').str.strip()
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
    df['지역명'] = df['행정구역'].str.split('(').str[0].str.strip()
    return df

df = load_data()

st.title("📊 서울시 구별 연령대 인구 분포 대시보드")
st.write("행정구, 성별, 연도를 선택하여 연령별 인구 흐름을 꺾은선 그래프로 확인하세요.")

st.sidebar.header("⚙️ 분석 조건 선택")

region_list = df['지역명'].tolist()
selected_region = st.sidebar.selectbox("행정구 선택", region_list, index=0)

gender_options = {"전체": "거주자", "남성": "남_거주자", "여성": "여_거주자"}
selected_gender_label = st.sidebar.selectbox("성별 선택", list(gender_options.keys()), index=0)
gender_code = gender_options[selected_gender_label]

selected_year = st.sidebar.slider("연도 선택", min_value=2020, max_value=2025, value=2024)

age_brackets = [
    '0~9세', '10~19세', '20~29세', '30~39세', '40~49세',
    '50~59세', '60~69세', '70~79세', '80~89세', '90~99세', '100세 이상'
]

target_cols = [f"{selected_year}년_{gender_code}_{age}" for age in age_brackets]

region_row = df[df['지역명'] == selected_region].iloc[0]
population_values = [region_row[col] for col in target_cols]

color_map = {
    "여성": "#FFB6C1",
    "남성": "#87CEEB",
    "전체": "#9370DB"
}
line_color = color_map.get(selected_gender_label, "#9370DB")

fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(
    age_brackets, 
    population_values, 
    color=line_color, 
    marker='o', 
    linewidth=3, 
    markersize=8, 
    label=f"{selected_region} ({selected_gender_label})"
)

ax.grid(True, which='both', axis='both', linestyle='--', alpha=0.5)

ax.yaxis.set_major_locator(ticker.MultipleLocator(100000))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))

ax.set_xlabel("나이 (연령대)", fontsize=12, labelpad=10)
ax.set_ylabel("인구수 (명)", fontsize=12, labelpad=10)

for i, txt in enumerate(population_values):
    ax.annotate(f"{txt:,}", (age_brackets[i], population_values[i]), 
                textcoords="offset points", xytext=(0, 8), ha='center', fontsize=9)

plt.tight_layout()
st.pyplot(fig)

st.subheader("📋 선택 데이터 상세 보기")
summary_df = pd.DataFrame({
    '연령대': age_brackets,
    '인구수(명)': [f"{val:,}" for val in population_values]
})
st.dataframe(summary_df.T)
