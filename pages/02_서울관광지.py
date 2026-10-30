import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="서울 Top 10 관광지 & 1박 2일 일정",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# 2. 관광지 데이터 정의
@st.cache_data
def get_tour_data():
    data = [
        {
            "day": "1일차",
            "name": "경복궁",
            "category": "역사/문화",
            "lat": 37.5796,
            "lon": 126.9770,
            "time": "09:00 - 11:00",
            "description": "조선 왕조의 대표 궁궐이자 한복 체험의 명소",
        },
        {
            "day": "1일차",
            "name": "북촌 한옥마을",
            "category": "역사/문화",
            "lat": 37.5826,
            "lon": 126.9831,
            "time": "12:00 - 13:30",
            "description": "전통 한옥이 잘 보존된 도심 속 한옥 주거지",
        },
        {
            "day": "1일차",
            "name": "인사동",
            "category": "역사/문화",
            "lat": 37.5716,
            "lon": 126.9860,
            "time": "13:30 - 15:00",
            "description": "전통 공예품과 찻집 및 골동품 거리가 형성된 거리",
        },
        {
            "day": "1일차",
            "name": "명동 쇼핑거리",
            "category": "쇼핑/푸드",
            "lat": 37.5629,
            "lon": 126.9858,
            "time": "15:00 - 17:00",
            "description": "K-뷰티 쇼핑과 다양한 길거리 음식을 즐길 수 있는 거리",
        },
        {
            "day": "2일차",
            "name": "홍대 거리",
            "category": "쇼핑/푸드",
            "lat": 37.5563,
            "lon": 126.9237,
            "time": "09:00 - 11:30",
            "description": "젊음과 버스킹 공연 및 유니크한 카페 문화의 중심지",
        },
        {
            "day": "2일차",
            "name": "동대문 디자인 플라자 (DDP)",
            "category": "쇼핑/푸드",
            "lat": 37.5665,
            "lon": 127.0092,
            "time": "13:00 - 15:00",
            "description": "세계적인 곡선 건축물과 야경이 아름다운 디자인 거점",
        },
        {
            "day": "2일차",
            "name": "이태원 & 해방촌",
            "category": "쇼핑/푸드",
            "lat": 37.5345,
            "lon": 126.9939,
            "time": "15:00 - 17:00",
            "description": "다채로운 글로벌 문화와 다국적 음식을 즐길 수 있는 지구",
        },
        {
            "day": "2일차",
            "name": "N서울타워",
            "category": "야경/전망",
            "lat": 37.5512,
            "lon": 126.9882,
            "time": "17:00 - 19:00",
            "description": "남산 정상에서 서울 시내 전체를 조망할 수 있는 랜드마크",
        },
        {
            "day": "추가 추천",
            "name": "롯데월드 타워 & 석촌호수",
            "category": "야경/전망",
            "lat": 37.5126,
            "lon": 127.1025,
            "time": "자율 탐방",
            "description": "123층 높이의 전망대와 석촌호수가 어우러진 명소",
        },
        {
            "day": "추가 추천",
            "name": "반포 한강공원",
            "category": "자연/휴식",
            "lat": 37.5103,
            "lon": 126.9960,
            "time": "자율 탐방",
            "description": "달빛무지개분수와 한강 피크닉을 즐기기 좋은 수변 공원",
        },
    ]
    return pd.DataFrame(data)


df_spots = get_tour_data()

# 3. 사이드바 구성
st.sidebar.title("🔍 관광지 필터")
st.sidebar.markdown("외국인이 사랑하는 **서울 주요 관광지 Top 10**")

day_filter = st.sidebar.selectbox("일정 선택", ["전체", "1일차", "2일차"])

if day_filter != "전체":
    filtered_df = df_spots[df_spots["day"] == day_filter]
else:
    filtered_df = df_spots.copy()

selected_spot_name = st.sidebar.radio(
    "📍 명소 상세보기", ["전체 보기"] + list(filtered_df["name"])
)

# 4. 메인 헤더 및 지도 출력
st.title("🇰🇷 서울 주요 관광지 지도 & 1박 2일 추천 코스")
st.markdown("지도의 마커를 클릭하여 명소 설명을 확인할 수 있습니다.")

if selected_spot_name != "전체 보기":
    spot_info = filtered_df[filtered_df["name"] == selected_spot_name].iloc[0]
    map_center = [spot_info["lat"], spot_info["lon"]]
    zoom_level = 15
else:
    map_center = [37.5550, 126.9800]
    zoom_level = 12

m = folium.Map(
    location=map_center, zoom_start=zoom_level, tiles="OpenStreetMap"
)

for _, row in filtered_df.iterrows():
    color = "red" if selected_spot_name == row["name"] else "blue"
    popup_html = f"""
    <div style="width: 200px;">
        <h4 style="margin-bottom: 5px;"><b>{row['name']}</b></h4>
        <p style="margin: 0; font-size: 12px; color: #666;"><b>일정:</b> {row['day']} ({row['time']})</p>
        <p style="margin-top: 5px; font-size: 13px;">{row['description']}</p>
    </div>
    """
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=row["name"],
        icon=folium.Icon(color=color, icon="info-sign"),
    ).add_to(m)

st_folium(m, width="100%", height=500)

st.divider()

# 5. 지도 하단 일목요연 일정표
st.subheader("🗓️ 1박 2일 추천 일정표 (09:00 - 19:00)")

tab1, tab2 = st.tabs(["📅 1일차 코스 (역사/도심)", "📅 2일차 코스 (문화/전망)"])

with tab1:
    day1_schedule = [
        {
            "시간": "09:00 - 11:00",
            "구분": "관광",
            "장소/내용": "경복궁",
            "비고": "조선 궁궐 관람 및 한복 체험",
        },
        {
            "시간": "11:00 - 12:00",
            "구분": "점심",
            "장소/내용": "토속촌 삼계탕",
            "비고": "진한 국물의 보양 삼계탕",
        },
        {
            "시간": "12:00 - 13:30",
            "구분": "관광",
            "장소/내용": "북촌 한옥마을",
            "비고": "전통 한옥 골목길 산책",
        },
        {
            "시간": "13:30 - 15:00",
            "구분": "관광",
            "장소/내용": "인사동",
            "비고": "전통 공예품 및 전통찻집",
        },
        {
            "시간": "15:00 - 17:00",
            "구분": "관광",
            "장소/내용": "명동 쇼핑거리",
            "비고": "K-뷰티 쇼핑 및 길거리 음식",
        },
        {
            "시간": "17:00 - 19:00",
            "구분": "저녁",
            "장소/내용": "명동교자 본점",
            "비고": "미쉐린 가이드 칼국수 명가",
        },
        {
            "시간": "숙박",
            "구분": "호텔",
            "장소/내용": "웨스틴 조선 서울",
            "비고": "명동/시청 인근 위치 우수 5성급 Hotel",
        },
    ]
    st.dataframe(pd.DataFrame(day1_schedule), use_container_width=True)

with tab2:
    day2_schedule = [
        {
            "시간": "09:00 - 11:30",
            "구분": "관광",
            "장소/내용": "홍대 거리",
            "비고": "버스킹, 카페 문화 감상",
        },
        {
            "시간": "11:30 - 13:00",
            "구분": "점심",
            "장소/내용": "우래옥",
            "비고": "전통 평양냉면 대표 맛집",
        },
        {
            "시간": "13:00 - 15:00",
            "구분": "관광",
            "장소/내용": "동대문 디자인 플라자 (DDP)",
            "비고": "곡선 건축물 감상 및 전시",
        },
        {
            "시간": "15:00 - 17:00",
            "구분": "관광",
            "장소/내용": "이태원 & 해방촌",
            "비고": "다문화 거리 및 경리단길 탐방",
        },
        {
            "시간": "17:00 - 19:00",
            "구분": "관광/저녁",
            "장소/내용": "N서울타워 & 엔그릴",
            "비고": "서울 도심 전경 감상 및 식사",
        },
    ]
    st.dataframe(pd.DataFrame(day2_schedule), use_container_width=True)
