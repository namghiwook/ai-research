"""최종 결과 파일의 모든 차원별 고유 값 나열"""
import pandas as pd

# 최종 결과 파일 읽기
df = pd.read_csv('final_joint_distribution_extended.csv', encoding='utf-8-sig')

print("=" * 80)
print("최종 결과 파일의 모든 차원별 고유 값 목록")
print("=" * 80)

# Weight를 제외한 모든 컬럼 확인
columns = [col for col in df.columns if col != 'Weight']

for col in columns:
    print(f"\n[{col}]")
    print("-" * 80)
    
    unique_values = sorted(df[col].unique())
    print(f"총 {len(unique_values)}개:")
    
    # 성별은 특별히 처리
    if col == 'Gender':
        print("  - 남성 (남자)")
        print("  - 여성 (여자)")
    else:
        for i, value in enumerate(unique_values, 1):
            print(f"  {i:3d}. {value}")

print("\n" + "=" * 80)
print("요약")
print("=" * 80)
for col in columns:
    print(f"  {col}: {df[col].nunique()}개 고유 값")
