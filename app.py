import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 페이지 기본 설정
st.set_page_config(
    page_title="스터디카페 & 도서관 잔여 좌석 찾기",
    page_icon="📚",
    layout="wide"
)

# 타이틀
st.title("📚 내 주변 스터디카페 & 도서관 실시간 잔여 좌석")
st.markdown("지도를 통해 주변 학습 공간의 남은 자리를 실시간으로 확인해 보세요!")

# 1. 사이드바 - 필터 설정
st.sidebar.header("🔍 검색 및 필터")
facility_type = st.sidebar.selectbox(
    "시설 유형 선택",
    ["전체", "스터디카페", "공공도서관"]
)

only_available = st.sidebar.checkbox("잔여 좌석 있는 곳만 보기", value=False)

# 2. 임시 데이터 (실제 서비스에서는 공공 API나 백엔드 DB에서 가져올 데이터)
data = pd.DataFrame([
    {
        "name": "공부선생 스터디카페 창원점",
        "type": "스터디카페",
        "lat": 35.2285,
        "lon": 128.6811,
        "total_seats": 80,
        "remaining_seats": 15,
        "address": "경상남도 창원시 성산구 중앙동"
    },
    {
        "name": "창원시립도서관 열람실",
        "type": "공공도서관",
        "lat": 35.2322,
        "lon": 128.6901,
        "total_seats": 150,
        "remaining_seats": 42,
        "address": "경상남도 창원시 성산구 용호동"
    },
    {
        "name": "작심스터디카페 상남점",
        "type": "스터디카페",
        "lat": 35.2241,
        "lon": 128.6825,
        "total_seats": 60,
        "remaining_seats": 0,
        "address": "경상남도 창원시 성산구 상남동"
    }
])

# 필터 적용
filtered_data = data.copy()
if facility_type != "전체":
    filtered_data = filtered_data[filtered_data["type"] == facility_type]
if only_available:
    filtered_data = filtered_data[filtered_data["remaining_seats"] > 0]

# 3. 지도 중심 설정 (창원시청 부근 기준)
m = folium.Map(location=[35.2279, 128.6819], zoom_start=14)

# 지도에 마커 추가
for idx, row in filtered_data.iterrows():
    # 잔여 좌석에 따른 색상 및 텍스트 분기
    if row["remaining_seats"] > 0:
        color = "green"
        status_text = f"잔여 좌석: **{row['remaining_seats']}석** / 전체 {row['total_seats']}석"
    else:
        color = "red"
        status_text = "**만석**"

    popup_html = f"""
    <div style="width:200px">
        <h4>{row['name']}</h4>
        <p><b>유형:</b> {row['type']}</p>
        <p>{status_text}</p>
        <p><small>{row['address']}</small></p>
    </div>
    """
    
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=row["name"],
        icon=folium.Icon(color=color, icon="info-sign")
    ).add_to(m)

# 4. 화면 레이아웃 구성 (좌: 지도, 우: 상세 리스트)
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗺️ 실시간 지도")
    st_folium(m, width="100%", height=500)

with col2:
    st.subheader("📋 시설 목록 및 실시간 현황")
    for idx, row in filtered_data.iterrows():
        with st.container():
            st.markdown(f"### **{row['name']}**")
            st.text(f"유형: {row['type']}")
            
            # 잔여 좌석 시각화 (프로그레스 바)
            percent = row["remaining_seats"] / row["total_seats"] if row["total_seats"] > 0 else 0
            st.progress(percent, text=f"남은 자리: {row['remaining_seats']}석 / 총 {row['total_seats']}석")
            st.divider()