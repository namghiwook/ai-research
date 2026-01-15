"""
샘플 데이터를 사용한 IPF 로직 테스트
"""
import pandas as pd
import numpy as np
from ipf_processor import IPFProcessor
from kosis_data_collector import KOSISDataCollector

def test_ipf_with_sample():
    """샘플 데이터로 IPF 테스트"""
    
    print("=" * 80)
    print("샘플 데이터를 사용한 IPF 테스트")
    print("=" * 80)
    
    # 샘플 데이터 로드
    print("\n[1] 샘플 데이터 로드")
    print("-" * 80)
    
    try:
        base_df = pd.read_csv("sample_base_data.csv", encoding='utf-8-sig')
        constraint1_df = pd.read_csv("sample_constraint1_data.csv", encoding='utf-8-sig')
        constraint2_df = pd.read_csv("sample_constraint2_data.csv", encoding='utf-8-sig')
        
        print(f"Base 데이터: {len(base_df)}행")
        print(f"제약 조건 1: {len(constraint1_df)}행")
        print(f"제약 조건 2: {len(constraint2_df)}행")
    except FileNotFoundError:
        print("샘플 데이터 파일을 찾을 수 없습니다. 먼저 create_sample_data.py를 실행하세요.")
        return
    
    # 데이터 클리닝
    print("\n[2] 데이터 클리닝")
    print("-" * 80)
    collector = KOSISDataCollector("")
    
    base_df_cleaned = collector.clean_data(base_df)
    constraint1_df_cleaned = collector.clean_data(constraint1_df)
    constraint2_df_cleaned = collector.clean_data(constraint2_df)
    
    print(f"클리닝 후 Base 데이터: {len(base_df_cleaned)}행")
    print(f"클리닝 후 제약 조건 1: {len(constraint1_df_cleaned)}행")
    print(f"클리닝 후 제약 조건 2: {len(constraint2_df_cleaned)}행")
    
    # Base 테이블 생성을 위한 고유 값 추출
    print("\n[3] Base Table 생성 준비")
    print("-" * 80)
    
    sidos = sorted(base_df_cleaned['Sido'].unique().tolist())
    sigungus = sorted(base_df_cleaned['Sigungu'].unique().tolist())
    age_groups = sorted(base_df_cleaned['Age_Group'].unique().tolist())
    genders = sorted(base_df_cleaned['Gender'].unique().tolist())
    
    # 유효한 시도-시군구 조합 추출
    valid_pairs = list(zip(base_df_cleaned['Sido'], base_df_cleaned['Sigungu']))
    valid_pairs = list(set(valid_pairs))
    
    print(f"시도 수: {len(sidos)}")
    print(f"시군구 수: {len(sigungus)}")
    print(f"연령대 수: {len(age_groups)}")
    print(f"성별 수: {len(genders)}")
    print(f"유효한 시도-시군구 조합 수: {len(valid_pairs)}")
    
    # 소득분위 추출 (제약 조건 2에서)
    income_quintiles = sorted(constraint2_df_cleaned['Income_Quintile'].unique().tolist())
    print(f"소득분위 수: {len(income_quintiles)}")
    
    # Base Table 생성
    print("\n[4] Base Table 생성")
    print("-" * 80)
    
    processor = IPFProcessor()
    base_table = processor.create_base_table(
        sidos=sidos,
        sigungus=sigungus,
        age_groups=age_groups,
        genders=genders,
        income_quintiles=income_quintiles,
        valid_sido_sigungu_pairs=valid_pairs
    )
    
    print(f"\n생성된 Base Table: {len(base_table)}행")
    print(f"예상 조합 수: {len(sidos)} * {len(sigungus)} * {len(age_groups)} * {len(genders)} * {len(income_quintiles)} = {len(sidos) * len(sigungus) * len(age_groups) * len(genders) * len(income_quintiles)}")
    
    # 제약 조건 준비
    print("\n[5] 제약 조건 준비")
    print("-" * 80)
    
    # 제약 조건 1: 시군구 x 성별 x 연령별 집계
    constraint1_agg = constraint1_df_cleaned.groupby(['Sigungu', 'Gender', 'Age_Group'])['value'].sum().reset_index()
    constraint1_agg = processor.normalize_constraints(constraint1_agg, 'value')
    
    print(f"제약 조건 1 집계: {len(constraint1_agg)}행")
    print(f"합계: {constraint1_agg['value'].sum():.6f}")
    
    # 제약 조건 2는 이미 정규화되어 있을 수 있음 (확인)
    if constraint2_df_cleaned['value'].sum() != 1.0:
        constraint2_agg = processor.normalize_constraints(constraint2_df_cleaned, 'value')
    else:
        constraint2_agg = constraint2_df_cleaned.copy()
    
    print(f"제약 조건 2: {len(constraint2_agg)}행")
    print(f"합계: {constraint2_agg['value'].sum():.6f}")
    
    # IPF 실행 준비
    print("\n[6] IPF 알고리즘 실행")
    print("-" * 80)
    
    aggregates = [constraint1_agg, constraint2_agg]
    dimensions = [
        ['Sigungu', 'Gender', 'Age_Group'],
        ['Age_Group', 'Income_Quintile']
    ]
    
    try:
        result_df = processor.run_ipf(
            base_table,
            aggregates,
            dimensions,
            convergence_rate=1e-6,
            max_iterations=50
        )
        
        # 결과 저장
        print("\n[7] 결과 저장")
        print("-" * 80)
        
        result_df.to_csv("test_ipf_result.csv", index=False, encoding='utf-8-sig')
        print("결과가 'test_ipf_result.csv'에 저장되었습니다.")
        
        # 결과 요약
        print("\n[8] 결과 요약")
        print("-" * 80)
        print(f"총 행 수: {len(result_df)}")
        print(f"Weight 합계: {result_df['Weight'].sum():.6f}")
        print(f"Weight 최소값: {result_df['Weight'].min():.6f}")
        print(f"Weight 최대값: {result_df['Weight'].max():.6f}")
        print(f"Weight 평균값: {result_df['Weight'].mean():.6f}")
        
        print("\n처음 10행:")
        print(result_df.head(10))
        
        print("\n[성공] IPF 테스트 완료!")
        
    except Exception as e:
        print(f"\n[오류] IPF 실행 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ipf_with_sample()
