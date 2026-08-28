import streamlit as st
import pandas as pd

# ────────────────────────────────────────────
# 페이지 기본 설정
# ────────────────────────────────────────────
st.set_page_config(
    page_title="서울 기온 랭킹",
    page_icon="🌡️",
    layout="centered"
)

# ────────────────────────────────────────────
# CSS 스타일
# ────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }

    .main-title {
        text-align: center;
        font-size: 2.6rem;
        font-weight: 900;
        background: linear-gradient(135deg, #FF6B6B, #FFA500, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    .sub-title {
        text-align: center;
        font-size: 1rem;
        color: #888;
        margin-bottom: 2rem;
    }

    .card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.08);
    }

    .rank-badge {
        text-align: center;
        font-size: 1rem;
        font-weight: 700;
        color: #aaa;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 0.3rem;
    }

    .rank-number {
        text-align: center;
        font-size: 5rem;
        font-weight: 900;
        line-height: 1;
    }

    .rank-total {
        text-align: center;
        font-size: 1.1rem;
        color: #aaa;
        margin-top: 0.3rem;
        margin-bottom: 1.2rem;
    }

    .temp-value {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 900;
    }

    .temp-label {
        text-align: center;
        font-size: 0.85rem;
        color: #aaa;
        margin-top: 0.2rem;
    }

    .percentile-bar-bg {
        background: rgba(255,255,255,0.1);
        border-radius: 50px;
        height: 14px;
        margin: 1.2rem 0 0.4rem 0;
        overflow: hidden;
    }

    .info-box {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1rem 1.4rem;
        margin-top: 1rem;
        font-size: 0.92rem;
        color: #ccc;
        line-height: 1.8;
    }

    .emoji-rank {
        font-size: 2rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    .divider {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.08);
        margin: 1.2rem 0;
    }

    .period-text {
        text-align: center;
        font-size: 1.05rem;
        color: #ddd;
        margin-bottom: 1.5rem;
        background: rgba(255,255,255,0.06);
        padding: 0.6rem 1rem;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────
# 데이터 로드
# ────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('seoul.csv', encoding='utf-8-sig')
    df.columns = df.columns.str.strip()
    df['날짜'] = df['날짜'].astype(str).str.strip()
    df = df[df['날짜'].str.match(r'^\d{4}-\d{2}-\d{2}$')]
    df['날짜'] = pd.to_datetime(df['날짜'])
    df = df.dropna(subset=['평균기온', '최고기온', '최저기온'])
    df['평균기온'] = pd.to_numeric(df['평균기온'], errors='coerce')
    df['최고기온'] = pd.to_numeric(df['최고기온'], errors='coerce')
    df['최저기온'] = pd.to_numeric(df['최저기온'], errors='coerce')
    df = df.dropna()
    return df

df = load_data()

# ────────────────────────────────────────────
# 유틸 함수
# ────────────────────────────────────────────
def get_rank_emoji(percentile_top):
    """상위 퍼센타일 기준 이모지 반환"""
    if percentile_top <= 1:
        return "🏆", "역대 최상위권"
    elif percentile_top <= 5:
        return "🥇", "TOP 5%"
    elif percentile_top <= 10:
        return "🥈", "TOP 10%"
    elif percentile_top <= 25:
        return "🥉", "TOP 25%"
    elif percentile_top <= 50:
        return "📊", "상위 절반"
    else:
        return "❄️", "하위권"

def get_temp_color(temp):
    """기온에 따른 색상 반환"""
    if temp >= 35:
        return "#FF2D2D"
    elif temp >= 30:
        return "#FF6B35"
    elif temp >= 25:
        return "#FFA500"
    elif temp >= 20:
        return "#FFD700"
    elif temp >= 10:
        return "#4FC3F7"
    elif temp >= 0:
        return "#29B6F6"
    else:
        return "#81D4FA"

def get_bar_color(temp):
    if temp >= 30:
        return "linear-gradient(90deg, #FF6B35, #FF2D2D)"
    elif temp >= 20:
        return "linear-gradient(90deg, #FFD700, #FFA500)"
    elif temp >= 10:
        return "linear-gradient(90deg, #4FC3F7, #0288D1)"
    else:
        return "linear-gradient(90deg, #81D4FA, #29B6F6)"

def compute_period_avg(df, start, end):
    """기간 평균 계산 및 전체 기간 대비 순위 반환"""
    mask = (df['날짜'] >= pd.Timestamp(start)) & (df['날짜'] <= pd.Timestamp(end))
    period_df = df[mask]
    if period_df.empty:
        return None

    # 같은 월-일 범위로 연도별 평균 계산 (역대 같은 시기 비교)
    all_months_days = period_df['날짜'].apply(lambda x: (x.month, x.day))
    month_day_list = list(set(all_months_days))

    yearly_avgs = []
    for year in df['날짜'].dt.year.unique():
        year_df = df[df['날짜'].dt.year == year]
        sub = year_df[year_df['날짜'].apply(lambda x: (x.month, x.day)).isin(month_day_list)]
        if not sub.empty:
            yearly_avgs.append({
                'year': year,
                '평균기온': sub['평균기온'].mean(),
                '최고기온': sub['최고기온'].mean(),
                '최저기온': sub['최저기온'].mean(),
            })

    yearly_df = pd.DataFrame(yearly_avgs).dropna()

    result = {}
    for col in ['평균기온', '최고기온', '최저기온']:
        my_val = period_df[col].mean()
        sorted_vals = yearly_df[col].sort_values(ascending=False).reset_index(drop=True)
        rank = (sorted_vals >= my_val).sum()
        total = len(sorted_vals)
        percentile_top = round(rank / total * 100, 1)
        result[col] = {
            'value': round(my_val, 1),
            'rank': int(rank),
            'total': int(total),
            'percentile_top': percentile_top,
            'all_values': sorted_vals.tolist()
        }

    result['days'] = len(period_df)
    result['start'] = start
    result['end'] = end
    return result

def render_rank_card(label, icon, data):
    val = data['value']
    rank = data['rank']
    total = data['total']
    pct = data['percentile_top']
    bar_width = max(2, round((1 - pct / 100) * 100))
    emoji, badge_text = get_rank_emoji(pct)
    color = get_temp_color(val)
    bar_color = get_bar_color(val)

    st.markdown(f"""
    <div class="card">
        <div class="rank-badge">{icon} {label}</div>
        <hr class="divider">
        <div class="emoji-rank">{emoji}</div>
        <div class="rank-number" style="color:{color};">#{rank}</div>
        <div class="rank-total">전체 {total}개 연도 중 · 상위 {pct}%</div>
        <div class="temp-value" style="color:{color};">{val}°C</div>
        <div class="temp-label">해당 기간 {label}</div>
        <div class="percentile-bar-bg">
            <div style="width:{bar_width}%; height:100%; background:{bar_color}; border-radius:50px; transition: width 1s ease;"></div>
        </div>
        <div style="text-align:center; font-size:0.82rem; color:#aaa;">← 낮음 &nbsp;&nbsp; 높음 →</div>
        <div class="info-box">
            🏷️ <b>{badge_text}</b> &nbsp;|&nbsp;
            📅 역대 같은 기간과 비교한 결과입니다.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ────────────────────────────────────────────
# UI 메인
# ────────────────────────────────────────────
st.markdown('<div class="main-title">🌡️ 서울 기온 랭킹</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">1907년부터 현재까지 · 서울 기상 관측 데이터 기반</div>', unsafe_allow_html=True)

min_date = df['날짜'].min().date()
max_date = df['날짜'].max().date()

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input(
        "📅 시작 날짜",
        value=pd.Timestamp("2024-07-01").date(),
        min_value=min_date,
        max_value=max_date
    )
with col2:
    end_date = st.date_input(
        "📅 종료 날짜",
        value=pd.Timestamp("2024-07-31").date(),
        min_value=min_date,
        max_value=max_date
    )

if start_date > end_date:
    st.error("⚠️ 시작 날짜가 종료 날짜보다 늦습니다. 다시 선택해주세요.")
    st.stop()

days_diff = (end_date - start_date).days + 1

st.markdown(f"""
<div class="period-text">
    📆 <b>{start_date.strftime('%Y년 %m월 %d일')}</b> 부터
    <b>{end_date.strftime('%Y년 %m월 %d일')}</b> 까지 &nbsp;·&nbsp; 총 <b>{days_diff}일</b>
</div>
""", unsafe_allow_html=True)

if st.button("🔍 순위 분석하기", use_container_width=True, type="primary"):
    with st.spinner("📊 역대 데이터와 비교 중..."):
        result = compute_period_avg(df, start_date, end_date)

    if result is None:
        st.error("❌ 해당 기간의 데이터가 없습니다.")
    else:
        st.success(f"✅ 분석 완료! 총 {result['days']}일 데이터 기준")

        render_rank_card("평균기온", "🌡️", result['평균기온'])
        render_rank_card("최고기온", "🔥", result['최고기온'])
        render_rank_card("최저기온", "❄️", result['최저기온'])

        with st.expander("📖 분석 방법 보기"):
            st.markdown("""
            - **비교 방식**: 선택한 기간의 **월-일 범위**를 기준으로, 1907년부터 현재까지 **같은 시기 연도별 평균**과 비교합니다.
            - 예: 7월 1일~7월 31일을 선택하면, 역대 모든 연도의 7월 평균기온과 비교합니다.
            - **순위 1위** = 역대 가장 높은 기온을 기록한 해
            - 데이터 출처: 기상청 서울(지점 108) 일별 관측 자료
            """)

# 하단 정보
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#555; font-size:0.8rem;'>📡 기상청 서울 관측소 (지점 108) · 1907–현재 · Made with Streamlit</div>",
    unsafe_allow_html=True
)
