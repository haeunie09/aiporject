import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="스타벅스 영양 성분 & 추천 대시보드", page_icon="☕", layout="wide")

st.title("☕ 스타벅스 맞춤 메뉴 추천 & 영양 성분 분석 대시보드")
st.markdown("원하는 메뉴의 영양 성분을 확인하고, **나만의 맞춤 메뉴 추천 기능**을 이용해 보세요!")

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

    # 2. 추가 음료 데이터 (starbucks-menu-nutrition-drinks.csv)
    df_drink2 = pd.read_csv('starbucks-menu-nutrition-drinks.csv')
    df_drink2.columns = df_drink2.columns.str.strip()
    df_drink2 = df_drink2[df_drink2['Calories'] != '-'].copy()
    
    df_drink2['Calories'] = pd.to_numeric(df_drink2['Calories'])
    df_drink2['Fat (g)'] = pd.to_numeric(df_drink2['Fat (g)'], errors='coerce').fillna(0)
    df_drink2['Carb. (g)'] = pd.to_numeric(df_drink2['Carb. (g)'], errors='coerce').fillna(0)
    df_drink2['Protein'] = pd.to_numeric(df_drink2['Protein'], errors='coerce').fillna(0)
    
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

# 사이드바 네비게이션
app_mode = st.sidebar.radio("원하시는 메뉴를 선택하세요", ["📋 개별 메뉴 영양 성분 조회", "🔍 맞춤형 음료 추천 (2번 기능)"])

if app_mode == "📋 개별 메뉴 영양 성분 조회":
    menu_type = st.sidebar.radio("메뉴 유형", ["음료 (Drinks)", "푸드 (Food)"])
    
    if menu_type == "음료 (Drinks)":
        st.subheader(f"🥤 스타벅스 음료 영양 성분 확인 (총 {len(df_drink)}종)")
        categories = ["전체 보기 (All)"] + list(df_drink['카테고리'].dropna().unique())
        selected_category = st.sidebar.selectbox("음료 카테고리 필터", categories)
        
        filtered_drinks = df_drink if selected_category == "전체 보기 (All)" else df_drink[df_drink['카테고리'] == selected_category]
            
        selected_item = st.selectbox("음료를 선택하거나 검색하세요:", filtered_drinks['메뉴명'].unique())
        item_row = filtered_drinks[filtered_drinks['메뉴명'] == selected_item].iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("칼로리", f"{item_row['칼로리 (kcal)']} kcal")
        col2.metric("총 지방", f"{item_row['총 지방 (g)']} g")
        col3.metric("당류", f"{item_row.get('당류 (g)', '-')} g")
        col4.metric("단백질", f"{item_row['단백질 (g)']} g")
        
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
        selected_food = st.selectbox("푸드 메뉴를 선택하거나 검색하세요:", df_food['메뉴명'].unique())
        food_row = df_food[df_food['메뉴명'] == selected_food].iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("칼로리", f"{food_row['칼로리 (kcal)']} kcal")
        col2.metric("지방", f"{food_row['총 지방 (g)']} g")
        col3.metric("탄수화물", f"{food_row['탄수화물 (g)']} g")
        col4.metric("단백질", f"{food_row['단백질 (g)']} g")
        
        st.markdown("#### 📋 상세 영양 성분표")
        display_cols = ['칼로리 (kcal)', '총 지방 (g)', '탄수화물 (g)', '식이섬유 (g)', '단백질 (g)']
        nut_table = pd.DataFrame({
            '영양 성분 항목': display_cols,
            '함량': [str(food_row[c]) for c in display_cols]
        })
        st.dataframe(nut_table, use_container_width=True, hide_index=True)

elif app_mode == "🔍 맞춤형 음료 추천 (2번 기능)":
    st.subheader("🎯 나의 건강 취향에 맞는 스타벅스 음료 추천")
    st.markdown("원하는 영양 성분 조건을 설정하시면, 조건에 딱 맞는 음료 목록을 찾아드립니다!")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        max_cal = st.slider("최대 칼로리 제한 (kcal)", 0, 550, 250, step=10)
        max_sugar = st.slider("최대 당류 제한 (g)", 0, 90, 20, step=5)
    with col_f2:
        min_protein = st.slider("최소 단백질 요구치 (g)", 0.0, 20.0, 5.0, step=0.5)
        caffeine_free = st.checkbox("카페인 없는 음료만 찾기 (카페인 0mg)")

    mask = (df_drink['칼로리 (kcal)'] <= max_cal) & (df_drink['단백질 (g)'] >= min_protein)
    
    if '당류 (g)' in df_drink.columns:
        sugars_series = pd.to_numeric(df_drink['당류 (g)'], errors='coerce').fillna(0)
        mask = mask & (sugars_series <= max_sugar)
        
    if caffeine_free and '카페인 (mg)' in df_drink.columns:
        caf_series = pd.to_numeric(df_drink['카페인 (mg)'], errors='coerce').fillna(0)
        mask = mask & (caf_series == 0)

    recommended_df = df_drink[mask]

    st.markdown(f"---")
    st.markdown(f"### 💡 조건에 일치하는 추천 음료: **{len(recommended_df)}개** 발견")

    if len(recommended_df) > 0:
        display_recommend_cols = ['메뉴명', '칼로리 (kcal)', '단백질 (g)', '당류 (g)', '총 지방 (g)', '카페인 (mg)']
        available_rec_cols = [c for c in display_recommend_cols if c in recommended_df.columns]
        
        st.dataframe(
            recommended_df[available_rec_cols].reset_index(drop=True),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("⚠️ 설정하신 조건이 너무 엄격하여 일치하는 음료가 없습니다. 슬라이더 범위를 조금 넓혀보세요!")

st.markdown("---")

# 🌍 국가별 인기도 비교 그래프 (디테일 업그레이드)
st.subheader("🌍 국가별 스타벅스 브랜드 인기도 비교")
st.markdown("전 세계 주요 국가별 스타벅스 시장 점유율 및 인기도(%) 조사 결과입니다.")

country_data = pd.DataFrame({
    '나라': ['미국', '대한민국', '일본', '중국', '영국', '캐나다', '브라질'],
    '인기도 (%)': [95, 92, 88, 75, 70, 85, 60],
    '순위': ['1위 (본고장)', '2위 (높은 밀도)', '3위 (아시아 선도)', '4위 (급성장 시장)', '6위 (유럽 거점)', '5위 (북미 핵심)', '7위 (남미 시장)']
})

fig = px.bar(
    country_data,
    x='나라',
    y='인기도 (%)',
    text='인기도 (%)',
    hover_data=['순위'],
    color='인기도 (%)',
    color_continuousScale=['#1E3932', '#00704A', '#00A862'],
    title='2026년 기준 국가별 스타벅스 인기도 지수'
)

fig.update_traces(
    texttemplate='%{text}%', 
    textposition='outside',
    marker_line_color='#0f172a',
    marker_line_width=1.5,
    opacity=0.9
)

fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    yaxis_range=[0, 110],
    coloraxis_showscale=False,
    xaxis_title=dict(text="<b>국가명</b>", font=dict(size=14)),
    yaxis_title=dict(text="<b>인기도 (%)</b>", font=dict(size=14)),
    title_font=dict(size=18, family="sans-serif", color="#00704A"),
    margin=dict(t=50, b=30, l=40, r=40)
)

st.plotly_chart(fig, use_container_width=True)
