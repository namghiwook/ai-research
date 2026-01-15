"""
데이터 수집 테스트 스크립트
데이터 수집 결과를 먼저 확인하기 위한 스크립트
"""
import pandas as pd
from kosis_data_collector import KOSISDataCollector

def test_data_collection():
    """데이터 수집 테스트 및 결과 확인"""
    
    # API 키 설정
    API_KEY = "ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY="
    
    # 최신 연도 설정 (2020~2024)
    YEAR = "2023"
    
    print("=" * 80)
    print("KOSIS 데이터 수집 테스트")
    print("=" * 80)
    
    collector = KOSISDataCollector(API_KEY)
    
    # 각 데이터 수집 테스트
    print("\n[1] Base 데이터 수집 테스트")
    print("-" * 80)
    base_df = collector.fetch_base_population_data(YEAR)
    
    if not base_df.empty:
        print(f"\n[성공] Base 데이터 수집 성공: {len(base_df)}행")
        print(f"\n컬럼 목록:")
        for i, col in enumerate(base_df.columns, 1):
            print(f"  {i}. {col}")
        
        print(f"\n데이터 타입:")
        print(base_df.dtypes)
        
        print(f"\n처음 5행:")
        print(base_df.head())
        
        print(f"\n고유값 확인:")
        for col in base_df.columns:
            if base_df[col].dtype == 'object':
                unique_count = base_df[col].nunique()
                print(f"  {col}: {unique_count}개 고유값")
                if unique_count <= 20:
                    print(f"    → {sorted(base_df[col].unique().tolist())}")
    else:
        print("[실패] Base 데이터 수집 실패 또는 데이터 없음")
        print("\n참고: 실제 통계표ID와 파라미터를 확인해야 할 수 있습니다.")
    
    print("\n" + "=" * 80)
    print("[2] 제약 조건 1 데이터 수집 테스트")
    print("-" * 80)
    constraint1_df = collector.fetch_constraint1_data(YEAR)
    
    if not constraint1_df.empty:
        print(f"\n[성공] 제약 조건 1 데이터 수집 성공: {len(constraint1_df)}행")
        print(f"\n컬럼 목록:")
        for i, col in enumerate(constraint1_df.columns, 1):
            print(f"  {i}. {col}")
        
        print(f"\n처음 5행:")
        print(constraint1_df.head())
    else:
        print("[실패] 제약 조건 1 데이터 수집 실패 또는 데이터 없음")
    
    print("\n" + "=" * 80)
    print("[3] 제약 조건 2 데이터 수집 테스트")
    print("-" * 80)
    constraint2_df = collector.fetch_constraint2_data(YEAR)
    
    if not constraint2_df.empty:
        print(f"\n[성공] 제약 조건 2 데이터 수집 성공: {len(constraint2_df)}행")
        print(f"\n컬럼 목록:")
        for i, col in enumerate(constraint2_df.columns, 1):
            print(f"  {i}. {col}")
        
        print(f"\n처음 5행:")
        print(constraint2_df.head())
    else:
        print("[실패] 제약 조건 2 데이터 수집 실패 또는 데이터 없음")
    
    # 데이터 저장 (확인용)
    if not base_df.empty:
        base_df.to_csv("collected_base_data.csv", index=False, encoding='utf-8-sig')
        print(f"\nBase 데이터가 'collected_base_data.csv'에 저장되었습니다.")
    
    if not constraint1_df.empty:
        constraint1_df.to_csv("collected_constraint1_data.csv", index=False, encoding='utf-8-sig')
        print(f"제약 조건 1 데이터가 'collected_constraint1_data.csv'에 저장되었습니다.")
    
    if not constraint2_df.empty:
        constraint2_df.to_csv("collected_constraint2_data.csv", index=False, encoding='utf-8-sig')
        print(f"제약 조건 2 데이터가 'collected_constraint2_data.csv'에 저장되었습니다.")
    
    print("\n" + "=" * 80)
    print("테스트 완료")
    print("=" * 80)

if __name__ == "__main__":
    test_data_collection()
