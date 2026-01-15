"""확장된 결과 확인"""
import pandas as pd
import json

# 결과 파일 읽기
df = pd.read_csv('final_joint_distribution_extended.csv', encoding='utf-8-sig')

print("=" * 80)
print("확장된 IPF 결과 확인")
print("=" * 80)

print(f"\n총 행 수: {len(df):,}")
print(f"컬럼: {list(df.columns)}")

print(f"\n각 차원별 고유 값 수:")
for col in df.columns:
    if col != 'Weight':
        unique_count = df[col].nunique()
        print(f"  {col}: {unique_count}개")
        if unique_count <= 10:
            print(f"    → {sorted(df[col].unique().tolist())}")

print(f"\nWeight 통계:")
print(f"  합계: {df['Weight'].sum():.10f}")
print(f"  최소값: {df['Weight'].min():.10f}")
print(f"  최대값: {df['Weight'].max():.10f}")
print(f"  평균값: {df['Weight'].mean():.10f}")

print(f"\n샘플 데이터 (처음 15행):")
print(df.head(15).to_string(index=False))

# 차원 정보 확인
try:
    with open('dimension_info.json', 'r', encoding='utf-8') as f:
        dim_info = json.load(f)
    print(f"\n차원 정보:")
    print(f"  차원 수: {len(dim_info['dimension_names'])}개")
    print(f"  차원 목록: {dim_info['dimension_names']}")
    for dim_name, count in dim_info['dimension_counts'].items():
        print(f"    {dim_name}: {count}개")
except:
    pass
