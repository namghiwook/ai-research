"""
Iterative Proportional Fitting (IPF) 알고리즘 구현
"""
import pandas as pd
import numpy as np
try:
    from ipfn import ipfn
except ImportError:
    import ipfn
from typing import List, Dict, Tuple

class IPFProcessor:
    def __init__(self):
        """IPF 프로세서 초기화"""
        pass
    
    def create_base_table(self, 
                         sidos: List[str],
                         sigungus: List[str],
                         age_groups: List[str],
                         genders: List[str],
                         income_quintiles: List[str],
                         valid_sido_sigungu_pairs: List[Tuple[str, str]] = None) -> pd.DataFrame:
        """
        Base Table 생성: Cartesian Product
        
        Args:
            sidos: 시도 리스트
            sigungus: 시군구 리스트
            age_groups: 연령대 리스트
            genders: 성별 리스트
            income_quintiles: 소득분위 리스트
            valid_sido_sigungu_pairs: 유효한 (시도, 시군구) 조합 리스트
            
        Returns:
            DataFrame: Base 테이블
        """
        print("Base Table 생성 중...")
        
        # Cartesian Product 생성
        from itertools import product
        
        all_combinations = list(product(sidos, sigungus, age_groups, genders, income_quintiles))
        
        base_df = pd.DataFrame(all_combinations, columns=[
            'Sido', 'Sigungu', 'Age_Group', 'Gender', 'Income_Quintile'
        ])
        
        # 유효한 시도-시군구 조합만 필터링
        if valid_sido_sigungu_pairs:
            valid_pairs_set = set(valid_sido_sigungu_pairs)
            base_df['is_valid'] = base_df.apply(
                lambda row: (row['Sido'], row['Sigungu']) in valid_pairs_set,
                axis=1
            )
            base_df = base_df[base_df['is_valid']].drop('is_valid', axis=1)
            print(f"유효한 시도-시군구 조합으로 필터링: {len(base_df)}행")
        
        # 초기 가중치 할당 (균일 분포)
        initial_weight = 1.0 / len(base_df)
        base_df['total'] = initial_weight
        
        print(f"Base Table 생성 완료: {len(base_df)}행")
        print(f"초기 가중치 합계: {base_df['total'].sum():.6f}")
        
        return base_df.reset_index(drop=True)
    
    def normalize_constraints(self, df: pd.DataFrame, value_col: str) -> pd.DataFrame:
        """
        제약 조건 데이터 정규화 (전체 합계 = 1.0)
        
        Args:
            df: 제약 조건 데이터프레임
            value_col: 값 컬럼명
            
        Returns:
            DataFrame: 정규화된 데이터프레임
        """
        df_normalized = df.copy()
        total_sum = df_normalized[value_col].sum()
        
        if total_sum > 0:
            df_normalized[value_col] = df_normalized[value_col] / total_sum
            print(f"제약 조건 정규화 완료 (합계: {df_normalized[value_col].sum():.6f})")
        else:
            print("경고: 제약 조건 합계가 0입니다.")
        
        return df_normalized
    
    def prepare_constraints(self, 
                           constraint1_df: pd.DataFrame,
                           constraint2_df: pd.DataFrame,
                           base_df: pd.DataFrame) -> Tuple[List, List, List]:
        """
        IPF 알고리즘을 위한 제약 조건 준비
        
        Args:
            constraint1_df: 제약 조건 1 데이터 (시군구 x 성별 x 연령)
            constraint2_df: 제약 조건 2 데이터 (연령 x 소득분위)
            base_df: Base 테이블
            
        Returns:
            Tuple: (aggregates 리스트, dimensions 리스트, convergence_rate)
        """
        aggregates = []
        dimensions = []
        
        # 제약 조건 1: 시군구 x 성별 x 연령
        if not constraint1_df.empty:
            print("제약 조건 1 준비 중...")
            # constraint1_df를 long format으로 변환하고 정규화
            # 실제 컬럼명은 데이터 구조에 따라 조정 필요
            constraint1_normalized = self.normalize_constraints(
                constraint1_df, 
                'value'  # 실제 값 컬럼명에 맞게 수정 필요
            )
            aggregates.append(constraint1_normalized)
            dimensions.append(['Sigungu', 'Gender', 'Age_Group'])
        
        # 제약 조건 2: 연령 x 소득분위
        if not constraint2_df.empty:
            print("제약 조건 2 준비 중...")
            constraint2_normalized = self.normalize_constraints(
                constraint2_df,
                'value'  # 실제 값 컬럼명에 맞게 수정 필요
            )
            aggregates.append(constraint2_normalized)
            dimensions.append(['Age_Group', 'Income_Quintile'])
        
        convergence_rate = 1e-6
        
        return aggregates, dimensions, convergence_rate
    
    def run_ipf(self, 
                base_df: pd.DataFrame,
                aggregates: List[pd.DataFrame],
                dimensions: List[List[str]],
                convergence_rate: float = 1e-6,
                max_iterations: int = 50) -> pd.DataFrame:
        """
        IPF 알고리즘 직접 구현
        
        Args:
            base_df: Base 테이블
            aggregates: 제약 조건 리스트 (각 DataFrame에 'total' 또는 'value' 컬럼 필요)
            dimensions: 각 제약 조건의 차원 리스트
            convergence_rate: 수렴 기준
            max_iterations: 최대 반복 횟수
            
        Returns:
            DataFrame: IPF 결과
        """
        print("IPF 알고리즘 실행 중 (직접 구현)...")
        
        result_df = base_df.copy()
        weight_col = 'total'
        
        for iteration in range(max_iterations):
            max_diff = 0.0
            
            # 각 제약 조건에 대해 순차적으로 적용
            for agg_df, dims in zip(aggregates, dimensions):
                # 제약 조건의 값 컬럼 찾기
                value_col = 'total' if 'total' in agg_df.columns else 'value'
                
                # Base table을 차원별로 그룹화하여 합계 계산
                group_sum = result_df.groupby(dims)[weight_col].sum().reset_index()
                group_sum = group_sum.rename(columns={weight_col: 'current_sum'})
                
                # 제약 조건과 합치기
                merged = group_sum.merge(agg_df, on=dims, how='inner')
                
                # 비율 계산 (목표값 / 현재값), 0으로 나누기 방지
                merged['ratio'] = merged[value_col] / (merged['current_sum'] + 1e-10)
                
                # Base table과 합치기
                result_df = result_df.merge(merged[dims + ['ratio']], on=dims, how='left')
                result_df['ratio'] = result_df['ratio'].fillna(1.0)
                
                # 가중치 업데이트
                result_df[weight_col] = result_df[weight_col] * result_df['ratio']
                
                # 최대 차이 업데이트
                max_diff = max(max_diff, abs(merged['ratio'] - 1.0).max())
                
                # 임시 컬럼 제거
                result_df = result_df.drop('ratio', axis=1)
            
            # 수렴 확인
            if max_diff < convergence_rate:
                print(f"  수렴 완료 (반복 {iteration + 1}회, 최대 차이: {max_diff:.8f})")
                break
            
            if (iteration + 1) % 10 == 0:
                print(f"  반복 {iteration + 1}회, 최대 차이: {max_diff:.8f}")
        
        if iteration == max_iterations - 1:
            print(f"  최대 반복 횟수 도달 ({max_iterations}회)")
        
        # Weight 컬럼으로 이름 변경
        if weight_col == 'total':
            result_df = result_df.rename(columns={'total': 'Weight'})
        
        # Weight 합계 검증
        weight_sum = result_df['Weight'].sum()
        print(f"IPF 완료. 최종 Weight 합계: {weight_sum:.6f}")
        
        if abs(weight_sum - 1.0) > 0.01:
            print(f"경고: Weight 합계가 1.0과 차이가 있습니다 ({weight_sum:.6f})")
        else:
            print("검증 통과: Weight 합계가 1.0에 가깝습니다.")
        
        return result_df
