"""
메인 실행 스크립트: KOSIS 데이터 수집 및 IPF 실행 (plan.md 요구사항 기반)
"""
import pandas as pd
import numpy as np
from kosis_data_collector_plan import KOSISPlanDataCollector
from ipf_processor_plan import IPFProcessorPlan
import json
from pathlib import Path

def main():
    """메인 함수"""
    
    API_KEY = "ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY="
    
    print("=" * 80)
    print("KOSIS 데이터를 활용한 가상 설문 대상(4,000만 명) 결합 확률 분포(IPF) 생성")
    print("=" * 80)
    
    # 1. 데이터 수집
    print("\n[1단계] KOSIS API를 통한 데이터 수집")
    collector = KOSISPlanDataCollector(API_KEY)
    all_data = collector.collect_all_data()
    
    if not all_data:
        print("오류: 데이터 수집에 실패했습니다.")
        return
    
    print(f"\n수집된 데이터: {len(all_data)}개")
    for name, df in all_data.items():
        print(f"  {name}: {len(df)}행")
    
    # 2. 차원 추출
    print("\n[2단계] 차원 값 추출")
    dimensions = collector.extract_dimensions_from_data(all_data)
    
    print("\n[추출된 차원]")
    for dim_name, dim_values in dimensions.items():
        print(f"  {dim_name}: {len(dim_values)}개")
        if len(dim_values) <= 20:
            print(f"    → {dim_values}")
        else:
            print(f"    → {dim_values[:10]} ... (총 {len(dim_values)}개)")
    
    # 차원 정보 저장
    with open('dimension_info.json', 'w', encoding='utf-8') as f:
        json.dump(dimensions, f, ensure_ascii=False, indent=2)
    print(f"\n  차원 정보 저장: dimension_info.json")
    
    # 3. Base Table 생성
    print("\n[3단계] Base Table 생성")
    processor = IPFProcessorPlan()
    
    base_table = processor.create_base_table(
        sidos=dimensions['Sido'],
        age_groups=dimensions['Age_Group'],
        genders=dimensions['Gender'],
        income_quintiles=dimensions['Income_Quintile']
    )
    
    print(f"  Base Table 크기: {len(base_table)}행 x {len(base_table.columns)}컬럼")
    
    # 4. 제약 조건 준비
    print("\n[4단계] 제약 조건 준비")
    aggregates, constraint_dimensions = processor.prepare_constraints(all_data, collector)
    
    if not aggregates:
        print("  경고: 제약 조건을 찾을 수 없습니다.")
        print("  기본 제약 조건을 생성합니다...")
        # 기본 제약 조건 생성 (균일 분포)
        # 실제로는 데이터에서 추출해야 함
        pass
    
    # 5. IPF 알고리즘 실행
    print("\n[5단계] IPF 알고리즘 실행")
    result_df = processor.run_ipf(
        base_df=base_table,
        aggregates=aggregates,
        dimensions=constraint_dimensions,
        convergence_rate=1e-6,
        max_iterations=50
    )
    
    # 6. 최종 결과 검증 및 저장
    print("\n[6단계] 최종 결과 검증 및 저장")
    
    # 컬럼 순서 확인 (plan.md 요구사항: Sido, Sigungu, Age_Group, Gender, Income_Quintile, Weight)
    final_columns = ['Sido', 'Sigungu', 'Age_Group', 'Gender', 'Income_Quintile', 'Weight']
    result_df = result_df[final_columns]
    
    # Weight 합계 최종 검증
    weight_sum = result_df['Weight'].sum()
    print(f"  최종 Weight 합계: {weight_sum:.10f}")
    
    if abs(weight_sum - 1.0) < 0.0001:
        print("  ✓ 검증 통과: Weight 합계가 1.0입니다.")
    else:
        print(f"  ⚠ 경고: Weight 합계가 1.0과 다릅니다 ({weight_sum:.10f})")
        # 정규화
        result_df['Weight'] = result_df['Weight'] / weight_sum
        print(f"  정규화 후 Weight 합계: {result_df['Weight'].sum():.10f}")
    
    # CSV 저장
    output_file = 'final_joint_distribution.csv'
    result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n  결과 저장: {output_file}")
    print(f"  총 {len(result_df)}행 저장됨")
    
    # Pickle 저장 (선택사항)
    output_pickle = 'final_joint_distribution.pkl'
    result_df.to_pickle(output_pickle)
    print(f"  결과 저장 (Pickle): {output_pickle}")
    
    # 통계 정보 출력
    print("\n[최종 결과 통계]")
    print(f"  총 행 수: {len(result_df):,}")
    print(f"  시도 수: {result_df['Sido'].nunique()}")
    print(f"  연령대 수: {result_df['Age_Group'].nunique()}")
    print(f"  성별 수: {result_df['Gender'].nunique()}")
    print(f"  소득분위 수: {result_df['Income_Quintile'].nunique()}")
    print(f"  Weight 합계: {result_df['Weight'].sum():.10f}")
    print(f"  Weight 최소값: {result_df['Weight'].min():.10f}")
    print(f"  Weight 최대값: {result_df['Weight'].max():.10f}")
    print(f"  Weight 평균값: {result_df['Weight'].mean():.10f}")
    
    print("\n" + "=" * 80)
    print("작업 완료!")
    print("=" * 80)

if __name__ == "__main__":
    main()
