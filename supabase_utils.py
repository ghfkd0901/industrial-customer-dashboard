"""
supabase_utils.py
──────────────────────────────────────────
app.py, pages/*.py, backfill 스크립트에서 공통으로 쓰는 Supabase 연결 + 데이터 매핑 로직.
컬럼명은 BigQuery `dse-marketing.sales.sales` 과 동일하게 맞췄습니다.
이 파일을 프로젝트 루트에 넣고 다른 스크립트에서 import 해서 씁니다.
"""

import math
import streamlit as st
import pandas as pd
from supabase import create_client, Client


# ─────────────────────────────────────────
# 1. 클라이언트
# ─────────────────────────────────────────
@st.cache_resource
def get_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


TABLE_NAME = "sales"


# ─────────────────────────────────────────
# 2. 원본 CSV 컬럼 → DB 컬럼 매핑
#    BigQuery `dse-marketing.sales.sales` 쿼리의 alias와 동일하게 맞춤.
#    ※ 실제 파일 컬럼명이 다르면 이 딕셔너리만 고치면 됩니다.
# ─────────────────────────────────────────
COLUMN_MAP = {
    "No": "no_",
    "구분": "category",
    "용도": "usage_type",
    "번지순번": "address_no",
    "설치장소번호": "facility_no",
    "사용계약번호": "contract_no",
    "시설물번호": "facility_id",
    "고객번호": "customer_no",
    "고객명": "customer_name",
    "도로명주소": "road_address",
    "지번주소": "lot_address",
    "시군구": "district",
    "등급": "grade",
    "최초공급일": "first_supply_date",
    "업종분류": "industry_code",
    "업종": "industry_name",
    "상품명": "product_name",
    "상품계약일자": "product_start_date",
    "상품해지일자": "product_end_date",
    "월 사용예정량": "monthly_usage_plan",
    "청구년월": "billing_ym",
    "관리회차": "management_seq",
    "사용량(m3)": "usage_m3",
    "사용량(mj)": "usage_mj",
    "납기구분": "payment_type",
    "검침적용일자": "meter_date",
    "공동주택코드": "apartment_code",
    "공동주택명": "apartment_name",
    "매출년월": "sales_ym",
}

DB_COLUMNS = list(dict.fromkeys(COLUMN_MAP.values()))  # 순서 유지, 중복 제거

DATE_COLS = [
    "first_supply_date", "product_start_date", "product_end_date",
    "billing_ym", "meter_date", "sales_ym",
]
NUMERIC_COLS = ["monthly_usage_plan", "usage_m3", "usage_mj"]
INT_COLS = ["no_"]


def _parse_flexible_date(series: pd.Series) -> pd.Series:
    """
    청구년월/매출년월 같은 컬럼은 파일마다 형식이 조금씩 다를 수 있음
    (예: '2026-02', '2026-02-01', 엑셀에서 저장 시 'Feb-26'으로 깨지는 경우 등).
    여러 형식을 순서대로 시도해서 최대한 살림.
    """
    s = series.astype(str).str.strip()

    # 1차: 표준 파싱 (YYYY-MM, YYYY-MM-DD 등 대부분 여기서 잡힘)
    parsed = pd.to_datetime(s, errors="coerce")

    # 2차: 엑셀 자동변환으로 깨진 'Mon-YY' 형식 재시도 (예: Feb-26)
    mask = parsed.isna()
    if mask.any():
        parsed_mmmyy = pd.to_datetime(s[mask], format="%b-%y", errors="coerce")
        parsed.loc[mask] = parsed_mmmyy

    return parsed


def clean_and_map_df(df: pd.DataFrame, filter_industrial: bool = True) -> pd.DataFrame:
    """
    원본 CSV DataFrame을 받아서
    1) 산업용만 필터링 (옵션)
    2) 컬럼명을 DB 컬럼명으로 변환
    3) 타입 정리 (날짜/숫자)
    4) DB에 없는 컬럼 제거
    """
    df = df.copy()

    # 산업용 필터 (상품명 컬럼 기준 - 용도 컬럼이 아님)
    if filter_industrial and "상품명" in df.columns:
        df = df[df["상품명"] == "산업용"].copy()

    # 컬럼명 변환 (매핑에 있는 것만)
    rename_map = {k: v for k, v in COLUMN_MAP.items() if k in df.columns}
    df = df.rename(columns=rename_map)

    # DB에 존재하는 컬럼만 남기기
    keep_cols = [c for c in DB_COLUMNS if c in df.columns]
    df = df[keep_cols]

    # 필수 키 컬럼 없으면 에러
    if "contract_no" not in df.columns or "billing_ym" not in df.columns:
        raise ValueError(
            "contract_no(사용계약번호) 또는 billing_ym(청구년월) 컬럼을 찾을 수 없습니다. "
            "COLUMN_MAP을 실제 파일 컬럼명에 맞게 수정하세요."
        )

    # 날짜 컬럼 정리 (여러 형식 유연하게 파싱)
    for col in DATE_COLS:
        if col in df.columns:
            parsed = _parse_flexible_date(df[col])
            df[col] = parsed.dt.strftime("%Y-%m-%d")
            df[col] = df[col].where(parsed.notna(), None)

    # 숫자 컬럼 정리 (천단위 콤마 제거 후 변환, 예: "3,401.4783")
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(",", "", regex=False), errors="coerce"
            )
            df[col] = df[col].where(df[col].notna(), None)

    for col in INT_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = df[col].apply(lambda v: int(v) if pd.notna(v) else None)

    # 나머지 NaN -> None (Supabase는 NaN을 못 받음)
    df = df.where(pd.notna(df), None)

    # contract_no, billing_ym 둘 다 있는 행만 (PK 무결성)
    df = df[df["contract_no"].notna() & df["billing_ym"].notna()]

    # 같은 배치 안에서 완전히 동일한 행(계약번호+시설물번호+관리회차+매출년월+사용량)만 중복 제거
    dedup_cols = [c for c in ["contract_no", "facility_id", "management_seq", "sales_ym", "usage_m3"] if c in df.columns]
    df = df.drop_duplicates(subset=dedup_cols, keep="last")

    return df



def _scrub_nan(records: list) -> list:
    """
    dict 리스트를 순회하며 float NaN을 전부 None으로 치환.
    pandas의 df.where()는 float 컬럼에서 dtype 유지 때문에 NaN이 되살아나는 경우가 있어서,
    JSON 직렬화 직전 딕셔너리 레벨에서 한 번 더 확실하게 걸러냄.
    """
    cleaned = []
    for row in records:
        cleaned.append({
            k: (None if isinstance(v, float) and math.isnan(v) else v)
            for k, v in row.items()
        })
    return cleaned


def upsert_sales(df: pd.DataFrame, batch_size: int = 500, progress_callback=None) -> int:
    """
    df를 sales 테이블에 upsert.
    contract_no + billing_ym 이 같으면 덮어쓰기, 없으면 새로 추가.
    반환값: 처리된 row 수
    """
    client = get_client()
    records = df.to_dict(orient="records")
    records = _scrub_nan(records)
    total = len(records)

    # 계약번호+시설물번호+관리회차+매출년월+사용량(m3) 전부 같으면 중복으로 보고 덮어씀
    for i in range(0, total, batch_size):
        batch = records[i : i + batch_size]
        client.table(TABLE_NAME).upsert(batch, on_conflict="contract_no,facility_id,management_seq,sales_ym,usage_m3").execute()
        if progress_callback:
            progress_callback(min(i + batch_size, total), total)

    return total


def fetch_sales(customer_name: str = None) -> pd.DataFrame:
    """
    조회 화면에서 쓸 함수. customer_name 지정 시 해당 고객만, 없으면 전체.
    app.py 화면에서 실제로 쓰는 컬럼만 select해서 페이로드를 줄임.
    """
    # app.py가 실제로 참조하는 컬럼만 (필요한 컬럼이 늘어나면 여기에 추가)
    SELECT_COLUMNS = (
        "contract_no,customer_name,usage_type,industry_code,industry_name,"
        "road_address,lot_address,sales_ym,usage_m3,usage_mj"
    )

    client = get_client()
    query = client.table(TABLE_NAME).select(SELECT_COLUMNS)
    if customer_name:
        query = query.eq("customer_name", customer_name)

    all_rows = []
    page_size = 5000  # Supabase 대시보드에서 Max Rows를 5000 이상으로 올려야 효과 있음
    offset = 0
    while True:
        resp = query.range(offset, offset + page_size - 1).execute()
        rows = resp.data
        all_rows.extend(rows)
        if len(rows) < page_size:
            break
        offset += page_size

    df = pd.DataFrame(all_rows)
    if not df.empty:
        df["sales_ym"] = pd.to_datetime(df["sales_ym"], errors="coerce")
    return df


def load_sales_for_app() -> pd.DataFrame:
    """
    app.py에서 바로 쓸 수 있는 형태로 판매량 데이터 로드.
    Supabase에서 가져온 영문 컬럼명 -> app.py가 쓰는 한글 컬럼명으로 변환 + 기본 정제까지 처리.
    app.py는 이 함수 하나만 호출하면 됨.
    """
    sale_df = fetch_sales()

    sale_df = sale_df.rename(columns={
        'no_': 'No',
        'category': '구분',
        'usage_type': '용도',
        'address_no': '번지순번',
        'facility_no': '설치장소번호',
        'contract_no': '사용계약번호',
        'facility_id': '시설물번호',
        'customer_no': '고객번호',
        'customer_name': '고객명',
        'road_address': '도로명주소',
        'lot_address': '지번주소',
        'district': '시군구',
        'grade': '등급',
        'first_supply_date': '최초공급일',
        'industry_code': '업종분류',
        'industry_name': '업종',
        'product_name': '상품명',
        'product_start_date': '상품계약일자',
        'product_end_date': '상품해지일자',
        'monthly_usage_plan': '월 사용예정량',
        'billing_ym': '청구년월',
        'management_seq': '관리회차',
        'usage_m3': '사용량(m3)',
        'usage_mj': '사용량(mj)',
        'payment_type': '납기구분',
        'meter_date': '검침적용일자',
        'apartment_code': '공동주택코드',
        'apartment_name': '공동주택명',
        'sales_ym': '매출년월',
    })

    if sale_df.empty:
        return sale_df

    sale_df['매출년월'] = pd.to_datetime(sale_df['매출년월'], errors='coerce')
    sale_df = sale_df.dropna(subset=['매출년월']).sort_values('매출년월')
    sale_df['고객명'] = sale_df['고객명'].astype(str).str.strip()

    return sale_df
    """사이드바 고객 목록용 - 고객명 unique 리스트"""
    client = get_client()
    resp = client.table(TABLE_NAME).select("customer_name").execute()
    names = sorted({r["customer_name"] for r in resp.data if r["customer_name"]})
    return names