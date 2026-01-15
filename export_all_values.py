"""모든 차원의 고유 값을 파일로 출력"""
import pandas as pd
import json

# 최종 결과 파일 읽기
df = pd.read_csv('final_joint_distribution_extended.csv', encoding='utf-8-sig')

result = {}

# Weight를 제외한 모든 컬럼
columns = [col for col in df.columns if col != 'Weight']

for col in columns:
    unique_values = sorted(df[col].unique().tolist())
    result[col] = unique_values

# JSON으로 저장
with open('all_dimension_values.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# 텍스트 파일로도 저장
with open('all_dimension_values.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("최종 결과 파일의 모든 차원별 고유 값 목록\n")
    f.write("=" * 80 + "\n\n")
    
    for col in columns:
        f.write(f"[{col}]\n")
        f.write("-" * 80 + "\n")
        f.write(f"총 {len(result[col])}개:\n")
        
        if col == 'Gender':
            f.write("  - 남성 (남자)\n")
            f.write("  - 여성 (여자)\n")
        else:
            for i, value in enumerate(result[col], 1):
                f.write(f"  {i:3d}. {value}\n")
        f.write("\n")
    
    f.write("=" * 80 + "\n")
    f.write("요약\n")
    f.write("=" * 80 + "\n")
    for col in columns:
        f.write(f"  {col}: {len(result[col])}개 고유 값\n")

print("파일 저장 완료:")
print("  - all_dimension_values.json")
print("  - all_dimension_values.txt")

# 화면 출력
print("\n" + "=" * 80)
print("최종 결과 파일의 모든 차원별 고유 값 목록")
print("=" * 80)

for col in columns:
    print(f"\n[{col}]")
    print("-" * 80)
    print(f"총 {len(result[col])}개:")
    
    if col == 'Gender':
        print("  - 남성 (남자)")
        print("  - 여성 (여자)")
    else:
        for i, value in enumerate(result[col], 1):
            print(f"  {i:3d}. {value}")
