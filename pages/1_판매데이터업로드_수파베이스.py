"""
pages/1_데이터입력.py 로 저장하세요 (기존 pages/ 폴더 안에).
담당자가 매달 CSV를 업로드하면 산업용만 필터링해서 Supabase에 upsert.
"""

import streamlit as st
import pandas as pd
from supabase_utils import clean_and_map_df, upsert_sales

st.set_page_config(page_title="판매량 데이터 입력", page_icon="📥", layout="centered")

st.title("📥 산업용 판매량 데이터 입력")
st.caption(
    "가정용외_YYYY.csv, 가정용외_YYYYMM.csv 등 원본 CSV를 그대로 업로드하세요. "
    "산업용만 자동으로 걸러서 저장합니다. 초기 백필(연도별 파일)이든 매달 갱신이든 동일하게 쓰면 됩니다."
)
st.caption("⚠️ 한 파일당 최대 200MB까지 업로드 가능합니다. 연도별 파일은 한 번에 하나씩 순서대로 올려주세요.")

uploaded = st.file_uploader("CSV 파일 선택", type=["csv"])

if uploaded is not None:
    # 인코딩 자동 시도
    try:
        raw_df = pd.read_csv(uploaded, encoding="cp949")
    except UnicodeDecodeError:
        uploaded.seek(0)
        raw_df = pd.read_csv(uploaded, encoding="utf-8-sig")

    st.write(f"원본 행 수: **{len(raw_df):,}**")

    # ── 진단용: 상품명 값 분포 확인 ──
    if "상품명" in raw_df.columns:
        with st.expander("🔍 상품명 값 분포 확인 (필터링 진단용)"):
            st.write(raw_df["상품명"].value_counts(dropna=False))
    else:
        st.warning("이 파일에 '상품명' 컬럼이 없습니다. 컬럼명을 확인해주세요.")
        st.write("실제 컬럼:", raw_df.columns.tolist())

    try:
        cleaned_df = clean_and_map_df(raw_df, filter_industrial=True)
    except ValueError as e:
        st.error(str(e))
        st.stop()

    st.write(f"산업용 필터 후 업로드 대상: **{len(cleaned_df):,}**건")

    with st.expander("미리보기 (상위 20건)"):
        st.dataframe(cleaned_df.head(20), use_container_width=True)

    if cleaned_df.empty:
        st.warning("업로드할 산업용 데이터가 없습니다. 파일을 확인해주세요.")
    else:
        if st.button("🚀 Supabase에 업로드", type="primary", use_container_width=True):
            progress_bar = st.progress(0, text="업로드 중...")

            def update_progress(done, total):
                progress_bar.progress(done / total, text=f"업로드 중... {done:,} / {total:,}")

            with st.spinner("처리 중..."):
                count = upsert_sales(cleaned_df, progress_callback=update_progress)

            progress_bar.empty()
            st.success(f"✅ {count:,}건 업로드 완료! (같은 계약번호+청구년월은 자동으로 덮어씀)")
            st.cache_data.clear()  # 조회 화면 캐시 초기화 -> 바로 반영
            st.balloons()

st.divider()
st.caption(
    "⚠️ 사용계약번호+시설물번호+관리회차+매출년월+사용량(m3)이 전부 같은 행만 중복으로 간주해 자동으로 덮어씁니다. "
    "하나라도 다르면 별개 데이터로 새로 추가되니, 같은 파일을 재업로드해도 안전합니다."
)