"""
KOSIS API 데이터 구조 분석
"""
import pandas as pd

df = pd.read_csv('kosis_api_test_result.csv', encoding='utf-8-sig')

print("=" * 80)
print("KOSIS API 데이터 구조 분석")
print("=" * 80)

print("\n[1] 기본 정보")
print(f"  총 행 수: {len(df):,}")
print(f"  컬럼 수: {len(df.columns)}")

print("\n[2] 주요 컬럼 분석")
print(f"  시도 (C1_NM): {df['C1_NM'].nunique()}개 고유값")
print(f"  연령대 (C2_NM): {df['C2_NM'].nunique()}개 고유값")
print(f"  항목 (ITM_NM): {df['ITM_NM'].nunique()}개 고유값")
print(f"  통계표 (TBL_ID): {df['TBL_ID'].unique()[0]}")
print(f"  기간 (PRD_DE): {df['PRD_DE'].unique()}")

print("\n[3] 시도 목록 (처음 20개)")
sidos = sorted(df['C1_NM'].unique())
for i, sido in enumerate(sidos[:20], 1):
    print(f"  {i}. {sido}")
if len(sidos) > 20:
    print(f"  ... 외 {len(sidos)-20}개")

print("\n[4] 연령대 목록")
age_groups = sorted(df['C2_NM'].unique())
for i, age in enumerate(age_groups, 1):
    print(f"  {i}. {age}")

print("\n[5] 항목 목록 (ITM_NM)")
items = sorted(df['ITM_NM'].unique())
for i, item in enumerate(items, 1):
    print(f"  {i}. {item}")

print("\n[6] 데이터 샘플 (시도별, 연령별, 성별)")
sample = df[(df['C1_NM'] != '전국') & (df['C2_NM'] != '합계')].head(10)
print(sample[['C1_NM', 'C2_NM', 'ITM_NM', 'DT']].to_string(index=False))

print("\n[7] 데이터 값 통계")
print(f"  최소값: {int(df['DT'].min()):,}")
print(f"  최대값: {int(df['DT'].max()):,}")
print(f"  평균값: {int(df['DT'].mean()):,}")
print(f"  총합: {int(df['DT'].sum()):,}")
