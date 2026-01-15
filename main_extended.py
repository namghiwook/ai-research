"""
확장된 KOSIS 데이터 기반 IPF 가상 인구 프로필 생성
모든 가능한 차원을 포함한 Cartesian Product 생성
"""
import pandas as pd
import numpy as np
from kosis_multi_data_collector import KOSISMultiDataCollector
from ipf_processor import IPFProcessor
import pickle
from itertools import product
import json

def create_extended_base_table(all_dimensions: dict, valid_pairs: list = None) -> pd.DataFrame:
    """
    모든 차원에 대한 확장된 Base Table 생성
    
    Args:
        all_dimensions: 모든 차원의 고유 값 딕셔너리
        valid_pairs: 유효한 시도-시군구 조합 리스트
        
    Returns:
        DataFrame: 확장된 Base 테이블
    """
    print("\n" + "=" * 80)
    print("확장된 Base Table 생성")
    print("=" * 80)
    
    # 필수 차원 확인 및 준비
    dimension_names = []
    dimension_values = []
    
    # 지역 차원 (필수)
    if 'Sido' in all_dimensions and all_dimensions['Sido']:
        dimension_names.append('Sido')
        dimension_values.append(all_dimensions['Sido'])
        print(f"  시도: {len(all_dimensions['Sido'])}개")
    
    if 'Sigungu' in all_dimensions and all_dimensions['Sigungu']:
        dimension_names.append('Sigungu')
        dimension_values.append(all_dimensions['Sigungu'])
        print(f"  시군구: {len(all_dimensions['Sigungu'])}개")
    
    # 연령 (필수)
    if 'Age_Group' in all_dimensions and all_dimensions['Age_Group']:
        # 연령대 형식 정규화
        age_groups = []
        for age in all_dimensions['Age_Group']:
            age_clean = str(age).replace('~', '-').replace('세', '').replace('이상', '+')
            if '85' in age_clean and '+' not in age_clean:
                age_clean = '85+'
            age_groups.append(age_clean)
        age_groups = sorted(list(set(age_groups)))
        dimension_names.append('Age_Group')
        dimension_values.append(age_groups)
        print(f"  연령대: {len(age_groups)}개")
    
    # 성별 (필수)
    if 'Gender' in all_dimensions and all_dimensions['Gender']:
        dimension_names.append('Gender')
        dimension_values.append(all_dimensions['Gender'])
        print(f"  성별: {len(all_dimensions['Gender'])}개")
    
    # 혼인상태 (선택)
    if 'Marital_Status' in all_dimensions and all_dimensions['Marital_Status']:
        dimension_names.append('Marital_Status')
        dimension_values.append(all_dimensions['Marital_Status'])
        print(f"  혼인상태: {len(all_dimensions['Marital_Status'])}개")
    
    # 교육정도 (선택)
    if 'Education' in all_dimensions and all_dimensions['Education']:
        dimension_names.append('Education')
        dimension_values.append(all_dimensions['Education'])
        print(f"  교육정도: {len(all_dimensions['Education'])}개")
    
    # 소득분위 (선택 - 기본값 사용)
    if 'Income_Quintile' not in dimension_names:
        income_quintiles = ['1분위', '2분위', '3분위', '4분위', '5분위']
        dimension_names.append('Income_Quintile')
        dimension_values.append(income_quintiles)
        print(f"  소득분위: {len(income_quintiles)}개 (기본값)")
    
    print(f"\n  총 차원 수: {len(dimension_names)}개")
    print(f"  차원 목록: {dimension_names}")
    
    # Cartesian Product 생성
    print("\n  Cartesian Product 생성 중...")
    all_combinations = list(product(*dimension_values))
    
    base_df = pd.DataFrame(all_combinations, columns=dimension_names)
    print(f"  생성된 조합 수: {len(base_df):,}개")
    
    # 유효한 시도-시군구 조합 필터링
    if valid_pairs and 'Sido' in base_df.columns and 'Sigungu' in base_df.columns:
        valid_pairs_set = set(valid_pairs)
        base_df['is_valid'] = base_df.apply(
            lambda row: (row['Sido'], row['Sigungu']) in valid_pairs_set,
            axis=1
        )
        base_df = base_df[base_df['is_valid']].drop('is_valid', axis=1)
        print(f"  필터링 후: {len(base_df):,}개")
    
    # 초기 가중치 할당
    initial_weight = 1.0 / len(base_df)
    base_df['total'] = initial_weight
    
    print(f"  초기 가중치 합계: {base_df['total'].sum():.6f}")
    
    return base_df.reset_index(drop=True)

def main():
    """메인 함수"""
    
    API_KEY = "ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY="
    
    print("=" * 80)
    print("확장된 KOSIS 데이터 기반 IPF 가상 인구 프로필 생성")
    print("모든 가능한 차원 포함")
    print("=" * 80)
    
    # 1. 모든 데이터 수집
    print("\n[1단계] 모든 KOSIS 데이터 수집")
    collector = KOSISMultiDataCollector(API_KEY)
    all_dimensions = collector.collect_all_data()
    
    print("\n" + "=" * 80)
    print("[통합 차원 요약]")
    print("=" * 80)
    for dim_name, dim_values in all_dimensions.items():
        print(f"  {dim_name}: {len(dim_values)}개")
        if len(dim_values) <= 10:
            print(f"    → {dim_values}")
        else:
            print(f"    → {dim_values[:5]} ... (총 {len(dim_values)}개)")
    
    # 2. 확장된 Base Table 생성
    print("\n[2단계] 확장된 Base Table 생성")
    base_table = create_extended_base_table(all_dimensions)
    
    # 차원 정보 저장
    dimension_info = {
        'dimension_names': list(base_table.columns),
        'dimension_counts': {col: base_table[col].nunique() for col in base_table.columns if col != 'total'}
    }
    
    with open('dimension_info.json', 'w', encoding='utf-8') as f:
        json.dump(dimension_info, f, ensure_ascii=False, indent=2)
    print(f"\n  차원 정보 저장: dimension_info.json")
    
    # 3. 제약 조건 준비
    print("\n[3단계] 제약 조건 준비")
    processor = IPFProcessor()
    
    # 제약 조건 데이터 준비 (수집된 데이터 중 사용 가능한 것들)
    aggregates = []
    dimensions_list = []
    
    # 제약 조건 1: 시군구 x 성별 x 연령 (가능한 경우)
    if '연령성별혼인상태' in collector.all_data:
        df = collector.all_data['연령성별혼인상태']
        df_cleaned = collector.clean_data(df)
        
        # 데이터 변환
        constraint_data = []
        for _, row in df_cleaned.iterrows():
            if row['C1_NM'] == '전국' or row['C2_NM'] == '합계':
                continue
            
            dt_value = row['DT']
            try:
                value = int(dt_value) if str(dt_value) not in ['-', '', 'nan'] else 0
            except:
                value = 0
            
            if value == 0:
                continue
            
            sido = row['C1_NM']
            age_group = str(row['C2_NM']).replace('~', '-').replace('세', '').replace('이상', '+')
            itm_nm = str(row['ITM_NM'])
            
            gender = None
            if '남자' in itm_nm:
                gender = '남자'
            elif '여자' in itm_nm:
                gender = '여자'
            
            if gender:
                constraint_data.append({
                    'Sigungu': sido,
                    'Gender': gender,
                    'Age_Group': age_group,
                    'value': value
                })
        
        if constraint_data:
            constraint_df = pd.DataFrame(constraint_data)
            constraint_agg = constraint_df.groupby(['Sigungu', 'Gender', 'Age_Group'])['value'].sum().reset_index()
            constraint_agg = processor.normalize_constraints(constraint_agg, 'value')
            aggregates.append(constraint_agg)
            dimensions_list.append(['Sigungu', 'Gender', 'Age_Group'])
            print(f"  제약 조건 1 추가: 시군구 x 성별 x 연령 ({len(constraint_agg)}행)")
    
    # 제약 조건 2: 연령 x 소득분위 (기본값 또는 실제 데이터)
    age_groups = base_table['Age_Group'].unique()
    income_quintiles = ['1분위', '2분위', '3분위', '4분위', '5분위']
    
    # 균등 분포로 제약 조건 생성 (실제 데이터가 없을 경우)
    constraint2_data = []
    for age in age_groups:
        for income in income_quintiles:
            constraint2_data.append({
                'Age_Group': age,
                'Income_Quintile': income,
                'value': 1.0 / (len(age_groups) * len(income_quintiles))
            })
    
    constraint2_df = pd.DataFrame(constraint2_data)
    aggregates.append(constraint2_df)
    dimensions_list.append(['Age_Group', 'Income_Quintile'])
    print(f"  제약 조건 2 추가: 연령 x 소득분위 ({len(constraint2_df)}행)")
    
    # 4. IPF 실행
    if aggregates:
        print("\n[4단계] IPF 알고리즘 실행")
        result_df = processor.run_ipf(
            base_table,
            aggregates,
            dimensions_list,
            convergence_rate=1e-6,
            max_iterations=50
        )
        
        # 5. 결과 저장
        print("\n[5단계] 결과 저장")
        output_file_csv = "final_joint_distribution_extended.csv"
        result_df.to_csv(output_file_csv, index=False, encoding='utf-8-sig')
        print(f"  CSV 저장: {output_file_csv}")
        
        output_file_pkl = "final_joint_distribution_extended.pkl"
        with open(output_file_pkl, 'wb') as f:
            pickle.dump(result_df, f)
        print(f"  Pickle 저장: {output_file_pkl}")
        
        # 최종 검증
        print("\n" + "=" * 80)
        print("[최종 검증]")
        print("=" * 80)
        weight_sum = result_df['Weight'].sum()
        print(f"  Weight 합계: {weight_sum:.6f}")
        print(f"  총 행 수: {len(result_df):,}행")
        print(f"  컬럼: {list(result_df.columns)}")
        print(f"  Weight 범위: {result_df['Weight'].min():.8f} ~ {result_df['Weight'].max():.8f}")
        
        print("\n처리 완료!")
    else:
        print("\n경고: 제약 조건이 없어 IPF를 실행할 수 없습니다.")

if __name__ == "__main__":
    main()
