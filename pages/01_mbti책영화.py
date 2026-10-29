import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="MBTI 맞춤 책 & 영화 추천! 🎬📚",
    page_icon="🍿",
    layout="centered"
)

# 메인 타이틀 & 소개
st.title("🍿 MBTI로 찾는 인생 책 & 영화 탐험!")
st.subheader("너의 MBTI에 딱 맞는 취향저격 작품을 확인해봐! ✨")
st.write("궁금한 MBTI 유형을 선택하면 너의 성향에 꼭 맞는 **추천 도서 2권**과 **추천 영화 2편**을 소개해줄게! 😉")

st.divider()

# MBTI 및 추천 도서/영화 데이터베이스 (기본 라이브러리 dict 구조)
mbti_recommendations = {
    "ISTJ": {
        "title": "원칙을 지키는 꼼꼼한 현실주의자 📐",
        "books": [
            {"title": "《아몬드》 (손원평)", "desc": "감정을 느끼지 못하는 소년의 철저한 관찰과 성장을 담은 몰입감 높은 소설!"},
            {"title": "《원씽(The One Thing)》 (게리 켈러)", "desc": "목표를 현실로 만드는 디테일하고 체계적인 원칙을 세워주는 책!"}
        ],
        "movies": [
            {"title": "🎬 셜록 홈즈 (Sherlock)", "desc": "치밀한 관찰력과 압도적인 논리로 사건을 깔끔하게 해결하는 쾌감!"},
            {"title": "🎬 파수꾼", "desc": "인물 간 관계와 감정의 변화를 차분하고 깊이 있게 추적하는 명작 영화!"}
        ]
    },
    "ISFJ": {
        "title": "성실하고
