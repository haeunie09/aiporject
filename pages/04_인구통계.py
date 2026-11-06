import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.font_manager as fm
import os
import platform
import urllib.request

st.set_page_config(
    page_title="서울시 인구 통계 분석",
    page_icon="📊",
    layout="wide"
)

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

selected
