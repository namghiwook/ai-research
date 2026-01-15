"""최종 결과 파일에서 통계 조회"""
import pandas as pd

# 최종 결과 파일 읽기
df = pd.read_csv('final_joint_distribution_extended.csv', encoding='utf-8-sig')

print("=" * 80)
print("통계 조회: 20~24세 미혼 남자 인구수")
print("=" * 80)

# 조건 필터링
# 연령대 형식 확인
print("\n[1] 연령대 고유 값 확인:")
age_groups = sorted(df['Age_Group'].unique())
print(f"  총 {len(age_groups)}개 연령대")
for age in age_groups:
    if '20' in str(age) or '24' in str(age):
        print(f"    → {age}")

# 필터링
# 연령대: 20-24 형식 확인
print("\n[1-1] 20-24 관련 연령대:")
age_20_24 = [x for x in df['Age_Group'].unique() if '20' in str(x) and '24' in str(x)]
print(f"  {age_20_24}")

# 정확한 연령대 매칭
age_conditions = df['Age_Group'].isin(['20-24', '20~24세', '20-24세', '20~24'])

filtered = df[
    age_conditions &
    (df['Gender'] == '남자') &
    (df['Marital_Status'] == '미혼')
].copy()

print(f"\n[2] 필터링 결과:")
print(f"  조건: 20~24세 + 남자 + 미혼")
print(f"  매칭된 행 수: {len(filtered)}개")

if len(filtered) > 0:
    # Weight 합계 계산
    weight_sum = filtered['Weight'].sum()
    
    print(f"\n[3] Weight 합계: {weight_sum:.10f}")
    print(f"  (전체 확률 분포에서의 비율)")
    
    # 전체 인구수 가정: 약 4,000만 명 (성인 인구)
    total_population = 40_000_000
    estimated_population = weight_sum * total_population
    
    print(f"\n[4] 추정 인구수:")
    print(f"  전체 성인 인구 가정: {total_population:,}명")
    print(f"  20~24세 미혼 남자 인구수: {estimated_population:,.0f}명")
    print(f"  ({estimated_population/1_000_000:.2f}백만 명)")
    
    # 지역별 분포 확인
    print(f"\n[5] 지역별 분포 (상위 10개):")
    regional_dist = filtered.groupby('Sido')['Weight'].sum().sort_values(ascending=False).head(10)
    for sido, weight in regional_dist.items():
        pop = weight * total_population
        print(f"  {sido}: {pop:,.0f}명 ({weight*100:.2f}%)")
    
    # 샘플 데이터 확인
    print(f"\n[6] 샘플 데이터 (처음 10행):")
    print(filtered[['Sido', 'Sigungu', 'Age_Group', 'Gender', 'Marital_Status', 'Income_Quintile', 'Weight']].head(10).to_string(index=False))
    
else:
    print("\n[오류] 조건을 만족하는 데이터가 없습니다.")
    print("\n사용 가능한 값들:")
    print(f"  연령대 샘플: {df['Age_Group'].unique()[:10].tolist()}")
    print(f"  성별: {df['Gender'].unique().tolist()}")
    print(f"  혼인상태: {df['Marital_Status'].unique().tolist()}")
