"""최종 결과 파일의 지역 구분 확인"""
import pandas as pd

# 최종 결과 파일 읽기
df = pd.read_csv('final_joint_distribution_extended.csv', encoding='utf-8-sig')

print("=" * 80)
print("최종 결과 파일의 지역 구분 (Sido) 확인")
print("=" * 80)

# Sido 고유 값 확인
sidos = sorted(df['Sido'].unique())

print(f"\n총 시도 수: {len(sidos)}개")
print(f"\n시도 목록:")
for i, sido in enumerate(sidos, 1):
    print(f"  {i:2d}. {sido}")

# 각 시도별 데이터 수 확인
print(f"\n시도별 데이터 행 수:")
sido_counts = df['Sido'].value_counts().sort_index()
for sido, count in sido_counts.items():
    print(f"  {sido}: {count:,}행")

# Sigungu도 확인
print(f"\n" + "=" * 80)
print("시군구 (Sigungu) 확인")
print("=" * 80)

sigungus = sorted(df['Sigungu'].unique())
print(f"\n총 시군구 수: {len(sigungus)}개")
print(f"\n시군구 목록 (처음 30개):")
for i, sigungu in enumerate(sigungus[:30], 1):
    print(f"  {i:2d}. {sigungu}")

if len(sigungus) > 30:
    print(f"  ... 외 {len(sigungus) - 30}개")

# 시도-시군구 조합 샘플 확인
print(f"\n" + "=" * 80)
print("시도-시군구 조합 샘플")
print("=" * 80)
sample = df[['Sido', 'Sigungu']].drop_duplicates().head(20)
print(sample.to_string(index=False))
