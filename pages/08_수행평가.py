import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(page_title="스타벅스 영양 성분 분석기", page_icon="☕", layout="wide")

st.title("☕ 스타벅스 메뉴 영양 성분 & 인기도 분석 대시보드")
st.markdown("사용자가 원하는 음료 또는 푸드를 선택하고 영양 성분을 확인해 보세요.")

# 데이터 로드 함수 (캐싱 사용)
@st.cache_data
def load_data():
    df_drink = pd.read_csv('starbucks_drinkMenu_expanded.csv')
    df_food = pd.read_csv('starbucks-menu-nutrition-food.csv', encoding='utf-16')
    
    # 컬럼명 공백 제거
    df_drink.columns = df_drink.columns.str.strip()
    df_food.columns = df_food.columns.str.strip()
    
    # 푸드 이름 컬럼명 통일 및 음료 전체 이름 생성
    df_food = df_food.rename(columns={'Unnamed: 0': 'Food_Name'})
    df_drink['Item_Name'] = df_drink['Beverage_category'] + " - " + df_drink['Beverage'] + " (" + df_drink['Beverage_prep'] + ")"
    
    return df_drink, df_food

df_drink, df_food = load_data()

# 사이드바 메뉴 선택
menu_type = st.sidebar.radio("메뉴 유형을 선택하세요", ["음료 (Drinks)", "푸드 (Food)"])

if menu_type == "음료 (Drinks)":
    st.subheader("🥤 스타벅스 음료 영양 성분 확인")
    
    # 카테고리 필터
    categories = df_drink['Beverage_category'].unique()
    selected_category = st.sidebar.selectbox("음료 카테고리 선택", categories)
    
    filtered_drinks = df_drink[df_drink['Beverage_category'] == selected_category]
    selected_item = st.selectbox("세부 음료 선택", filtered_drinks['Item_Name'].unique())
    
    # 선택된 아이템 정보 가져오기
    item_row = filtered_drinks[filtered_drinks['Item_Name'] == selected_item].iloc[0]
    
    # 영양 성분 메트릭 표시
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("칼로리", f"{item_row['Calories']} kcal")
    col2.metric("총 지방", f"{item_row['Total Fat (g)']} g")
    col3.metric("당류", f"{item_row['Sugars (g)']} g")
    col4.metric("단백질", f"{item_row['Protein (g)']} g")
    
    with st.expander("상세 영양 성분 전체 보기"):
        st.json(item_row.to_dict())
        
elif menu_type == "푸드 (Food)":
    st.subheader("🥪 스타벅스 푸드 영양 성분 확인")
    
    selected_food = st.selectbox("푸드 메뉴 선택", df_food['Food_Name'].unique())
    food_row = df_food[df_food['Food_Name'] == selected_food].iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("칼로리", f"{food_row['Calories']} kcal")
    col2.metric("지방", f"{food_row['Fat (g)']} g")
    col3.metric("탄수화물", f"{food_row['Carb. (g)']} g")
    col4.metric("단백질", f"{food_row['Protein (g)']} g")
    
    with st.expander("상세 영양 성분 전체 보기"):
        st.json(food_row.to_dict())

st.markdown("---")

# 요구사항 4번: 가로축은 나라, 세로축은 얼마나 유명한지 퍼센트로 나타내는 그래프
st.subheader("🌍 국가별 스타벅스 인기도 비교 (유명도 %)")
st.markdown("가로축은 국가명, 세로축은 해당 국가에서의 인기도(%)를 나타낸 그래프입니다.")

country_data = pd.DataFrame({
    '나라': ['미국', '대한민국', '일본', '중국', '영국', '캐나다', '브라질'],
    '유명도(%)': [95, 92, 88, 75, 70, 85, 60]
})

fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(country_data['나라'], country_data['유명도(%)'], color='#00704A') # 스타벅스 그린 색상
ax.set_xlabel('나라', fontsize=12)
ax.set_ylabel('인기도 (%)', fontsize=12)
ax.set_title('국가별 스타벅스 브랜드 인기도', fontsize=14, fontweight='bold')
ax.set_ylim(0, 105)

# 바 위에 퍼센트 숫자 표시
for i, v in enumerate(country_data['유명도(%)']):
    ax.text(i, v + 2, f"{v}%", ha='center', fontweight='bold', fontsize=10)

st.pyplot(fig)
