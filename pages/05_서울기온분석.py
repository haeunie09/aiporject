import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 페이지 기본 설정
st.set_page_config(page_title="월별 기온 분석", layout="wide")

st.title("월별 기온 분석 애플리케이션")

# 1. 데이터 불러오기 (한글 깨짐 방지: cp949 인코딩 사용)
@st.cache_data
def load_data():
    df = pd.read_csv('temperature.csv', encoding='cp949')
    
    # '일시' 컬럼 분할 (예: 'Oct-07' -> 월, 연도)
    date_split = df['일시'].str.split('-', expand=True)
    
    # 월 이름 -> 숫자 매핑
    month_map = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    
    df['월'] = date_split[0].map(month_map)
    
    # 2자리 연도를 4자리 연도로 변환
    def parse_year(yr_str):
        yr = int(yr_str)
        if yr <= 26:
            return 2000 + yr
        else:
            return 1900 + yr

    df['연도'] = date_split[1].apply(parse_year)
    return df

try:
    df = load_data()

    # 2. 월 선택 셀렉트박스
    selected_month = st.selectbox(
        "분석할 월을 선택하세요:",
        options=list(range(1, 13)),
        format_func=lambda x: f"{x}월"
    )

    # 3. 데이터 필터링 및 중복 연도 제거 (마지막 데이터 기준 또는 평균 처리)
    filtered_df = df[df['월'] == selected_month].copy()
    # 중복 연도가 있을 경우 마지막 행을 채택하거나 평균 처리 (여기서는 깔끔하게 평균 처리 후 연도순 정렬)
    filtered_df = filtered_df.groupby('연도', as_index=False).agg({
        '최고기온(℃)': 'max',
        '최저기온(℃)': 'min',
        '평균기온(℃)': 'mean'
    }).sort_values('연도')

    # 4. 그래프 생성
    fig, ax = plt.subplots(figsize=(12, 6))

    # 최고기온(연한 보라색 #B19CD9), 최저기온(연한 연두색 #98FB98)
    ax.plot(filtered_df['연도'], filtered_df['최고기온(℃)'], label='Max Temp', color='#B19CD9', linewidth=2, marker='o', markersize=4)
    ax.plot(filtered_df['연도'], filtered_df['최저기온(℃)'], label='Min Temp', color='#98FB98', linewidth=2, marker='o', markersize=4)

    # 5. 그래프 제목 및 범례 설정 (글자 깨짐 방지 영문 표기)
    ax.set_title("Monthly Temperature Analysis", fontsize=16, pad=15)
    ax.legend(loc='upper right', fontsize=11)

    # 6. 축 레이블 설정
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Temperature", fontsize=12)

    # 7. X축 범위를 데이터의 실제 최소/최대 연도(2026년 포함)까지 완벽하게 강제 고정
    min_year = int(filtered_df['연도'].min())
    max_year = int(filtered_df['연도'].max())  # 2026년까지 포함됨
    
    ax.set_xlim(min_year - 1, max_year + 1)
    
    # X축 눈금을 5년 단위로 명확하게 설정하여 2026년까지 모두 표시
    ax.set_xticks(np.arange(min_year, max_year + 1, 5))
    plt.xticks(rotation=45)

    # 그리드 추가 및 레이아웃 정리
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    # 스트림릿에 그래프 출력
    st.pyplot(fig)

    # 상세 데이터 확인용 테이블
    with st.expander("선택한 월의 상세 데이터 보기"):
        st.dataframe(filtered_df[['연도', '최고기온(℃)', '최저기온(℃)', '평균기온(℃)']].reset_index(drop=True))

except FileNotFoundError:
    st.error("`temperature.csv` 파일을 찾을 수 없습니다. 리포지토리 폴더에 파일을 업로드했는지 확인해 주세요.")
