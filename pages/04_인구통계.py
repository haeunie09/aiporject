```python
# Let's double check the exact code using python syntax parser to be 100% sure it compiles.
import ast

code = """import streamlit as st
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
st.write("행정구 복수 비교 및 특정 연령대별 최다 거주 지역 분석 기능을 제공합니다.")

st.sidebar.header("⚙️ 분석 조건 선택")

region_list = [r for r in df['지역명'].tolist() if r != '서울시']
selected_regions = st.sidebar.multiselect("행정구 선택 (복수 선택 가능)", region_list, default=[region_list[0]])

selected_year = st.sidebar.slider("연도 선택", min_value=2020, max_value=2025, value=2024)

age_brackets = [
    '0~9세', '10~19세', '20~29세', '30~39세', '40~49세',
    '50~59세', '60~69세', '70~79세', '80~89세', '90~99세', '100세 이상'
]

x_labels = ['0~10' if age == '0~9세' else ('100+' if '100' in age else age.replace('세', '')) for age in age_brackets]

st.subheader(f"📈 [{selected_year}년] 선택 자치구 성별 연령별 인구 비교")

if not selected_regions:
    st.warning("비교할 행정구를 최소 1개 이상 선택해주세요.")
else:
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for region in selected_regions:
        region_row = df[df['지역명'] == region].iloc[0]
        
        female_cols = [f"{selected_year}년_여_거주자_{age}" for age in age_brackets]
        female_vals = [region_row[col] for col in female_cols]
        
        male_cols = [f"{selected_year}년_남_거주자_{age}" for age in age_brackets]
        male_vals = [region_row[col] for col in male_cols]
        
        ax.plot(
            x_labels, female_vals, 
            color="#FFB6C1", marker='o', linewidth=2.5, markersize=6, 
            label=f"{region} (여성)"
        )
        ax.plot(
            x_labels, male_vals, 
            color="#87CEEB", marker='s', linewidth=2.5, markersize=6, linestyle='--',
            label=f"{region} (남성)"
        )

    ax.grid(True, which='both', axis='both', linestyle='--', alpha=0.5)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(50000))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))

    ax.set_xlabel("나이 (연령대)", fontsize=12, labelpad=10)
    ax.set_ylabel("인\\n구\\n수", fontsize=12, labelpad=10, rotation=0, va='center')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    st.pyplot(fig)

st.divider()
st.subheader("🏆 특정 연령대 인구 상위 자치구 순위")
st.write("특정 연령대(10살 단위)를 선택하면 해당 연령 인구가 가장 많은 자치구들(서울시 제외)을 막대 그래프로 확인할 수 있습니다.")

col1, col2 = st.sidebar.columns(2)
with col1:
    selected_age_idx = st.selectbox("연령대 선택", range(len(age_brackets)), format_func=lambda x: x_labels[x])
with col2:
    top_n = st.slider("표시할 구 개수", min_value=5, max_value=25, value=10)

target_col_name = f"{selected_year}년_거주자_{age_brackets[selected_age_idx]}"
target_age_label = x_labels[selected_age_idx]

sub_df = df[df['지역명'] != '서울시']
ranked_df = sub_df[['지역명', target_col_name]].sort_values(by=target_col_name, ascending=False).head(top_n)

fig2, ax2 = plt.subplots(figsize=(12, 5))
bars = ax2.bar(ranked_df['지역명'], ranked_df[target_col_name], color='#87CEEB', edgecolor='#4682B4')

ax2.grid(True, which='both', axis='y', linestyle='--', alpha=0.5)
ax2.yaxis.set_major_locator(ticker.MultipleLocator(20000))
ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))

ax2.set_xlabel("행정구", fontsize=12, labelpad=10)
ax2.set_ylabel("인\\n구\\n수", fontsize=12, labelpad=10, rotation=0, va='center')
ax2.set_title(f"[{selected_year}년] {target_age_label}세 연령대 인구 상위 자치구", fontsize=14, pad=15, fontweight='bold')

for bar in bars:
    height = bar.get_height()
    ax2.annotate(f'{height:,}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),  
                textcoords="offset points",
                ha='center', va='bottom', fontsize=8)

plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig2)

st.subheader("📋 선택된 자치구별 데이터 요약")
summary_data = {}
for region in selected_regions:
    region_row = df[df['지역명'] == region].iloc[0]
    total_vals = [region_row[f"{selected_year}년_거주자_{age}"] for age in age_brackets]
    summary_data[f"{region} (전체)"] = [f"{val:,}" for val in total_vals]

summary_df = pd.DataFrame(summary_data, index=age_brackets)
st.dataframe(summary_df)
"""

try:
    ast.parse(code)
    print("Parsed OK")
except SyntaxError as e:
    print(e)


```

```text
Parsed OK


```

```python
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
st.write("행정구 복수 비교 및 특정 연령대별 최다 거주 지역 분석 기능을 제공합니다.")

st.sidebar.header("⚙️ 분석 조건 선택")

region_list = [r for r in df['지역명'].tolist() if r != '서울시']
selected_regions = st.sidebar.multiselect("행정구 선택 (복수 선택 가능)", region_list, default=[region_list[0]])

selected_year = st.sidebar.slider("연도 선택", min_value=2020, max_value=2025, value=2024)

age_brackets = [
    '0~9세', '10~19세', '20~29세', '30~39세', '40~49세',
    '50~59세', '60~69세', '70~79세', '80~89세', '90~99세', '100세 이상'
]

x_labels = ['0~10' if age == '0~9세' else ('100+' if '100' in age else age.replace('세', '')) for age in age_brackets]

st.subheader(f"📈 [{selected_year}년] 선택 자치구 성별 연령별 인구 비교")

if not selected_regions:
    st.warning("비교할 행정구를 최소 1개 이상 선택해주세요.")
else:
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for region in selected_regions:
        region_row = df[df['지역명'] == region].iloc[0]
        
        female_cols = [f"{selected_year}년_여_거주자_{age}" for age in age_brackets]
        female_vals = [region_row[col] for col in female_cols]
        
        male_cols = [f"{selected_year}년_남_거주자_{age}" for age in age_brackets]
        male_vals = [region_row[col] for col in male_cols]
        
        ax.plot(
            x_labels, female_vals, 
            color="#FFB6C1", marker='o', linewidth=2.5, markersize=6, 
            label=f"{region} (여성)"
        )
        ax.plot(
            x_labels, male_vals, 
            color="#87CEEB", marker='s', linewidth=2.5, markersize=6, linestyle='--',
            label=f"{region} (남성)"
        )

    ax.grid(True, which='both', axis='both', linestyle='--', alpha=0.5)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(50000))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))

    ax.set_xlabel("나이 (연령대)", fontsize=12, labelpad=10)
    ax.set_ylabel("인\n구\n수", fontsize=12, labelpad=10, rotation=0, va='center')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    st.pyplot(fig)

st.divider()
st.subheader("🏆 특정 연령대 인구 상위 자치구 순위")
st.write("특정 연령대(10살 단위)를 선택하면 해당 연령 인구가 가장 많은 자치구들(서울시 제외)을 막대 그래프로 확인할 수 있습니다.")

col1, col2 = st.sidebar.columns(2)
with col1:
    selected_age_idx = st.selectbox("연령대 선택", range(len(age_brackets)), format_func=lambda x: x_labels[x])
with col2:
    top_n = st.slider("표시할 구 개수", min_value=5, max_value=25, value=10)

target_col_name = f"{selected_year}년_거주자_{age_brackets[selected_age_idx]}"
target_age_label = x_labels[selected_age_idx]

sub_df = df[df['지역명'] != '서울시']
ranked_df = sub_df[['지역명', target_col_name]].sort_values(by=target_col_name, ascending=False).head(top_n)

fig2, ax2 = plt.subplots(figsize=(12, 5))
bars = ax2.bar(ranked_df['지역명'], ranked_df[target_col_name], color='#87CEEB', edgecolor='#4682B4')

ax2.grid(True, which='both', axis='y', linestyle='--', alpha=0.5)
ax2.yaxis.set_major_locator(ticker.MultipleLocator(20000))
ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))

ax2.set_xlabel("행정구", fontsize=12, labelpad=10)
ax2.set_ylabel("인\n구\n수", fontsize=12, labelpad=10, rotation=0, va='center')
ax2.set_title(f"[{selected_year}년] {target_age_label}세 연령대 인구 상위 자치구", fontsize=14, pad=15, fontweight='bold')

for bar in bars:
    height = bar.get_height()
    ax2.annotate(f'{height:,}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),  
                textcoords="offset points",
                ha='center', va='bottom', fontsize=8)

plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig2)

st.subheader("📋 선택된 자치구별 데이터 요약")
summary_data = {}
for region in selected_regions:
    region_row = df[df['지역명'] == region].iloc[0]
    total_vals = [region_row[f"{selected_year}년_거주자_{age}"] for age in age_brackets]
    summary_data[f"{region} (전체)"] = [f"{val:,}" for val in total_vals]

summary_df = pd.DataFrame(summary_data, index=age_brackets)
st.dataframe(summary_df)

```
