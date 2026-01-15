"""
메인 실행 스크립트: KOSIS 데이터 수집 및 IPF 실행
"""
import pandas as pd
import numpy as np
from kosis_data_collector import KOSISDataCollector
from ipf_processor import IPFProcessor
import pickle
from pathlib import Path
import sys

def main(use_sample_data=True):
    """
    메인 함수
    
    Args:
        use_sample_data: True면 샘플 데이터 사용, False면 KOSIS API 사용
    """
    # API 키 설정
    API_KEY = "ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY="
    
    # 최신 연도 설정 (2020~2024)
    YEAR = "2023"
    
    print("=" * 80)
    print("KOSIS 데이터 기반 IPF 가상 인구 프로필 생성")
    print("=" * 80)
    
    # 1. 데이터 수집
    if use_sample_data:
        print("\n[1단계] 샘플 데이터 사용")
        try:
            base_df = pd.read_csv("sample_base_data.csv", encoding='utf-8-sig')
            constraint1_df = pd.read_csv("sample_constraint1_data.csv", encoding='utf-8-sig')
            constraint2_df = pd.read_csv("sample_constraint2_data.csv", encoding='utf-8-sig')
            print("샘플 데이터 로드 완료")
        except FileNotFoundError:
            print("오류: 샘플 데이터 파일을 찾을 수 없습니다.")
            print("먼저 'python create_sample_data.py'를 실행하세요.")
            return
    else:
        print("\n[1단계] KOSIS API를 통한 데이터 수집 시작")
        collector = KOSISDataCollector(API_KEY)
        
        base_df = collector.fetch_base_population_data(YEAR)
        constraint1_df = collector.fetch_constraint1_data(YEAR)
        constraint2_df = collector.fetch_constraint2_data(YEAR)
    
    # 데이터 클리닝
    print("\n[1-1단계] 데이터 클리닝")
    collector = KOSISDataCollector(API_KEY) if not use_sample_data else KOSISDataCollector("")
    
    base_df_cleaned = collector.clean_data(base_df)
    constraint1_df_cleaned = collector.clean_data(constraint1_df)
    constraint2_df_cleaned = collector.clean_data(constraint2_df)
    
    print(f"클리닝 완료 - Base: {len(base_df_cleaned)}행, 제약조건1: {len(constraint1_df_cleaned)}행, 제약조건2: {len(constraint2_df_cleaned)}행")
    
    # 데이터 수집 결과 확인
    print("\n" + "=" * 80)
    print("[데이터 수집 결과 확인]")
    print("=" * 80)
    print(f"\nBase 데이터:")
    if not base_df_cleaned.empty:
        print(f"  - 행 수: {len(base_df_cleaned)}")
        print(f"  - 컬럼: {list(base_df_cleaned.columns)}")
        print(f"  - 샘플 데이터:")
        print(base_df_cleaned.head(3))
        
        # 오류 응답인지 확인
        if 'err' in base_df_cleaned.columns or 'errMsg' in base_df_cleaned.columns:
            print("\n[오류] KOSIS API 호출 실패:")
            print(base_df_cleaned.to_string())
            print("\nKOSIS API 호출에 실패했습니다. 샘플 데이터를 사용하여 계속 진행합니다.")
            print("샘플 데이터로 전환 중...")
            
            # 샘플 데이터로 fallback
            try:
                base_df_cleaned = pd.read_csv("sample_base_data.csv", encoding='utf-8-sig')
                constraint1_df_cleaned = pd.read_csv("sample_constraint1_data.csv", encoding='utf-8-sig')
                constraint2_df_cleaned = pd.read_csv("sample_constraint2_data.csv", encoding='utf-8-sig')
                collector = KOSISDataCollector("")
                base_df_cleaned = collector.clean_data(base_df_cleaned)
                constraint1_df_cleaned = collector.clean_data(constraint1_df_cleaned)
                constraint2_df_cleaned = collector.clean_data(constraint2_df_cleaned)
                print("샘플 데이터 로드 완료")
            except FileNotFoundError:
                print("오류: 샘플 데이터 파일도 찾을 수 없습니다.")
                print("먼저 'python create_sample_data.py'를 실행하세요.")
                return
    else:
        print("  - 데이터가 비어있습니다.")
        print("\nKOSIS API 호출 실패. 샘플 데이터로 전환 중...")
        
        # 샘플 데이터로 fallback
        try:
            base_df_cleaned = pd.read_csv("sample_base_data.csv", encoding='utf-8-sig')
            constraint1_df_cleaned = pd.read_csv("sample_constraint1_data.csv", encoding='utf-8-sig')
            constraint2_df_cleaned = pd.read_csv("sample_constraint2_data.csv", encoding='utf-8-sig')
            collector = KOSISDataCollector("")
            base_df_cleaned = collector.clean_data(base_df_cleaned)
            constraint1_df_cleaned = collector.clean_data(constraint1_df_cleaned)
            constraint2_df_cleaned = collector.clean_data(constraint2_df_cleaned)
            print("샘플 데이터 로드 완료")
        except FileNotFoundError:
            print("오류: 샘플 데이터 파일도 찾을 수 없습니다.")
            print("먼저 'python create_sample_data.py'를 실행하세요.")
            return
    
    # 데이터가 충분히 수집되었는지 확인
    if base_df_cleaned.empty or constraint1_df_cleaned.empty or constraint2_df_cleaned.empty:
        print("\n[오류] 필수 데이터가 부족합니다. 처리할 수 없습니다.")
        return
    
    # 필수 컬럼 확인
    required_cols_base = ['Sido', 'Sigungu', 'Age_Group', 'Gender']
    missing_cols = [col for col in required_cols_base if col not in base_df_cleaned.columns]
    if missing_cols:
        print(f"\n[오류] Base 데이터에 필수 컬럼이 없습니다: {missing_cols}")
        print(f"현재 컬럼: {list(base_df_cleaned.columns)}")
        return
    
    # 2. IPF 처리
    print("\n" + "=" * 80)
    print("[2단계] IPF 처리 시작")
    print("=" * 80)
    
    processor = IPFProcessor()
    
    # Base 테이블 생성을 위한 고유 값 추출
    print("\n[2-1단계] 고유 값 추출")
    sidos = sorted(base_df_cleaned['Sido'].unique().tolist())
    sigungus = sorted(base_df_cleaned['Sigungu'].unique().tolist())
    age_groups = sorted(base_df_cleaned['Age_Group'].unique().tolist())
    genders = sorted(base_df_cleaned['Gender'].unique().tolist())
    
    # 유효한 시도-시군구 조합 추출
    valid_pairs = list(zip(base_df_cleaned['Sido'], base_df_cleaned['Sigungu']))
    valid_pairs = list(set(valid_pairs))
    
    # 소득분위 추출 (제약 조건 2에서)
    income_quintiles = sorted(constraint2_df_cleaned['Income_Quintile'].unique().tolist())
    
    print(f"시도 수: {len(sidos)}, 시군구 수: {len(sigungus)}")
    print(f"연령대 수: {len(age_groups)}, 성별 수: {len(genders)}, 소득분위 수: {len(income_quintiles)}")
    print(f"유효한 시도-시군구 조합 수: {len(valid_pairs)}")
    
    # Base 테이블 생성
    print("\n[2-2단계] Base Table 생성")
    base_table = processor.create_base_table(
        sidos=sidos,
        sigungus=sigungus,
        age_groups=age_groups,
        genders=genders,
        income_quintiles=income_quintiles,
        valid_sido_sigungu_pairs=valid_pairs
    )
    
    # 제약 조건 준비
    print("\n[2-3단계] 제약 조건 준비")
    
    # 제약 조건 1: 시군구 x 성별 x 연령별 집계
    constraint1_agg = constraint1_df_cleaned.groupby(['Sigungu', 'Gender', 'Age_Group'])['value'].sum().reset_index()
    constraint1_agg = processor.normalize_constraints(constraint1_agg, 'value')
    
    print(f"제약 조건 1 집계: {len(constraint1_agg)}행, 합계: {constraint1_agg['value'].sum():.6f}")
    
    # 제약 조건 2 정규화 확인
    if constraint2_df_cleaned['value'].sum() != 1.0:
        constraint2_agg = processor.normalize_constraints(constraint2_df_cleaned, 'value')
    else:
        constraint2_agg = constraint2_df_cleaned.copy()
    
    print(f"제약 조건 2: {len(constraint2_agg)}행, 합계: {constraint2_agg['value'].sum():.6f}")
    
    # IPF 실행
    print("\n[2-4단계] IPF 알고리즘 실행")
    aggregates = [constraint1_agg, constraint2_agg]
    dimensions = [
        ['Sigungu', 'Gender', 'Age_Group'],
        ['Age_Group', 'Income_Quintile']
    ]
    
    result_df = processor.run_ipf(
        base_table,
        aggregates,
        dimensions,
        convergence_rate=1e-6,
        max_iterations=50
    )
    
    # 최종 결과 저장
    print("\n" + "=" * 80)
    print("[3단계] 결과 저장")
    print("=" * 80)
    
    # CSV 저장
    output_file_csv = "final_joint_distribution.csv"
    result_df.to_csv(output_file_csv, index=False, encoding='utf-8-sig')
    print(f"\n[저장 완료] CSV 파일: {output_file_csv}")
    
    # Pickle 저장
    output_file_pkl = "final_joint_distribution.pkl"
    with open(output_file_pkl, 'wb') as f:
        pickle.dump(result_df, f)
    print(f"[저장 완료] Pickle 파일: {output_file_pkl}")
    
    # 최종 검증
    print("\n" + "=" * 80)
    print("[최종 검증]")
    print("=" * 80)
    weight_sum = result_df['Weight'].sum()
    print(f"Weight 합계: {weight_sum:.6f}")
    
    if abs(weight_sum - 1.0) < 0.01:
        print("[검증 통과] Weight 합계가 1.0에 가깝습니다.")
    else:
        print(f"[검증 실패] Weight 합계가 1.0과 차이가 있습니다 ({weight_sum:.6f})")
    
    print(f"\n결과 데이터 정보:")
    print(f"  - 총 행 수: {len(result_df):,}행")
    print(f"  - 컬럼: {list(result_df.columns)}")
    print(f"  - Weight 범위: {result_df['Weight'].min():.8f} ~ {result_df['Weight'].max():.8f}")
    print(f"  - Weight 평균: {result_df['Weight'].mean():.8f}")
    
    print("\n최종 결과 샘플 (처음 10행):")
    print(result_df.head(10).to_string(index=False))
    
    print("\n" + "=" * 80)
    print("처리 완료!")
    print("=" * 80)

if __name__ == "__main__":
    # 명령행 인자로 샘플 데이터 사용 여부 결정
    use_sample = True  # 기본값: 샘플 데이터 사용
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == 'kosis':
            use_sample = False
    
    main(use_sample_data=use_sample)
