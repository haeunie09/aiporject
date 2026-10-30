import os
import pandas as pd
import pydeck as pdk
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="서울 Top 10 관광지 지도",
    page_icon="🗽",
    layout="wide",
    initial_sidebar_state="expanded",
)


# 2. 데이터 자동 생성 함수 (외부 CSV 없이 코드 내부에서 생성)
@st.cache_data
def get_tour_data():
    data = [
        {
            "name": "경복궁",
            "category": "역사/문화",
            "lat": 37.5796,
            "lon": 126.9770,
            "description": "조선 왕조의 대표 궁궐이자 한복 체험의 명소",
        },
        {
            "name": "N서울타워",
            "category": "야경/전망",
            "lat": 37.5512,
            "lon": 126.9882,
            "description": "남산 정상에서 서울 시내 전체를 조망할 수 있는 랜드마크",
        },
        {
            "name": "명동 쇼핑거리",
            "category": "쇼핑/푸드",
            "lat": 37.5629,
            "lon": 126.9858,
            "description": "K-뷰티 쇼핑과 다양한 길거리 음식을 즐길 수 있는 거리",
        },
        {
            "name": "북촌 한옥마을",
            "category": "역사/문화",
            "lat": 37.5826,
            "lon": 126.9831,
            "description": "전통 한옥이 잘 보존된 도심 속 한옥 주거지",
        },
        {
            "name": "인사동",
            "category": "역사/문화",
            "lat": 37.5716,
            "lon": 126.9860,
            "description": "전통 공예품과 찻집 및 골동품 거리가 형성된 전통 문화의 거리",
        },
        {
            "name": "홍대 거리",
            "category": "쇼핑/푸드",
            "lat": 37.5563,
            "lon": 126.9237,
            "description": "젊음과 버스킹 공연 및 유니크한 카페 문화의 중심지",
        },
        {
            "name": "동대문 디자인 플라자 (DDP)",
            "category": "쇼핑/푸드",
            "lat": 37.5665,
            "lon": 127.0092,
            "description": "세계적인 곡선 건축물과 야경이 아름다운 디자인 거점",
        },
        {
            "name": "이태원 & 해방촌",
            "category": "쇼핑/푸드",
            "lat": 37.5345,
            "lon": 126.9939,
            "description": "다채로운 글로벌 문화와 다국적 음식을 즐길 수 있는 지구",
        },
        {
            "name": "롯데월드 타워 & 석촌호수",
            "category": "야경/전망",
            "lat": 37.5126,
            "lon": 127.1025,
            "description": "123층 높이의 전망대와 아름다운 석촌호수가 어우러진 명소",
        },
        {
            "name": "반포 한강공원",
            "category": "자연/휴식",
            "lat": 37.5103,
            "lon": 126.9960,
            "description": "달빛무지개분수와 한강 라면 및 피크닉을 즐기기 좋은 수변 공원",
        },
    ]
    return pd.DataFrame(data)


df_spots = get_tour_data()

# 3. 사이드바 구성
st.sidebar.title("🔍 관광지 필터")
st.sidebar.markdown("외국인 관광객이 사랑하는 **서울 대표 관광지 Top 10**입니다.")

categories = ["전체"] + list(df_spots["category"].unique())
selected_category = st.sidebar.selectbox("카테고리 선택", categories)

if selected_category != "전체":
    filtered_df = df_spots[df_spots["category"] == selected_category]
else:
    filtered_df = df_spots.copy()

selected_spot_name = st.sidebar.radio(
    "📍 명소 상세보기",
    ["전체 보기"] + list(filtered_df["name"]),
)

# 4. 메인 화면
st.title("🇰🇷 외국인이 좋아하는 서울 주요 관광지 Top 10")
st.markdown("지도의 **핀을 클릭**하면 해당 명소의 정보를 확인할 수 있습니다.")
st.divider()

# 5. 지도 위치 및 줌 설정
if selected_spot_name != "전체 보기":
    spot_info = filtered_df[filtered_df["name"] == selected_spot_name].iloc[0]
    view_state = pdk.ViewState(
        latitude=spot_info["lat"],
        longitude=spot_info["lon"],
        zoom=14,
        pitch=45,
    )
    map_data = filtered_df[filtered_df["name"] == selected_spot_name]
else:
    view_state = pdk.ViewState(
        latitude=37.5550,
        longitude=126.9800,
        zoom=11.2,
        pitch=30,
    )
    map_data = filtered_df

# 6. 지도 레이어 정의
layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_data,
    get_position=["lon", "lat"],
    get_color="[235, 64, 52, 200]",
    get_radius=200,
    radius_scale=1,
    radius_min_pixels=8,
    radius_max_pixels=20,
    pickable=True,
)

r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={
        "html": "<b>{name}</b><br/><i>{category}</i><br/>{description}",
        "style": {
            "backgroundColor": "navy",
            "color": "white",
            "fontSize": "14px",
            "padding": "10px",
            "borderRadius": "5px",
        },
    },
)

st.pydeck_chart(r)

# 7. 하단 상세 정보
st.divider()
st.subheader("📋 관광지 목록 상세")

col1, col2 = st.columns([1, 1])

with col1:
    st.dataframe(
        filtered_df[["name", "category", "description"]],
        column_config={
            "name": "관광지명",
            "category": "카테고리",
            "description": "설명",
        },
        use_container_width=True,
        hide_index=True,
    )

with col2:
    if selected_spot_name != "전체 보기":
        selected_row = filtered_df[
            filtered_df["name"] == selected_spot_name
        ].iloc[0]
        st.info(
            f"### 📍 {selected_row['name']}\n\n"
            f"- **분류:** {selected_row['category']}\n"
            f"- **위도/경도:** `{selected_row['lat']}, {selected_row['lon']}`\n\n"
            f"{selected_row['description']}"
        )
    else:
        st.success(
            "왼쪽 사이드바에서 특정 관광지를 선택하시면 해당 위치로 지도가 이동합니다!"
        )
