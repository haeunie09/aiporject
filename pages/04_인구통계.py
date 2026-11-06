import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.font_manager as fm
import os
import platform
import urllib.request

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="서울시 인구 통계 분석",
    page_icon="📊",
    layout="wide"
)

# 2. 한글 폰트 자동 다운로드 및 강제 적용 (글자 깨짐 방지)
def setup_korean_font():
    font_path = 'NanumGothic.ttf'
    if not os.path.exists(font_path):
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
            urllib.request.urlretrieve(url, font_path)
        except Exception:
            pass

    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        font_name = fm.FontProperties(fname=font_path).get_name()
        plt.rc('font', family=font_name)
    else:
        current_os = platform.system()
        if current_os == 'Windows':
            plt.rc('font', family='Malgun Gothic')
        elif current_os == 'Darwin':
            plt.rc('font', family='AppleGothic')
        else:
            plt.rc('font', family='sans-serif')
            
    plt.rc('axes', unicode_minus=False)

setup_korean_font()

# 3. 데이터 로드 및 전처리 (상위 폴더의 population.csv 참조)
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

# 4. 앱 헤더 및 설명
st.title("📊 서울시 구별 연령대 인구 분포 대시보드")
st.write("행정구, 성별, 연도를 선택하여 연령별 인구 흐름을 꺾은선 그래프로 확인하세요.")

# 5. 사이드바 조건 선택 옵션
st.sidebar.header("⚙️ 분석 조건 선택")

region_list = df['지역명'].tolist()
selected_region = st.sidebar.selectbox("행정구 선택", region_list, index=0)

# 성별 선택 옵션 매핑 수정 (NameError 원인 해결)
gender_options = {"전체": "거주자", "남성": "남_거주자", "여성": "여_거주자"}
selected_gender_label = st.sidebar.selectbox("성별 선택", list(gender_options.keys()), index=0)
gender_code = gender_options[selected_gender_label]

selected_year = st.sidebar.slider("연도 선택", min_value=2020, max_value=2025, value=2024)

# 6. 선택한 조건에 따른 데이터 추출
age_brackets = [
    '0~9세', '10~19세', '20~29세', '30~39세', '40~49세',
    '50~59세', '60~69세', '70~79세', '80~89세', '90~99세', '100세 이상'
]

target_cols = [f"{selected_year}년_{gender_code}_{age}" for age in age_brackets]

region_row = df[df['지역명'] == selected_region].iloc[0]
population_values = [region_row[col] for col in target_cols]

# 7. 성별에 따른 그래프 색상 설정 (여성: 베이비 핑크, 남성: 밝은 하늘색, 전체: 보라색)
color_map = {
    "여성": "#FFB6C1",  # 베이비 핑크
    "남성": "#87CEEB",  # 밝은 하늘색
    "전체": "#9370DB"   # 보라색
}
line_color = color_map.get(selected_gender_label, "#9370DB")

# 8. 그래프 시각화
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

# 선택한 연도와 행정구가 합쳐진 제목 설정
ax.set_title(f"{selected_year
