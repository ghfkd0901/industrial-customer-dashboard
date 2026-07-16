import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import html
from supabase_utils import load_sales_for_app

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

/* Streamlit 내장 아이콘(expander 화살표 등)은 전용 폰트 유지해야 글자로 안 깨짐 */
[data-testid="stIconMaterial"],
span[class*="material-symbols"] {
    font-family: 'Material Symbols Rounded' !important;
}

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

/* ── 2x2 그리드 카드 헤더 ── */
.quad-hdr {
    font-size: 14px; font-weight: 700; color: #1a1a2e;
    margin-bottom: 10px; padding-bottom: 8px;
    border-bottom: 1px solid #f0f3f8;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# 2. 데이터 로드
# ─────────────────────────────────────────
@st.cache_data(ttl=600)   # 10분마다 새로고침 (Supabase에 새로 입력된 데이터 반영되도록)
def load_all_data():
    base_path      = os.path.join(os.getcwd(), 'data')  # streamlit을 프로젝트 루트에서 실행하는 한 pages/ 안에서도 항상 정확함
    interview_file = os.path.join(base_path, '면담내용.xlsx')

    # 판매량: Supabase 로드 + 한글 컬럼 매핑까지 supabase_utils.py가 전담
    sale_df = load_sales_for_app()

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
def section_header(icon: str, title: str, link_url: str = None, link_label: str = "원본 시트 열기"):
    if link_url:
        col_title, col_link = st.columns([5, 1])
        with col_title:
            st.markdown(
                f'<div class="sec-hdr">'
                f'<div class="sec-hdr-icon">{icon}</div>'
                f'<span class="sec-hdr-text">{title}</span>'
                f'<div class="sec-hdr-line"></div></div>',
                unsafe_allow_html=True,
            )
        with col_link:
            st.link_button(f"🔗 {link_label}", link_url, use_container_width=True)
    else:
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

        # ── 공통 헬퍼 (분기별로 재사용) ──
        def clean_str(v):
            s = str(v).strip()
            return '' if s in ('None', 'nan', 'NaN', 'none', 'NaT') else s

        def fmt_date_str(v):
            try:
                if pd.isna(v): return ''
                return pd.Timestamp(v).strftime('%Y-%m-%d')
            except Exception:
                return ''

        def quad_header(icon: str, title: str, link_url: str = None):
            if link_url:
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f'<div class="quad-hdr">{icon} {html.escape(title)}</div>', unsafe_allow_html=True)
                with c2:
                    st.link_button("🔗 원본", link_url, use_container_width=True)
            else:
                st.markdown(f'<div class="quad-hdr">{icon} {html.escape(title)}</div>', unsafe_allow_html=True)

        # ══════════════════════════════════════
        # 상단 요약 스트립: 기본 정보 (전체 폭, KPI 4개 + 주소)
        # ══════════════════════════════════════
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

            st.markdown(f"""
            <div class="kpi-row">
                <div class="kpi-card">
                    <div class="kpi-label">용도 · 업종</div>
                    <div class="kpi-value" style="font-size:14px;">{html.escape(usage_str)} · {html.escape(biz_str)}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">📍 주소</div>
                    <div class="kpi-value" style="font-size:13px;">{html.escape(road_addr)}</div>
                </div>
                <div class="kpi-card green">
                    <div class="kpi-label">{cur_year}년 누적</div>
                    <div class="kpi-value green">{total_cur:,.0f} <span style="font-size:12px;font-weight:500;">m³</span></div>
                </div>
                <div class="kpi-card amber">
                    <div class="kpi-label">전체 누적</div>
                    <div class="kpi-value" style="font-size:17px;">{total_all:,.0f} <span style="font-size:12px;font-weight:500;">m³</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("기본 정보 데이터가 없습니다.")

        # ══════════════════════════════════════
        # 2 x 2 그리드
        # ══════════════════════════════════════
        # ══════════════════════════════════════
        # 상단 2분할: 계약정보 / 연소기·PSM
        # ══════════════════════════════════════
        row1_col1, row1_col2 = st.columns(2)

        # ── Q1 (좌상): 사용계약정보 ──
        with row1_col1:
            with st.container(border=True):
                quad_header("📄", "사용계약정보")

                contract_col = None
                contract_source_df = None
                for col_name in ['사용계약번호', '계약번호']:
                    if col_name in cust_sale.columns:
                        contract_col = col_name
                        contract_source_df = cust_sale
                        break

                cust_psm_for_contract = pd.DataFrame()
                if contract_col is None and not psm_raw.empty:
                    cust_psm_for_contract = psm_raw[
                        psm_raw['고객명'].apply(clean_name)
                        .str.contains(match_key, na=False, regex=False)
                    ]
                    for col_name in ['사용계약번호', '계약번호']:
                        if col_name in cust_psm_for_contract.columns:
                            contract_col = col_name
                            contract_source_df = cust_psm_for_contract
                            break

                if contract_col is None:
                    st.caption("사용계약번호 컬럼을 찾을 수 없습니다.")
                else:
                    contract_list = (
                        contract_source_df[contract_col]
                        .dropna().astype(str).str.strip()
                    )
                    contract_list = contract_list[contract_list != ''].unique().tolist()

                    if not contract_list:
                        st.caption("등록된 사용계약번호가 없습니다.")
                    else:
                        sale_has_addr = (
                            contract_col in cust_sale.columns
                            and '도로명주소' in cust_sale.columns
                        )
                        src_has_addr = ('도로명주소' in contract_source_df.columns)

                        def lookup_addr(contract_val):
                            road, jibun = '-', '-'
                            if sale_has_addr:
                                m = cust_sale[cust_sale[contract_col].astype(str).str.strip() == contract_val]
                                m = m.dropna(subset=['도로명주소'])
                                if not m.empty:
                                    row0 = m.iloc[0]
                                    road  = str(row0.get('도로명주소', '-')) or '-'
                                    jibun = str(row0.get('지번주소', '-')) or '-'
                                    return road, jibun
                            if src_has_addr:
                                m = contract_source_df[
                                    contract_source_df[contract_col].astype(str).str.strip() == contract_val
                                ].dropna(subset=['도로명주소'])
                                if not m.empty:
                                    row0 = m.iloc[0]
                                    road  = str(row0.get('도로명주소', '-')) or '-'
                                    jibun = str(row0.get('지번주소', '-')) or '-'
                            return road, jibun

                        contract_disp = pd.DataFrame(
                            [(c, *lookup_addr(c)) for c in contract_list],
                            columns=['사용계약번호', '도로명주소', '지번주소'],
                        )
                        st.dataframe(
                            contract_disp,
                            use_container_width=True,
                            hide_index=True,
                            height=38 + min(len(contract_disp), 8) * 36,
                        )

        # ── Q2 (우상): 연소기 · PSM ──
        with row1_col2:
            with st.container(border=True):
                quad_header("🔥", "연소기 · PSM", link_url=PSM_SHEET_URL)

                if psm_raw.empty:
                    st.caption("PSM 데이터를 불러오지 못했습니다.")
                else:
                    cust_psm = psm_raw[
                        psm_raw['고객명'].apply(clean_name)
                        .str.contains(match_key, na=False, regex=False)
                    ].copy()

                    if cust_psm.empty:
                        st.caption("해당 고객의 연소기 데이터가 없습니다.")
                    else:
                        n_burner = len(cust_psm)
                        n_meter  = cust_psm['계량기번호'].nunique() if '계량기번호' in cust_psm.columns else '-'
                        total_heat = cust_psm['연소기열량_num'].sum() if '연소기열량_num' in cust_psm.columns else 0

                        daily_heat = total_heat * 24
                        lng_kg = (daily_heat / 9190) * 0.78
                        lpg_kg = daily_heat / 11040
                        lng_r  = lng_kg / 50000
                        lpg_r  = lpg_kg / 5000

                        def r_badge(label, r):
                            if r >= 1.0:
                                cls, txt = 'b-danger', f'⚠ PSM 대상 ({r:.2f})'
                            elif r >= 0.7:
                                cls, txt = 'b-warn', f'△ 주의 ({r:.2f})'
                            else:
                                cls, txt = 'b-safe', f'✓ 비대상 ({r:.2f})'
                            return f'<span class="psm-badge {cls}" style="margin-right:6px;">{label} {txt}</span>'

                        st.markdown(f"""
                        <div style="display:flex; gap:16px; margin-bottom:10px; font-size:13px;">
                            <div>연소기 <b>{n_burner}</b>대</div>
                            <div>계량기 <b>{n_meter}</b>대</div>
                            <div>총열량 <b>{total_heat:,.0f}</b> kcal/h</div>
                        </div>
                        <div style="margin-bottom:10px;">{r_badge('LNG', lng_r)}{r_badge('LPG', lpg_r)}</div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"**연소기 목록 ({n_burner}대)**")
                        burner_sorted = cust_psm.copy()
                        if '연소기열량_num' in burner_sorted.columns:
                            burner_sorted = burner_sorted.sort_values('연소기열량_num', ascending=False).reset_index(drop=True)

                        disp_df = pd.DataFrame()
                        if '계량기번호' in burner_sorted.columns:
                            disp_df['계량기번호'] = burner_sorted['계량기번호'].apply(clean_str)
                        disp_df['연소기명'] = burner_sorted.get('연소기명', pd.Series([''] * len(burner_sorted))).apply(clean_str)
                        disp_df['열량(kcal/h)'] = burner_sorted.get('연소기열량_num', pd.Series([0] * len(burner_sorted)))

                        st.dataframe(
                            disp_df,
                            use_container_width=True,
                            hide_index=True,
                            column_config={'열량(kcal/h)': st.column_config.NumberColumn('열량 (kcal/h)', format="%,.0f")},
                            height=38 + min(len(disp_df), 8) * 36,
                        )

        # ══════════════════════════════════════
        # 전체 폭: 상담 · 면담 이력
        # ══════════════════════════════════════
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            quad_header("📝", "상담 · 면담 이력")

            if cust_interview.empty:
                st.caption("등록된 상담 이력이 없습니다.")
            else:
                itv_disp = pd.DataFrame()
                itv_disp['날짜'] = cust_interview['날짜'].dt.strftime('%Y-%m-%d')
                if '담당자' in cust_interview.columns:
                    itv_disp['담당자'] = cust_interview['담당자'].apply(clean_str)
                itv_disp['면담 내용'] = cust_interview['면담 내용'].apply(
                    lambda v: str(v).strip() if pd.notna(v) and str(v).strip() else '(내용 없음)'
                )

                st.dataframe(
                    itv_disp,
                    use_container_width=True,
                    hide_index=True,
                    height=38 + min(len(itv_disp), 8) * 36,
                )

        # ══════════════════════════════════════
        # 판매량: 좌(연간 선그래프) / 우(시설물별 가로막대)
        # ══════════════════════════════════════
        row2_col1, row2_col2 = st.columns(2)

        # ── 연간 판매량 추이 ──
        with row2_col1:
            with st.container(border=True):
                quad_header("📊", "연간 판매량 추이")

                if cust_sale.empty:
                    st.caption("판매량 데이터가 없습니다.")
                else:
                    year_list = sorted(cust_sale['매출년월'].dt.year.unique(), reverse=True)
                    default_years = year_list[:min(2, len(year_list))]

                    sel_years = st.multiselect(
                        "조회 연도", options=year_list, default=default_years,
                        key="sel_years_multi", format_func=lambda y: f"{y}년",
                        label_visibility="collapsed",
                    )

                    if not sel_years:
                        st.caption("연도를 하나 이상 선택해주세요.")
                    else:
                        sel_years_sorted = sorted(sel_years)
                        PALETTE = ['#1a73e8', '#0f9d58', '#f9ab00', '#ea4335', '#9334e6']
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
                                x=monthly['월'], y=monthly['사용량(m3)'], name=f'{yr}년',
                                mode='lines+markers',
                                line=dict(color=color, width=2.5 if is_latest else 1.6,
                                          dash='solid' if is_latest else 'dot'),
                                marker=dict(size=6 if is_latest else 4, color=color,
                                            line=dict(color='#ffffff', width=1.2)),
                                fill='tozeroy' if is_latest else 'none',
                                fillcolor=f'rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.06)' if is_latest else None,
                                hovertemplate=f'%{{x}}월 · {yr}년<br>%{{y:,.0f}} m³<extra></extra>',
                            ))

                        fig_m.update_layout(
                            height=260, margin=dict(t=10, b=8, l=0, r=8),
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                            hovermode='x unified',
                            legend=dict(orientation='h', yanchor='bottom', y=1.0, xanchor='right', x=1, font=dict(size=10)),
                            yaxis=dict(showgrid=True, gridcolor='#f0f2f4', tickformat=',.0f', title=None, tickfont=dict(size=9)),
                            xaxis=dict(title=None, fixedrange=True, tickmode='array',
                                       tickvals=list(range(1, 13)), ticktext=[f'{m}월' for m in range(1, 13)],
                                       tickfont=dict(size=9)),
                        )
                        st.plotly_chart(fig_m, use_container_width=True, config={'displayModeBar': False})

        # ── 시설물별 판매량 비교 ──
        with row2_col2:
            with st.container(border=True):
                quad_header("🏗️", "시설물별 판매량 비교")

                if cust_sale.empty or '시설물번호' not in cust_sale.columns:
                    st.caption("시설물번호 데이터가 없습니다.")
                else:
                    month_options = sorted(
                        cust_sale['매출년월'].dropna().dt.to_period('M').unique(), reverse=True
                    )
                    if not month_options:
                        st.caption("매출년월 데이터가 없습니다.")
                    else:
                        sel_month = st.selectbox(
                            "조회 월", options=month_options, index=0,
                            format_func=lambda p: f"{p.year}년 {p.month}월",
                            key="facility_month_sel",
                        )
                        month_sale = cust_sale[cust_sale['매출년월'].dt.to_period('M') == sel_month]

                        facility_usage = (
                            month_sale.dropna(subset=['시설물번호'])
                            .groupby('시설물번호', as_index=False)['사용량(m3)'].sum()
                            .sort_values('사용량(m3)', ascending=True)
                        )

                        if facility_usage.empty:
                            st.caption("해당 월에 시설물별 판매량 데이터가 없습니다.")
                        else:
                            fig_f = go.Figure(go.Bar(
                                x=facility_usage['사용량(m3)'],
                                y=facility_usage['시설물번호'].astype(str),
                                orientation='h',
                                marker_color='#1a73e8',
                                text=[f"{v:,.0f}" for v in facility_usage['사용량(m3)']],
                                textposition='outside',
                                textfont=dict(size=9, color='#3c4043'),
                                hovertemplate='시설물번호 %{y}<br>%{x:,.0f} m³<extra></extra>',
                            ))
                            bar_h = max(28 * len(facility_usage), 260)
                            fig_f.update_layout(
                                height=min(bar_h, 500),
                                margin=dict(t=10, b=8, l=0, r=50),
                                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                xaxis=dict(showgrid=True, gridcolor='#f0f2f4', tickformat=',.0f', title=None, tickfont=dict(size=9)),
                                yaxis=dict(title=None, tickfont=dict(size=9), type='category'),
                            )
                            st.plotly_chart(fig_f, use_container_width=True, config={'displayModeBar': False})
                            st.caption(f"{sel_month.year}년 {sel_month.month}월 기준")

        # ══════════════════════════════════════
        # 전체 폭: 월별 증감 분석 테이블
        # ══════════════════════════════════════
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            quad_header("📈", "월별 증감 분석 (전년 대비)")

            if cust_sale.empty:
                st.caption("판매량 데이터가 없습니다.")
            else:
                if '시설물번호' in cust_sale.columns:
                    facility_options = sorted(cust_sale['시설물번호'].dropna().unique().tolist())
                    sel_facilities = st.multiselect(
                        "시설물번호 선택 (미선택 시 전체 합산)",
                        options=facility_options,
                        default=[],
                        key="yoy_facility_sel",
                    )
                    yoy_source = cust_sale[cust_sale['시설물번호'].isin(sel_facilities)] if sel_facilities else cust_sale
                else:
                    yoy_source = cust_sale

                def fmt_num(v):
                    return '-' if pd.isna(v) else f"{v:,.0f}"

                def fmt_pct(v):
                    return '-' if pd.isna(v) or not np.isfinite(v) else f"{v:+.1f}%"

                if yoy_source.empty:
                    st.caption("선택한 시설물에 대한 판매량 데이터가 없습니다.")
                else:
                    monthly_yoy = (
                        yoy_source
                        .assign(연=yoy_source['매출년월'].dt.year, 월=yoy_source['매출년월'].dt.month)
                        .groupby(['연', '월'], as_index=False)['사용량(m3)'].sum()
                        .sort_values(['연', '월'])
                        .reset_index(drop=True)
                    )
                    monthly_yoy['당년누계판매량'] = monthly_yoy.groupby('연')['사용량(m3)'].cumsum()

                    prior = monthly_yoy[['연', '월', '사용량(m3)', '당년누계판매량']].copy()
                    prior['연'] = prior['연'] + 1
                    prior = prior.rename(columns={
                        '사용량(m3)': '전년동월판매량',
                        '당년누계판매량': '전년누계판매량',
                    })

                    merged = monthly_yoy.merge(prior, on=['연', '월'], how='left')
                    merged = merged.rename(columns={'사용량(m3)': '당월판매량'})

                    merged['매출년월'] = merged['연'].astype(str) + '-' + merged['월'].astype(str).str.zfill(2)
                    merged['당월증감'] = merged['당월판매량'] - merged['전년동월판매량']
                    merged['당월증감률'] = merged['당월증감'] / merged['전년동월판매량'] * 100
                    merged['누계증감'] = merged['당년누계판매량'] - merged['전년누계판매량']
                    merged['누계증감률'] = merged['누계증감'] / merged['전년누계판매량'] * 100

                    yoy_disp = pd.DataFrame({
                        '매출년월': merged['매출년월'],
                        '당월판매량': merged['당월판매량'].apply(fmt_num),
                        '전년동월판매량': merged['전년동월판매량'].apply(fmt_num),
                        '증감': merged['당월증감'].apply(fmt_num),
                        '증감률': merged['당월증감률'].apply(fmt_pct),
                        '당년누계판매량': merged['당년누계판매량'].apply(fmt_num),
                        '전년누계판매량': merged['전년누계판매량'].apply(fmt_num),
                        '누계증감': merged['누계증감'].apply(fmt_num),
                        '누계증감률': merged['누계증감률'].apply(fmt_pct),
                    }).sort_values('매출년월', ascending=False)

                    st.dataframe(
                        yoy_disp,
                        use_container_width=True,
                        hide_index=True,
                        height=38 + min(len(yoy_disp), 8) * 36,
                    )