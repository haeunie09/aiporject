import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

    # 선택된 월의 데이터 필터링 및 연도순 정렬 (중복 연도가 있다면 평균 처리 혹은 마지막 값 유지)
    filtered_df = df[df['월'] == selected_month].groupby('연도', as_index=False).mean(numeric_only=True)
    filtered_df = filtered_df.sort_values('연도')

    # 3. 그래프 생성
    fig, ax = plt.subplots(figsize=(12, 6))

    # 최고기온(연한 보라색 #B19CD9), 최저기온(연한 연두색 #98FB98)
    # 글자 깨짐 방지를 위해 범례 라벨을 영문으로 지정
    ax.plot(filtered_df['연도'], filtered_df['최고기온(℃)'], label='Max Temp', color='#B19CD9', linewidth=2, marker='o', markersize=4)
    ax.plot(filtered_df['연도'], filtered_df['최저기온(℃)'], label='Min Temp', color='#98FB98', linewidth=2, marker='o', markersize=4)

    # 4. 그래프 제목 및 범례 설정 (글자 깨짐 방지를 위해 영문 사용)
    ax.set_title("Monthly Temperature Analysis", fontsize=16, pad=15)
    ax.legend(loc='upper right', fontsize=11)

    # 5. 축 레이블 설정
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Temperature", fontsize=12)

    # 6. X축(연도) 범위를 2026년(데이터의 최신 연도)까지 명확하게 강제 지정
    min_year = int(filtered_df['연도'].min())
    max_year = int(filtered_df['연도'].max())
    ax.set_xlim(min_year - 1, max_year + 1)
    
    # X축 눈금(Ticks)을 5년 단위 또는 적절히 끊어서 2026년까지 전부 표시되도록 설정
    import numpy as np
    ax.set_xticks(np.arange(min_year, max_year + 1, 5))

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
