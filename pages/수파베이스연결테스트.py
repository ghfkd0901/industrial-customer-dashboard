"""
test_connection.py
프로젝트 루트에 저장하고 터미널에서:
    streamlit run test_connection.py
로 실행하세요. (기존 app.py는 안 건드립니다)
"""

import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Supabase 연결 테스트", page_icon="🔌")
st.title("🔌 Supabase 연결 테스트")

# ── 1. secrets.toml 값 확인 ──
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    st.success(f"secrets.toml 로드 성공")
    st.code(f"SUPABASE_URL = {url}\nSUPABASE_KEY = {key[:15]}... (일부만 표시)")
except Exception as e:
    st.error("secrets.toml을 못 읽었습니다. .streamlit/secrets.toml 위치와 내용을 확인하세요.")
    st.exception(e)
    st.stop()

# ── 2. 클라이언트 생성 ──
try:
    client = create_client(url, key)
    st.success("Supabase 클라이언트 생성 성공")
except Exception as e:
    st.error("클라이언트 생성 실패 (URL/KEY 형식 확인)")
    st.exception(e)
    st.stop()

# ── 3. 실제 테이블 조회 시도 ──
st.divider()
st.subheader("industrial_sales 테이블 조회")

if st.button("조회 테스트 실행", type="primary"):
    try:
        resp = client.table("industrial_sales").select("*", count="exact").limit(5).execute()
        st.success(f"연결 성공! 현재 테이블 행 수: {resp.count}")
        if resp.data:
            st.write("샘플 데이터 (최대 5건):")
            st.dataframe(resp.data)
        else:
            st.info("테이블은 존재하지만 아직 데이터가 없습니다. (정상 - 백필 전이면 당연합니다)")
    except Exception as e:
        st.error("테이블 조회 실패")
        st.exception(e)
        st.warning(
            "'relation \"industrial_sales\" does not exist' 에러가 뜨면 "
            "아직 schema.sql을 Supabase SQL Editor에서 실행 안 하신 겁니다. "
            "먼저 schema.sql부터 실행하세요."
        )