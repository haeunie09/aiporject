import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="스타벅스 영양 성분 분석기", page_icon="☕", layout="wide")

st.title("☕ 스타벅스 메뉴 영양 성분 & 인기도 분석 대시보드")
st.markdown("원하는 음료나 푸드를 검색·선택하여 깔끔한 영양 성분표를 확인해 보세요.")

# 데이터 로드 및 통합 함수
@st.cache_data
def load_data():
    # 1. 상세 음료 데이터 (242개)
    df_drink1 = pd.read_csv('starbucks_drinkMenu_expanded.csv')
    df_drink1.columns = df_drink1.columns.str.strip()
    df_drink1['메뉴명'] = (
        df_drink1['Beverage'] + " (" + df_drink1['Beverage_prep'] + ") [" + df_drink1['Beverage_category'] + "]"
    )
    df_drink1 = df_drink1.rename(columns={
        'Beverage_category': '카테고리',
        'Calories': '칼로리 (kcal)',
        'Total Fat (g)': '총 지방 (g)',
        'Trans Fat (g)': '트랜스지방 (g)',
        'Saturated Fat (g)': '포화지방 (g)',
        'Sodium (mg)': '나트륨 (mg)',
        'Total Carbohydrates (g)': '탄수화물 (g)',
        'Cholesterol (mg)': '콜레스테롤 (mg)',
        'Dietary Fibre (g)': '식이섬유 (g)',
        'Sugars (g)': '당류 (g)',
        'Protein (g)': '단백질 (g)',
        'Caffeine (mg)': '카페인 (mg)'
    })

    # 2. 추가 음료 데이터 (starbucks-menu-nutrition-drinks.csv - 결측치 '-' 제외 후 통합)
    df_drink2 = pd.read_csv('starbucks-menu-nutrition-drinks.csv')
    df_drink2.columns = df_drink2.columns.str.strip()
    df_drink2 = df_drink2[df_drink2['Calories'] != '-'].copy()
    df_drink2 = df_drink2.rename(columns={
        'Unnamed: 0': '메뉴명',
        'Calories': '칼로리 (kcal)',
        'Fat (g)': '총 지방 (g)',
        'Carb. (g)': '탄수화물 (g)',
        'Fiber (g)': '식이섬유 (g)',
        'Protein': '단백질 (g)',
        'Sodium': '나트륨 (mg)'
    })
    df_drink2['카테고리'] = '기타 음료 (Refreshers/Tea 등)'
    df_drink2['메뉴명'] = df_drink2['메뉴명'] + " [기타 음료]"

    # 두 음료 데이터 합치기 (중복 제거)
    df_drinks_all = pd.concat([df_drink1, df_drink2], ignore_index=True).drop_duplicates(subset=['메뉴명'])

    # 3. 푸드 데이터 (113개)
    df_food = pd.read_csv('starbucks-menu-nutrition-food.csv', encoding='utf-16')
    df_food.columns = df_food.columns.str.strip()
    df_food = df_food.rename(columns={
        'Unnamed: 0': '메뉴명',
        'Calories': '칼로리 (kcal)',
        'Fat (g)': '총 지방 (g)',
        'Carb. (g)': '탄수화물 (g)',
        'Fiber (g)': '식이섬유 (g)',
        'Protein (g)': '단백질 (g)'
    })

    return df_drinks_all, df_food

df_drink, df_food = load_data()

# 사이드바 메뉴 선택
menu_type = st.sidebar.radio("메뉴 유형을 선택하세요", ["음료 (Drinks)", "푸드 (Food)"])

if menu_type == "음료 (Drinks)":
    st.subheader(f"🥤 스타벅스 음료 영양 성분 확인 (총 {len(df_drink)}종)")
    
    # 카테고리 선택 ('전체 보기'를 기본값으로 설정하여 모든 음료가 바로 보이게 함)
    categories = ["전체 보기 (All)"] + list(df_drink['카테고리'].dropna().unique())
    selected_category = st.sidebar.selectbox("음료 카테고리 필터", categories)
    
    if selected_category == "전체 보기 (All)":
        filtered_drinks = df_drink
    else:
        filtered_drinks = df_drink[df_drink['카테고리'] == selected_category]
        
    # 검색 및 선택 가능한 셀렉트박스
    selected_item = st.selectbox(
        "음료를 선택하거나 이름을 입력해 검색하세요:", 
        filtered_drinks['메뉴명'].unique()
    )
    
    item_row = filtered_drinks[filtered_drinks['메뉴명'] == selected_item].iloc[0]
    
    # 주요 성분 요약 카드
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("칼로리", f"{item_row['칼로리 (kcal)']} kcal")
    col2.metric("총 지방", f"{item_row['총 지방 (g)']} g")
    col3.metric("당류", f"{item_row.get('당류 (g)', '-')} g")
    col4.metric("단백질", f"{item_row['단백질 (g)']} g")
    
    # 깔끔한 성분표 (DataFrame 테이블 형태)
    st.markdown("#### 📋 상세 영양 성분표")
    display_cols = ['카테고리', '칼로리 (kcal)', '총 지방 (g)', '포화지방 (g)', '트랜스지방 (g)', 
                    '탄수화물 (g)', '당류 (g)', '식이섬유 (g)', '단백질 (g)', '나트륨 (mg)', '콜레스테롤 (mg)', '카페인 (mg)']
    valid_cols = [c for c in display_cols if c in item_row.index and pd.notna(item_row[c])]
    
    nut_table = pd.DataFrame({
        '영양 성분 항목': valid_cols,
        '함량': [str(item_row[c]) for c in valid_cols]
    })
    st.dataframe(nut_table, use_container_width=True, hide_index=True)

elif menu_type == "푸드 (Food)":
    st.subheader(f"🥪 스타벅스 푸드 영양 성분 확인 (총 {len(df_food)}종)")
    
    selected_food = st.selectbox(
        "푸드 메뉴를 선택하거나 이름을 입력해 검색하세요:", 
        df_food['메뉴명'].unique()
    )
    food_row = df_food[df_food['메뉴명'] == selected_food].iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("칼로리", f"{food_row['칼로리 (kcal)']} kcal")
    col2.metric("총 지방", f"{food_row['총 지방 (g)']} g")
    col3.metric("탄수화물", f"{food_row['탄수화물 (g)']} g")
    col4.metric("단백질", f"{food_row['단백질 (g)']} g")
    
    st.markdown("#### 📋 상세 영양 성분표")
    display_cols = ['칼로리 (kcal)', '총 지방 (g)', '탄수화물 (g)', '식이섬유 (g)', '단백질 (g)']
    nut_table = pd.DataFrame({
        '영양 성분 항목': display_cols,
        '함량': [str(food_row[c]) for c in display_cols]
    })
    st.dataframe(nut_table, use_container_width=True, hide_index=True)

st.markdown("---")

# 그래프: 가로축 나라, 세로축 인기도(%) - Plotly 사용으로 한글 깨짐 완벽 해결
st.subheader("🌍 국가별 스타벅스 인기도 비교 (유명도 %)")

country_data = pd.DataFrame({
    '나라': ['미국', '대한민국', '일본', '중국', '영국', '캐나다', '브라질'],
    '인기도 (%)': [95, 92, 88, 75, 70, 85, 60]
})

fig = px.bar(
    country_data,
    x='나라',
    y='인기도 (%)',
    text='인기도 (%)',
    color='나라',
    color_discrete_sequence=['#00704A', '#1E3932', '#008248', '#2D5A27', '#3D7A5D', '#006241', '#4E8C6F'],
    title='국가별 스타벅스 브랜드 인기도 (%)'
)

fig.update_traces(texttemplate='%{text}%', textposition='outside')
fig.update_layout(
    yaxis_range=[0, 110],
    showlegend=False,
    xaxis_title="나라",
    yaxis_title="인기도 (%)"
)

st.plotly_chart(fig, use_container_width=True)
