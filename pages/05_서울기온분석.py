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
    
    # '일시' 컬럼 분할 (예: 'Oct-07' -> 월: Oct, 연도: 07)
    date_split = df['일시'].str.split('-', expand=True)
    
    # 월 이름 -> 숫자 매핑
    month_map = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    
    df['월'] = date_split[0].map(month_map)
    
    # 2자리 연도를 4자리 연도로 변환 (07~99 -> 1907~1999, 00~26 -> 2000~2026)
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

    # 2. 월 선택 사이드바/드롭다운
    selected_month = st.selectbox(
        "분석할 월을 선택하세요:",
        options=list(range(1, 13)),
        format_func=lambda x: f"{x}월"
    )

    # 선택된 월의 데이터 필터링 및 연도순 정렬
    filtered_df = df[df['월'] == selected_month].sort_values('연도')

    # 3. 그래프 생성
    fig, ax = plt.subplots(figsize=(12, 6))

    # 최고 기온 (연한 보라색: #C71585 또는 #B19CD9), 최저 기온 (연한 연두색: #90EE90 또는 #98FB98)
    ax.plot(filtered_df['연도'], filtered_df['최고기온(℃)'], label='최고기온', color='#B19CD9', linewidth=2, marker='o', markersize=4)
    ax.plot(filtered_df['연도'], filtered_df['최저기온(℃)'], label='최저기온', color='#98FB98', linewidth=2, marker='o', markersize=4)

    # 4. 그래프 제목 및 범례 설정
    ax.set_title("월별 기온분석", fontsize=16, pad=15)
    ax.legend(loc='upper right', fontsize=11)

    # 5. 축 레이블 설정 (요청사항: 가로축 및 세로축 레이블 지정)
    ax.set_xlabel("연도", fontsize=12)
    ax.set_ylabel("연도", fontsize=12)  # 요청하신 대로 세로축 레이블을 '연도'로 설정했습니다 (기온 단위 표시 원할 시 '기온(℃)'로 변경 가능)

    # 그리드 추가 및 레이아웃 정리
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    # 스트림릿에 그래프 출력
    st.pyplot(fig)

    # 데이터 테이블 표시 (선택사항)
    with st.expander("상세 데이터 보기"):
        st.dataframe(filtered_df[['일시', '연도', '월', '최고기온(℃)', '최저기온(℃)', '평균기온(℃)']])

except FileNotFoundError:
    st.error("`temperature.csv` 파일을 찾을 수 없습니다. 경로를 확인해 주세요.")
