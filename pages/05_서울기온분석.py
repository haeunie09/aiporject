import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import platform

# 1. 맷플롯립 한글 폰트 설정 (운영체제별 자동 대응)
if platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':
    plt.rc('font', family='AppleGothic')
else:
    # 스트림릿 클라우드(Linux) 환경에서 한글 깨짐 방지를 위한 조치
    plt.rc('font', family='DejaVu Sans')

# 마이너스 기호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False

# 페이지 기본 설정
st.set_page_config(page_title="월별 기온 분석", layout="wide")

st.title("월별 기온 분석 애플리케이션")

# 2. 데이터 불러오기 (한글 깨짐 방지: cp949 인코딩 사용)
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

    # 3. 월 선택 셀렉트박스
    selected_month = st.selectbox(
        "분석할 월을 선택하세요:",
        options=list(range(1, 13)),
        format_func=lambda x: f"{x}월"
    )

    # 선택된 월의 데이터 필터링 및 연도순 정렬
    filtered_df = df[df['월'] == selected_month].sort_values('연도')

    # 4. 그래프 생성
    fig, ax = plt.subplots(figsize=(12, 6))

    # 최고기온: 연한 보라색 (#B19CD9), 최저기온: 연한 연두색 (#98FB98)
    ax.plot(filtered_df['연도'], filtered_df['최고기온(℃)'], label='최고기온', color='#B19CD9', linewidth=2, marker='o', markersize=4)
    ax.plot(filtered_df['연도'], filtered_df['최저기온(℃)'], label='최저기온', color='#98FB98', linewidth=2, marker='o', markersize=4)

    # 5. 그래프 제목 및 범례 설정 (제목: 월별 기온분석)
    ax.set_title("월별 기온분석", fontsize=16, pad=15)
    ax.legend(loc='upper right', fontsize=11)

    # 6. 축 레이블 설정 (가로축: 연도 / 세로축: 기온, 깨짐 방지를 위해 명확한 레이블 지정)
    ax.set_xlabel("Year (연도)", fontsize=12)
    ax.set_ylabel("Temperature (°C)", fontsize=12)

    # 그리드 추가 및 레이아웃 정리
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    # 스트림릿에 그래프 출력
    st.pyplot(fig)

    # 상세 데이터 확인용 테이블
    with st.expander("선택한 월의 상세 데이터 보기"):
        st.dataframe(filtered_df[['일시', '연도', '월', '최고기온(℃)', '최저기온(℃)', '평균기온(℃)']].reset_index(drop=True))

except FileNotFoundError:
    st.error("`temperature.csv` 파일을 찾을 수 없습니다. 리포지토리 폴더에 파일을 업로드했는지 확인해 주세요.")
