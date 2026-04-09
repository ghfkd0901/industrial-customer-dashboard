import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import html

# ─────────────────────────────────────────
# 1. 페이지 설정 및 전역 스타일
# ─────────────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="산업용 고객 통합 관리 시스템",
    page_icon="🏭",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700&display=swap');

* { font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif !important; }

.main { background-color: #f4f6fb; }
[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e5e9f0;
}
[data-testid="stSidebar"] .stSelectbox label { font-size: 13px; color: #5f6368; }

/* ── 섹션 헤더 ── */
.sec-hdr {
    display: flex; align-items: center; gap: 10px;
    margin: 1.8rem 0 1rem;
}
.sec-hdr-icon {
    width: 30px; height: 30px; border-radius: 8px;
    background: #1a73e8; display: flex; align-items: center;
    justify-content: center; font-size: 14px; flex-shrink: 0;
}
.sec-hdr-text { font-size: 14px; font-weight: 700; color: #1a1a2e; }
.sec-hdr-line { flex: 1; height: 1px; background: #e5e9f0; }

/* ── 고객 타이틀 ── */
.cust-title {
    display: flex; align-items: center; gap: 12px;
    padding: 1rem 0 0.2rem;
}
.cust-name { font-size: 24px; font-weight: 800; color: #1a1a2e; }
.cust-badge {
    font-size: 11px; font-weight: 700; letter-spacing: .04em;
    background: #e8f0fe; color: #1558d0;
    padding: 4px 12px; border-radius: 20px;
}

/* ── 기본정보 카드 ── */
.info-card {
    background: #ffffff; border: 1px solid #e5e9f0;
    border-radius: 12px; overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,.04);
}
.info-row {
    display: flex; align-items: stretch;
    border-bottom: 1px solid #f0f3f8;
}
.info-row:last-child { border-bottom: none; }
.info-label {
    width: 130px; flex-shrink: 0;
    background: #f8f9fc; color: #5f6368;
    font-size: 12px; font-weight: 600;
    padding: 10px 14px; display: flex; align-items: center;
    border-right: 1px solid #f0f3f8;
}
.info-value {
    flex: 1; color: #1a1a2e; font-size: 13px;
    padding: 10px 14px; display: flex; align-items: center;
}

/* ── KPI 카드 ── */
.kpi-row { display: flex; gap: 12px; margin-bottom: 16px; }
.kpi-card {
    flex: 1; background: #ffffff; border: 1px solid #e5e9f0;
    border-radius: 12px; padding: 16px 18px;
    position: relative; overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,.04);
}
.kpi-card::after {
    content: ''; position: absolute;
    bottom: 0; left: 0; right: 0; height: 3px;
    background: #1a73e8;
}
.kpi-card.green::after { background: #0f9d58; }
.kpi-card.amber::after { background: #f9ab00; }
.kpi-card.red::after   { background: #ea4335; }
.kpi-label { font-size: 11px; color: #80868b; font-weight: 600;
    letter-spacing: .05em; text-transform: uppercase; margin-bottom: 8px; }
.kpi-value { font-size: 22px; font-weight: 800; color: #1a1a2e; }
.kpi-value.green { color: #0f9d58; }
.kpi-value.red   { color: #ea4335; }

/* ── PSM 카드 ── */
.psm-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
.psm-card {
    background: #ffffff; border: 1px solid #e5e9f0;
    border-radius: 12px; padding: 16px 18px;
    position: relative; overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,.04);
}
.psm-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 3px; border-radius: 12px 12px 0 0;
}
.psm-card.psm-blue::before   { background: #1a73e8; }
.psm-card.psm-danger::before { background: #ea4335; }
.psm-card.psm-warn::before   { background: #f9ab00; }
.psm-card.psm-safe::before   { background: #0f9d58; }
.psm-label { font-size: 11px; color: #80868b; font-weight: 600;
    letter-spacing: .04em; margin-bottom: 8px; }
.psm-val { font-size: 20px; font-weight: 800; color: #1a1a2e; margin-bottom: 6px; }
.psm-badge {
    display: inline-block; font-size: 11px; font-weight: 700;
    padding: 3px 10px; border-radius: 20px;
}
.psm-badge.b-danger { background: #fce8e6; color: #c5221f; }
.psm-badge.b-safe   { background: #e6f4ea; color: #137333; }
.psm-badge.b-warn   { background: #fef7e0; color: #b06000; }

/* ── 타임라인 ── */
.tl-wrap { padding: 4px 0; }
.tl-item { display: flex; gap: 14px; padding-bottom: 24px; position: relative; }
.tl-item:not(:last-child)::before {
    content: ''; position: absolute; left: 10px; top: 24px; bottom: 0;
    width: 1.5px; background: #e5e9f0;
}
.tl-dot {
    width: 22px; height: 22px; border-radius: 50%;
    flex-shrink: 0; margin-top: 1px; position: relative; z-index: 1;
}
.tl-dot.recent { background: #e8f0fe; border: 2px solid #1a73e8; }
.tl-dot.recent::after {
    content: ''; position: absolute; top: 50%; left: 50%;
    transform: translate(-50%,-50%);
    width: 8px; height: 8px; border-radius: 50%; background: #1a73e8;
}
.tl-dot.old { background: #f8f9fa; border: 2px solid #dadce0; }
.tl-dot.old::after {
    content: ''; position: absolute; top: 50%; left: 50%;
    transform: translate(-50%,-50%);
    width: 8px; height: 8px; border-radius: 50%; background: #bdc1c6;
}
.tl-body { flex: 1; }
.tl-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }
.tl-date { font-size: 13px; font-weight: 700; color: #3c4043; }
.tl-manager {
    font-size: 11.5px; color: #5f6368;
    background: #f1f3f4; padding: 2px 10px; border-radius: 99px;
}
.tl-badge-new {
    font-size: 10px; font-weight: 700; letter-spacing: .05em;
    background: #e8f0fe; color: #1558d0; padding: 2px 8px; border-radius: 4px;
}
.tl-box {
    background: #ffffff; border: 1px solid #e5e9f0;
    border-radius: 10px; padding: 12px 16px;
    font-size: 13.5px; color: #1a1a2e; line-height: 1.75;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
}

/* ── 판매량 차트 라벨 ── */
.chart-lbl { font-size: 13px; font-weight: 600; color: #5f6368; margin-bottom: 4px; }

/* ── 구분선 ── */
.divider { border: none; border-top: 1px solid #e5e9f0; margin: 0.5rem 0 1.2rem; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# 2. 데이터 로드
# ─────────────────────────────────────────
@st.cache_data
def load_all_data():
    base_path      = r'D:\Project\산업용관리대쉬보드\data'
    sale_file      = os.path.join(base_path, '산업용_통합데이터_정리완료.csv')
    interview_file = os.path.join(base_path, '면담내용.xlsx')

    sale_df = pd.read_csv(sale_file, encoding='utf-8-sig')
    sale_df['매출년월'] = pd.to_datetime(sale_df['매출년월'], errors='coerce')
    sale_df = sale_df.dropna(subset=['매출년월']).sort_values('매출년월')
    sale_df['고객명'] = sale_df['고객명'].astype(str).str.strip()

    interview_df = pd.read_excel(interview_file, header=0)
    interview_df.columns = [str(c).strip() for c in interview_df.columns]
    expected = ['수요처', '날짜', '면담 내용']
    if not all(c in interview_df.columns for c in expected):
        rename_map = {interview_df.columns[i]: expected[i]
                      for i in range(min(3, len(interview_df.columns)))}
        interview_df = interview_df.rename(columns=rename_map)
    interview_df['날짜'] = pd.to_datetime(interview_df['날짜'], errors='coerce')
    interview_df = interview_df.dropna(subset=['날짜']).sort_values('날짜', ascending=False)
    interview_df['수요처'] = interview_df['수요처'].astype(str).str.strip()

    return sale_df, interview_df


PSM_SHEET_URL = "https://docs.google.com/spreadsheets/d/1ZwuT0NihpFzE-AxnKocIKN-DbZd-Q5fqbIvvhx6AJJg/edit?usp=sharing"

@st.cache_data(ttl=600)
def load_psm_data(sheet_url: str) -> pd.DataFrame:
    try:
        sheet_id = sheet_url.split("/d/")[1].split("/")[0]
        csv_url  = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        df = pd.read_csv(csv_url)
        df.columns = df.columns.str.strip()

        if '사용량구분' in df.columns:
            df = df[df['사용량구분'] == '산업용']
        elif '사용량 구분' in df.columns:
            df = df[df['사용량 구분'] == '산업용']
        if '사용중구분' in df.columns:
            df = df[df['사용중구분'] == '사용중']

        if '설치일자' in df.columns:
            df['설치일자_str'] = df['설치일자'].fillna(0).astype(str).str.split('.').str[0]
            df['설치일자_dt']  = pd.to_datetime(df['설치일자_str'], format='%Y%m%d', errors='coerce')

        heat_col = ('연소기열량' if '연소기열량' in df.columns
                    else '연소기 열량' if '연소기 열량' in df.columns else None)
        if heat_col:
            df['연소기열량_num'] = pd.to_numeric(df[heat_col], errors='coerce').fillna(0)
            df.rename(columns={heat_col: '연소기열량_원본'}, inplace=True)

        if '고객명' in df.columns:
            df['고객명'] = df['고객명'].astype(str).str.strip()
        return df
    except Exception:
        return pd.DataFrame()


# ─────────────────────────────────────────
# 헬퍼
# ─────────────────────────────────────────
def section_header(icon: str, title: str):
    st.markdown(
        f'<div class="sec-hdr">'
        f'<div class="sec-hdr-icon">{icon}</div>'
        f'<span class="sec-hdr-text">{title}</span>'
        f'<div class="sec-hdr-line"></div></div>',
        unsafe_allow_html=True,
    )

def clean_name(s: str) -> str:
    return (s.replace('주식회사', '').replace('(주)', '')
             .replace('㈜', '').replace('(유)', '')
             .replace('유한회사', '').strip())


# ─────────────────────────────────────────
# 3. 앱 메인
# ─────────────────────────────────────────
try:
    sale_df, interview_df = load_all_data()
    psm_raw = load_psm_data(PSM_SHEET_URL)
    load_ok = True
except Exception as e:
    st.error(f"데이터 로드 오류: {e}")
    load_ok = False

if load_ok:
    # ── 고객별 총 사용량 (사이드바 정렬용) ──
    customer_total = (
        sale_df.groupby('고객명')['사용량(m3)'].sum()
        .reset_index().rename(columns={'사용량(m3)': '총사용량'})
    )

    with st.sidebar:
        st.markdown("### 🔍 고객 검색")

        # 업종 필터 (업종분류 아닌 업종 열 사용)
        biz_options = sorted(sale_df['업종'].dropna().unique().tolist())
        sel_biz = st.selectbox(
            "업종 선택",
            options=["전체"] + biz_options,
            index=0,
            key="sel_biz",
        )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # 업종 필터 적용 후 판매량 내림차순
        if sel_biz == "전체":
            filtered_sale = sale_df
        else:
            filtered_sale = sale_df[sale_df['업종'] == sel_biz]

        filtered_customers = (
            filtered_sale.groupby('고객명')['사용량(m3)'].sum()
            .reset_index()
            .sort_values('사용량(m3)', ascending=False)['고객명']
            .tolist()
        )

        if not filtered_customers:
            st.warning("해당 업종에 고객이 없습니다.")
            selected_customer = None
        else:
            selected_customer = st.selectbox(
                "관리 업체 선택",
                options=filtered_customers,
                label_visibility="collapsed",
                key="sel_customer",
            )

    if selected_customer:
        cust_sale = sale_df[sale_df['고객명'] == selected_customer].copy()

        match_key = clean_name(selected_customer)
        if len(match_key) < 3:
            match_key = selected_customer

        cust_interview = interview_df[
            interview_df['수요처'].apply(clean_name)
            .str.contains(match_key, na=False, regex=False)
        ].copy()

        # ── 고객 타이틀 ──
        st.markdown(
            f'<div class="cust-title">'
            f'<span class="cust-name">🏭 {html.escape(selected_customer)}</span>'
            f'<span class="cust-badge">산업용</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<hr class="divider">', unsafe_allow_html=True)


        # ══════════════════════════════════════
        # SECTION 1: 기본 정보
        # ══════════════════════════════════════
        section_header("📋", "기본 정보")

        if not cust_sale.empty:
            usage_str = ' / '.join(str(v) for v in cust_sale['용도'].dropna().unique())
            biz_str   = ' / '.join(str(v) for v in cust_sale['업종분류'].dropna().unique())
            ind_str   = ' / '.join(str(v) for v in cust_sale['업종'].dropna().unique())
            addr_row  = cust_sale.dropna(subset=['도로명주소']).iloc[0] if '도로명주소' in cust_sale.columns else None
            road_addr = str(addr_row['도로명주소']) if addr_row is not None else '-'
            jibun_addr= str(addr_row['지번주소']) if addr_row is not None and '지번주소' in cust_sale.columns else '-'

            cur_year  = int(cust_sale['매출년월'].dt.year.max())
            total_cur = cust_sale[cust_sale['매출년월'].dt.year == cur_year]['사용량(m3)'].sum()
            total_all = cust_sale['사용량(m3)'].sum()

            # KPI 행
            st.markdown(f"""
            <div class="kpi-row">
                <div class="kpi-card">
                    <div class="kpi-label">용도</div>
                    <div class="kpi-value" style="font-size:16px;">{html.escape(usage_str)}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">업종 분류</div>
                    <div class="kpi-value" style="font-size:16px;">{html.escape(biz_str)}</div>
                </div>
                <div class="kpi-card green">
                    <div class="kpi-label">{cur_year}년 누적 사용량</div>
                    <div class="kpi-value green">{total_cur:,.0f} <span style="font-size:13px;font-weight:500;">m³</span></div>
                </div>
                <div class="kpi-card amber">
                    <div class="kpi-label">전체 누적 사용량</div>
                    <div class="kpi-value" style="font-size:18px;">{total_all:,.0f} <span style="font-size:13px;font-weight:500;">m³</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 상세 테이블
            st.markdown(f"""
            <div class="info-card">
                <div class="info-row">
                    <div class="info-label">📍 도로명주소</div>
                    <div class="info-value">{html.escape(road_addr)}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">🗺️ 지번주소</div>
                    <div class="info-value">{html.escape(jibun_addr)}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">🏭 세부업종</div>
                    <div class="info-value">{html.escape(ind_str)}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("기본 정보 데이터가 없습니다.")


        # ══════════════════════════════════════
        # SECTION 2: 연소기 정보
        # ══════════════════════════════════════
        section_header("🔥", "연소기 정보")

        if psm_raw.empty:
            st.warning("PSM 데이터를 불러오지 못했습니다.")
        else:
            cust_psm = psm_raw[
                psm_raw['고객명'].apply(clean_name)
                .str.contains(match_key, na=False, regex=False)
            ].copy()

            if cust_psm.empty:
                st.info("해당 고객의 연소기 데이터가 없습니다.")
            else:
                n_burner = len(cust_psm)
                n_meter  = cust_psm['계량기번호'].nunique() if '계량기번호' in cust_psm.columns else '-'
                total_heat = cust_psm['연소기열량_num'].sum() if '연소기열량_num' in cust_psm.columns else 0

                st.markdown(f"""
                <div class="kpi-row">
                    <div class="kpi-card">
                        <div class="kpi-label">연소기 수</div>
                        <div class="kpi-value">{n_burner} <span style="font-size:14px;font-weight:500;">대</span></div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">계량기 수</div>
                        <div class="kpi-value">{n_meter} <span style="font-size:14px;font-weight:500;">대</span></div>
                    </div>
                    <div class="kpi-card amber">
                        <div class="kpi-label">총 열량 (kcal/h)</div>
                        <div class="kpi-value" style="font-size:18px;">{total_heat:,.0f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── 연소기 테이블: 토글 가능한 expander ──
                def clean_str(v):
                    s = str(v).strip()
                    return '' if s in ('None', 'nan', 'NaN', 'none', 'NaT') else s

                def fmt_date_str(v):
                    try:
                        if pd.isna(v): return ''
                        return pd.Timestamp(v).strftime('%Y-%m-%d')
                    except Exception:
                        return ''

                # 정제 + 컬럼 선택
                burner_sorted = cust_psm.copy()
                if '연소기열량_num' in burner_sorted.columns:
                    burner_sorted = burner_sorted.sort_values('연소기열량_num', ascending=False).reset_index(drop=True)

                disp_df = pd.DataFrame()
                disp_df['연소기명']     = burner_sorted.get('연소기명', pd.Series([''] * len(burner_sorted))).apply(clean_str)
                disp_df['모델명']       = burner_sorted.get('모델명',   pd.Series([''] * len(burner_sorted))).apply(clean_str)
                disp_df['열량(kcal/h)'] = burner_sorted.get('연소기열량_num', pd.Series([0] * len(burner_sorted)))
                if '계량기번호' in burner_sorted.columns:
                    disp_df['계량기번호'] = burner_sorted['계량기번호'].apply(clean_str)
                if '설치일자_dt' in burner_sorted.columns:
                    disp_df['설치일자'] = burner_sorted['설치일자_dt'].apply(fmt_date_str)

                col_cfg = {
                    '열량(kcal/h)': st.column_config.NumberColumn('열량 (kcal/h)', format="%,.0f"),
                }

                # 토글 버튼 (session_state)
                burner_key = f"burner_open_{selected_customer}"
                if burner_key not in st.session_state:
                    st.session_state[burner_key] = True

                btn_label = f"{'▲ 접기' if st.session_state[burner_key] else f'▼ 연소기 목록 {len(disp_df)}대 보기'}"
                if st.button(btn_label, key=f"btn_{burner_key}", use_container_width=False):
                    st.session_state[burner_key] = not st.session_state[burner_key]
                    st.rerun()

                if st.session_state[burner_key]:
                    st.dataframe(
                        disp_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config=col_cfg,
                        height=min(36 * len(disp_df) + 38, 420),
                    )


        # ══════════════════════════════════════
        # SECTION 3: PSM 현황
        # ══════════════════════════════════════
        section_header("⚖️", "PSM 현황")

        if psm_raw.empty:
            st.warning("PSM 데이터를 불러오지 못했습니다.")
        else:
            cust_psm2 = psm_raw[
                psm_raw['고객명'].apply(clean_name)
                .str.contains(match_key, na=False, regex=False)
            ].copy()

            if cust_psm2.empty or '연소기열량_num' not in cust_psm2.columns:
                st.info("해당 고객의 PSM 분석 데이터가 없습니다.")
            else:
                total_heat = cust_psm2['연소기열량_num'].sum()
                daily_heat = total_heat * 24
                lng_kg     = (daily_heat / 9190) * 0.78
                lpg_kg     = daily_heat / 11040
                lng_r      = lng_kg / 50000
                lpg_r      = lpg_kg / 5000

                def r_cls(r):
                    if r >= 1.0:   return "psm-danger"
                    elif r >= 0.7: return "psm-warn"
                    return "psm-safe"

                def psm_badge_html(is_psm, r):
                    if is_psm:
                        return '<span class="psm-badge b-danger">⚠ PSM 대상</span>'
                    elif r >= 0.7:
                        return '<span class="psm-badge b-warn">△ 주의</span>'
                    return '<span class="psm-badge b-safe">✓ 비대상</span>'

                lng_psm = lng_r >= 1.0
                lpg_psm = lpg_r >= 1.0

                st.markdown(f"""
                <div class="psm-grid">
                    <div class="psm-card {r_cls(lng_r)}">
                        <div class="psm-label">LNG R값</div>
                        <div class="psm-val">{lng_r:.4f}</div>
                        {psm_badge_html(lng_psm, lng_r)}
                    </div>
                    <div class="psm-card {r_cls(lpg_r)}">
                        <div class="psm-label">LPG R값</div>
                        <div class="psm-val">{lpg_r:.4f}</div>
                        {psm_badge_html(lpg_psm, lpg_r)}
                    </div>
                    <div class="psm-card psm-blue">
                        <div class="psm-label">일일 총 열량 (Mcal)</div>
                        <div class="psm-val" style="font-size:16px;">{daily_heat/1000:,.1f}</div>
                    </div>
                    <div class="psm-card psm-blue">
                        <div class="psm-label">LNG 환산 (kg/일)</div>
                        <div class="psm-val" style="font-size:16px;">{lng_kg:,.1f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.caption("R값 기준 — LNG 기준량: 50,000 kg/일 · LPG 기준량: 5,000 kg/일 | R ≥ 1.0 → PSM 대상 / R ≥ 0.7 → 주의")


        # ══════════════════════════════════════
        # SECTION 4: 판매량 분석
        # ══════════════════════════════════════
        section_header("📊", "판매량 분석")

        if not cust_sale.empty:
            annual = (
                cust_sale
                .assign(연도=cust_sale['매출년월'].dt.year)
                .groupby('연도', as_index=False)[['사용량(m3)', '사용량(mj)']].sum()
            )
            year_list = sorted(annual['연도'].unique(), reverse=True)  # 최신순

            # 멀티셀렉트 — 기본값: 최근 3개 연도
            default_years = year_list[:min(3, len(year_list))]
            sel_years = st.multiselect(
                "📆 조회 연도 선택 (복수 선택 가능)",
                options=year_list,
                default=default_years,
                key="sel_years_multi",
                format_func=lambda y: f"{y}년",
            )
            if not sel_years:
                st.info("연도를 하나 이상 선택해주세요.")
            else:
                sel_years_sorted = sorted(sel_years)  # 오름차순 정렬 (차트용)

                col_left, col_right = st.columns(2)

                # ── 좌: 연간 바차트 (선택된 연도 강조) ──
                with col_left:
                    st.markdown('<p class="chart-lbl">연간 사용량 (m³)</p>', unsafe_allow_html=True)
                    bar_colors = [
                        '#1a73e8' if int(y) in sel_years_sorted else '#c9d8f8'
                        for y in annual['연도']
                    ]
                    fig_a = go.Figure(go.Bar(
                        x=annual['연도'].astype(str),
                        y=annual['사용량(m3)'],
                        marker_color=bar_colors,
                        marker_line_width=0,
                        width=0.5,
                        text=[f"{v:,.0f}" if int(y) in sel_years_sorted else ""
                              for y, v in zip(annual['연도'], annual['사용량(m3)'])],
                        textposition='outside',
                        textfont=dict(size=10, color='#3c4043'),
                        hovertemplate='%{x}년<br>%{y:,.0f} m³<extra></extra>',
                    ))
                    fig_a.update_layout(
                        height=300, margin=dict(t=20, b=8, l=0, r=8),
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=False, bargap=0.4,
                        yaxis=dict(showgrid=True, gridcolor='#f0f2f4', tickformat=',.0f',
                                   zeroline=False, title=None, tickfont=dict(size=10)),
                        xaxis=dict(title=None, tickfont=dict(size=11), fixedrange=True),
                    )
                    st.plotly_chart(fig_a, use_container_width=True, config={'displayModeBar': False})

                # ── 우: 월별 꺾은선 (선택된 연도 각각 한 선) ──
                with col_right:
                    years_label = ' · '.join(f"{y}년" for y in sel_years_sorted)
                    st.markdown(f'<p class="chart-lbl">월별 사용량 (m³) — {years_label}</p>', unsafe_allow_html=True)

                    # 연도별 색상 팔레트 (최대 10개 연도 지원)
                    PALETTE = [
                        '#1a73e8', '#0f9d58', '#f9ab00', '#ea4335',
                        '#9334e6', '#00897b', '#e65100', '#1565c0',
                        '#558b2f', '#6d4c41',
                    ]
                    full_months = pd.DataFrame({'월': range(1, 13)})
                    fig_m = go.Figure()

                    for i, yr in enumerate(sel_years_sorted):
                        color = PALETTE[i % len(PALETTE)]
                        is_latest = (yr == max(sel_years_sorted))
                        monthly = (
                            cust_sale[cust_sale['매출년월'].dt.year == yr]
                            .assign(월=lambda d: d['매출년월'].dt.month)
                            .groupby('월', as_index=False)['사용량(m3)'].sum()
                        )
                        monthly = full_months.merge(monthly, on='월', how='left').fillna(0)

                        fig_m.add_trace(go.Scatter(
                            x=monthly['월'],
                            y=monthly['사용량(m3)'],
                            name=f'{yr}년',
                            mode='lines+markers',
                            line=dict(
                                color=color,
                                width=2.5 if is_latest else 1.8,
                                dash='solid' if is_latest else 'dot',
                            ),
                            marker=dict(
                                size=7 if is_latest else 5,
                                color=color,
                                line=dict(color='#ffffff', width=1.5),
                            ),
                            fill='tozeroy' if is_latest else 'none',
                            fillcolor=f'rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.06)' if is_latest else None,
                            hovertemplate=f'%{{x}}월 · {yr}년<br>%{{y:,.0f}} m³<extra></extra>',
                        ))

                    fig_m.update_layout(
                        height=300, margin=dict(t=20, b=8, l=0, r=8),
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        hovermode='x unified',
                        legend=dict(orientation='h', yanchor='bottom', y=1.02,
                                    xanchor='right', x=1, font=dict(size=11)),
                        yaxis=dict(showgrid=True, gridcolor='#f0f2f4', tickformat=',.0f',
                                   zeroline=False, title=None, tickfont=dict(size=10)),
                        xaxis=dict(title=None, fixedrange=True,
                                   tickmode='array', tickvals=list(range(1, 13)),
                                   ticktext=[f'{m}월' for m in range(1, 13)],
                                   tickfont=dict(size=10)),
                    )
                    st.plotly_chart(fig_m, use_container_width=True, config={'displayModeBar': False})

                with st.expander("📋 상세 데이터"):
                    t_a, t_m = st.tabs(["연간", "월간"])
                    with t_a:
                        st.dataframe(
                            annual.rename(columns={'연도': '연도', '사용량(m3)': '사용량 (m³)', '사용량(mj)': '사용량 (MJ)'})
                            .sort_values('연도', ascending=False),
                            use_container_width=True, hide_index=True,
                        )
                    with t_m:
                        # 선택 연도 전체 월별 데이터 합쳐서 표시
                        all_monthly = []
                        for yr in sel_years_sorted:
                            m_df = (
                                cust_sale[cust_sale['매출년월'].dt.year == yr]
                                .assign(월=lambda d: d['매출년월'].dt.month)
                                .groupby('월', as_index=False)[['사용량(m3)', '사용량(mj)']].sum()
                            )
                            m_df = full_months.merge(m_df, on='월', how='left').fillna(0)
                            m_df.insert(0, '연도', yr)
                            all_monthly.append(m_df)
                        disp_m = pd.concat(all_monthly, ignore_index=True)
                        disp_m['월'] = disp_m['월'].astype(int).astype(str) + '월'
                        st.dataframe(
                            disp_m.rename(columns={'사용량(m3)': '사용량 (m³)', '사용량(mj)': '사용량 (MJ)'}),
                            use_container_width=True, hide_index=True,
                        )
        else:
            st.info("판매량 데이터가 없습니다.")


        # ══════════════════════════════════════
        # SECTION 5: 상담 · 면담 이력 (토글)
        # ══════════════════════════════════════
        section_header("📝", "상담 · 면담 이력")

        if cust_interview.empty:
            st.info("등록된 상담 이력이 없습니다.")
        else:
            def render_interview_item(i: int, row):
                """st.expander 안팎 모두 안전한 순수 텍스트 렌더링"""
                date_str    = row['날짜'].strftime('%Y-%m-%d')
                content_str = str(row.get('면담 내용', '') or '').strip()

                manager_str = ''
                if '담당자' in cust_interview.columns:
                    raw = str(row.get('담당자', '')).strip()
                    if raw not in ('nan', '', 'None'):
                        manager_str = f'  |  👤 {raw}'

                recent_tag = '  |  🔵 최근' if i == 0 else ''

                # 마크다운 bold/특수기호 일절 사용 안 함 — plain write
                st.write(f"📅 {date_str}{manager_str}{recent_tag}")
                st.write(content_str if content_str else '(내용 없음)')
                st.write('')  # 여백

            # 최근 1건 항상 표시
            render_interview_item(0, cust_interview.iloc[0])

            # 나머지 — session_state 버튼 토글 (expander 미사용)
            rest = cust_interview.iloc[1:]
            if not rest.empty:
                itv_key = f"itv_open_{selected_customer}"
                if itv_key not in st.session_state:
                    st.session_state[itv_key] = False

                itv_btn_label = f"{'▲ 접기' if st.session_state[itv_key] else f'▼ 이전 이력 {len(rest)}건 더 보기'}"
                if st.button(itv_btn_label, key=f"btn_{itv_key}"):
                    st.session_state[itv_key] = not st.session_state[itv_key]
                    st.rerun()

                if st.session_state[itv_key]:
                    for idx, (_, row) in enumerate(rest.iterrows(), start=1):
                        render_interview_item(idx, row)
                        if idx < len(rest):
                            st.markdown("---")