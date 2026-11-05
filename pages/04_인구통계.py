import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.font_manager as fm
import os
import platform

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="서울시 인구 통계 분석",
    page_icon="📊",
    layout="wide"
)

# 2. Streamlit Cloud 및 다양한 OS 환경을 고려한 한글 폰트 설정
def setup_korean_font():
    # 리눅스(Streamlit Cloud)에서 나눔글꼴 경로 검색 및 설정
    font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        plt.rc('font', family='NanumGothic')
    else:
        # 로컬(Windows / Mac) 환경 예외 처리
        if platform.system() == 'Windows':
            plt.rc('font', family='Malgun Gothic')
        elif platform.system() == 'Darwin':
            plt.rc('font', family='AppleGothic')
        else:
            plt.rc('font', family='NanumGothic')
    
    plt.rc('axes', unicode_minus=False)

setup_korean_font()

# 3. 데이터 로드 및 전처리 (상위 폴더의 population.csv 참조)
@st.cache_data
def load_data():
    # pages 폴더 기준 상위 폴더에 위치한 population.csv 경로 설정
    file_path = os.path.join(os.path.dirname(__file__), '..', 'population.csv')
    
    # CP949 인코딩으로 불러오기
    df = pd.read_csv(file_path, encoding='cp949')
    
    # 숫자 칼럼의 쉼표(,) 제거 및 int 변환
    num_cols = [c for c in df.columns if c != '행정구역']
    for col in num_cols:
        df[col] = df[col].astype(str).str.replace(',', '').str.strip()
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
    # 행정구역명 정제 (코드 제거 후 지역명만 추출)
    df['지역명'] = df['행정구역'].str.split('(').str[0].str.strip()
    return df

df = load_data()

# 4. 앱 헤더 및 설명
st.title("📊 서울시 구별 연령대 인구 분포 대시보드")
st.write("행정구, 성별, 연도를 선택하여 연령별 인구 흐름을 꺾은선 그래프로 확인하세요.")

# 5. 사이드바 조건 선택 옵션
st.sidebar.header("⚙️ 분석 조건 선택")

# (1) 행정구 선택
region_list = df['지역명'].tolist()
selected_region = st.sidebar.selectbox("행정구 선택", region_list, index=0)

# (2) 성별 선택
gender_options = {"전체": "거주자", "남성": "남_거주자", "여성": "여_거주자"}
selected_gender_label = st.sidebar.selectbox("성별 선택", list(gender_options.keys()), index=0)
gender_code = gender_options[selected_gender_label]

# (3) 연도 선택 (2020년 ~ 2025년)
selected_year = st.sidebar.slider("연도 선택", min_value=2020, max_value=2025, value=2024)

# 6. 선택한 조건에 따른 데이터 추출
age_brackets = [
    '0~9세', '10~19세', '20~29세', '30~39세', '40~49세',
    '50~59세', '60~69세', '70~79세', '80~89세', '90~99세', '100세 이상'
]

# 칼럼명 조합 (예: 2024년_거주자_0~9세)
target_cols = [f"{selected_year}년_{gender_code}_{age}" for age in age_brackets]

region_row = df[df['지역명'] == selected_region].iloc[0]
population_values = [region_row[col] for col in target_cols]

# 7. 그래프 시각화
fig, ax = plt.subplots(figsize=(12, 6))

# 베이비 핑크 색상 적용 (#FFB6C1) 및 꺾은선 그래프 스타일 지정
ax.plot(
    age_brackets, 
    population_values, 
    color='#FFB6C1', 
    marker='o', 
    linewidth=3, 
    markersize=8, 
    label=f"{selected_region} ({selected_gender_label})"
)

# 눈금 및 구분선(Grid) 설정
# 가로축: 10살 단위 구분선
ax.grid(True, which='both', axis='both', linestyle='--', alpha=0.5)

# 세로축: 10만 단위(100,000) 구분선 설정
ax.yaxis.set_major_locator(ticker.MultipleLocator(100000))
# Y축 숫자 표기에 쉼표(,) 추가
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))

# 축 이름 및 제목 설정
ax.set_xlabel("나이 (연령대)", fontsize=12, labelpad=10)
ax.set_ylabel("인구수 (명 / 10만 단위 구분)", fontsize=12, labelpad=10)
ax.set_title(f"[{selected_year}년] {selected_region} - {selected_gender_label} 연령별 인구수", fontsize=15, pad=15)

# 데이터 포인트 값 표시 (상단 숫자 안내)
for i, txt in enumerate(population_values):
    ax.annotate(f"{txt:,}", (age_brackets[i], population_values[i]), 
                textcoords="offset points", xytext=(0, 8), ha='center', fontsize=9)

# 그래프 여백 및 Streamlit 출력
plt.tight_layout()
st.pyplot(fig)

# 8. 선택된 조건 요약 데이터 표 보기
st.subheader("📋 선택 데이터 상세 보기")
summary_df = pd.DataFrame({
    '연령대': age_brackets,
    '인구수(명)': [f"{val:,}" for val in population_values]
})
st.dataframe(summary_df.T)
