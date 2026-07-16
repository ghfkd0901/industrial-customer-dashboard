"""
backfill_local.py
──────────────────────────────────────────
초기 적재용 스크립트. Streamlit 앱이 아니라 터미널에서 직접 실행합니다.
'산업용_통합데이터_정리완료.csv' (이미 산업용만 정리된 파일)를 읽어서
Supabase sales 테이블에 통째로 upsert 합니다.
컬럼명은 BigQuery dse-marketing.sales.sales 과 동일하게 맞췄습니다.

사용법:
    1) pip install supabase python-dotenv pandas
    2) 프로젝트 루트에 .env 파일 만들고 아래 두 줄 작성:
         SUPABASE_URL=https://xxxxx.supabase.co
         SUPABASE_KEY=secret_key_붙여넣기
    3) python backfill_local.py
"""

import os
import sys
import math
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ .env 파일에 SUPABASE_URL / SUPABASE_KEY 를 설정하세요.")
    sys.exit(1)

CSV_PATH = os.path.join("data", "산업용_통합데이터_정리완료.csv")
TABLE_NAME = "sales"
BATCH_SIZE = 500

# ── 원본 컬럼 → DB 컬럼 매핑 (supabase_utils.py와 동일하게 유지, BigQuery alias 기준) ──
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
DB_COLUMNS = list(dict.fromkeys(COLUMN_MAP.values()))
DATE_COLS = ["first_supply_date", "product_start_date", "product_end_date",
             "billing_ym", "meter_date", "sales_ym"]
NUMERIC_COLS = ["monthly_usage_plan", "usage_m3", "usage_mj"]
INT_COLS = ["no_"]


def parse_flexible_date(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip()
    parsed = pd.to_datetime(s, errors="coerce")
    mask = parsed.isna()
    if mask.any():
        parsed.loc[mask] = pd.to_datetime(s[mask], format="%b-%y", errors="coerce")
    return parsed


def load_and_clean() -> pd.DataFrame:
    print(f"📂 읽는 중: {CSV_PATH}")
    try:
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(CSV_PATH, encoding="cp949")

    print(f"   원본 행 수: {len(df):,}")
    print(f"   원본 컬럼: {df.columns.tolist()}")

    if "상품명" in df.columns:
        before = len(df)
        df = df[df["상품명"] == "산업용"].copy()
        print(f"   산업용 필터: {before:,} → {len(df):,}")

    rename_map = {k: v for k, v in COLUMN_MAP.items() if k in df.columns}
    df = df.rename(columns=rename_map)

    missing = [c for c in ["contract_no", "billing_ym"] if c not in df.columns]
    if missing:
        print(f"❌ 필수 컬럼 없음: {missing}")
        print("   COLUMN_MAP을 실제 CSV 컬럼명에 맞게 수정하세요.")
        sys.exit(1)

    keep_cols = [c for c in DB_COLUMNS if c in df.columns]
    df = df[keep_cols]

    for col in DATE_COLS:
        if col in df.columns:
            parsed = parse_flexible_date(df[col])
            df[col] = parsed.dt.strftime("%Y-%m-%d")
            df[col] = df[col].where(parsed.notna(), None)

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

    df = df.where(pd.notna(df), None)
    df = df[df["contract_no"].notna() & df["billing_ym"].notna()]
    dedup_cols = [c for c in ["contract_no", "facility_id", "management_seq", "sales_ym", "usage_m3"] if c in df.columns]
    df = df.drop_duplicates(subset=dedup_cols, keep="last")

    print(f"   업로드 대상 행 수: {len(df):,}")
    return df




def scrub_nan(records: list) -> list:
    cleaned = []
    for row in records:
        cleaned.append({
            k: (None if isinstance(v, float) and math.isnan(v) else v)
            for k, v in row.items()
        })
    return cleaned


def upload(df: pd.DataFrame):
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    records = df.to_dict(orient="records")
    records = scrub_nan(records)
    total = len(records)

    # 계약번호+시설물번호+관리회차+매출년월+사용량(m3) 전부 같으면 중복으로 보고 덮어씀
    for i in range(0, total, BATCH_SIZE):
        batch = records[i : i + BATCH_SIZE]
        client.table(TABLE_NAME).upsert(batch, on_conflict="contract_no,facility_id,management_seq,sales_ym,usage_m3").execute()
        done = min(i + BATCH_SIZE, total)
        print(f"   업로드 진행: {done:,} / {total:,}", end="\r")

    print(f"\n✅ 완료: 총 {total:,}건 업로드")


if __name__ == "__main__":
    df = load_and_clean()
    if df.empty:
        print("⚠️ 업로드할 데이터가 없습니다.")
        sys.exit(0)
    upload(df)