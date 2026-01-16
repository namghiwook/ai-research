"""
Iterative Proportional Fitting (IPF) 알고리즘 구현 (plan.md 요구사항 기반)
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from itertools import product

class IPFProcessorPlan:
    def __init__(self):
        """IPF 프로세서 초기화"""
        pass
    
    def create_base_table(self, 
                         sidos: List[str],
                         age_groups: List[str],
                         genders: List[str],
                         income_quintiles: List[str]) -> pd.DataFrame:
        """
        Base Table 생성: Cartesian Product
        plan.md 요구사항: 시군구는 제외하고 시도만 사용
        
        Args:
            sidos: 시도 리스트
            age_groups: 연령대 리스트
            genders: 성별 리스트
            income_quintiles: 소득분위 리스트
            
        Returns:
            DataFrame: Base 테이블 (Sido, Age_Group, Gender, Income_Quintile, total)
        """
        print("\n[Base Table 생성]")
        print(f"  시도: {len(sidos)}개")
        print(f"  연령대: {len(age_groups)}개")
        print(f"  성별: {len(genders)}개")
        print(f"  소득분위: {len(income_quintiles)}개")
        
        # Cartesian Product 생성
        all_combinations = list(product(sidos, age_groups, genders, income_quintiles))
        
        base_df = pd.DataFrame(all_combinations, columns=[
            'Sido', 'Age_Group', 'Gender', 'Income_Quintile'
        ])
        
        # plan.md 요구사항: Sigungu 컬럼 추가 (빈 값 또는 시도와 동일)
        # 최종 출력 형식에 Sigungu가 포함되어 있으므로 추가
        base_df['Sigungu'] = ''  # 시군구는 사용하지 않으므로 빈 값
        
        # 컬럼 순서 조정 (최종 출력 형식에 맞춤)
        base_df = base_df[['Sido', 'Sigungu', 'Age_Group', 'Gender', 'Income_Quintile']]
        
        # 초기 가중치 할당 (균일 분포)
        initial_weight = 1.0 / len(base_df)
        base_df['total'] = initial_weight
        
        print(f"  Base Table 생성 완료: {len(base_df)}행")
        print(f"  초기 가중치 합계: {base_df['total'].sum():.6f}")
        
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
            print(f"  제약 조건 정규화 완료 (합계: {df_normalized[value_col].sum():.6f})")
        else:
            print("  경고: 제약 조건 합계가 0입니다.")
        
        return df_normalized
    
    def convert_to_long_format(self, df: pd.DataFrame, 
                               dimension_cols: List[str],
                               value_col: str = 'DT') -> pd.DataFrame:
        """
        Wide format 데이터를 Long format으로 변환
        
        Args:
            df: 원본 데이터프레임
            dimension_cols: 차원 컬럼 리스트
            value_col: 값 컬럼명 (또는 찾을 컬럼)
            
        Returns:
            DataFrame: Long format 데이터프레임
        """
        # KOSIS 데이터는 보통 이미 Long format이거나, 특정 구조를 가짐
        # DT 컬럼이나 숫자 컬럼을 찾아서 사용
        
        result_df = df.copy()
        
        # 값 컬럼 찾기
        if value_col not in result_df.columns:
            # 숫자 컬럼 찾기
            numeric_cols = result_df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                value_col = numeric_cols[0]
            elif 'DT' in result_df.columns:
                value_col = 'DT'
            else:
                # 모든 컬럼 중 차원 컬럼이 아닌 것 찾기
                for col in result_df.columns:
                    if col not in dimension_cols and result_df[col].dtype in [np.int64, np.float64]:
                        value_col = col
                        break
        
        # 차원 컬럼과 값 컬럼만 선택
        cols_to_keep = dimension_cols + [value_col]
        cols_to_keep = [col for col in cols_to_keep if col in result_df.columns]
        
        result_df = result_df[cols_to_keep].copy()
        result_df = result_df.rename(columns={value_col: 'value'})
        
        # 결측값 제거
        result_df = result_df.dropna(subset=['value'])
        
        # 값이 0보다 큰 것만 유지
        result_df = result_df[result_df['value'] > 0]
        
        return result_df.reset_index(drop=True)
    
    def prepare_constraints(self, 
                           all_data: Dict[str, pd.DataFrame],
                           collector) -> Tuple[List, List]:
        """
        IPF 알고리즘을 위한 제약 조건 준비
        
        Args:
            all_data: 수집된 모든 데이터 딕셔너리
            collector: KOSISPlanDataCollector 인스턴스 (변환 메서드 사용)
            
        Returns:
            Tuple: (aggregates 리스트, dimensions 리스트)
        """
        aggregates = []
        dimensions = []
        
        print("\n[제약 조건 준비]")
        
        # 제약 조건 1: 시도 x 연령 x 성별
        constraint1_list = []
        for name, df in all_data.items():
            if df.empty:
                continue
            
            # 시도, 연령, 성별 정보가 모두 있는지 확인
            has_sido = 'C1_NM' in df.columns
            has_age = any('C2' in col and 'NM' in col for col in df.columns)
            has_gender = 'ITM_NM' in df.columns
            
            if has_sido and has_age and has_gender:
                converted = collector.convert_to_constraint_format(df, 'sido_age_gender')
                if not converted.empty:
                    constraint1_list.append(converted)
                    print(f"  제약 조건 1 데이터 발견: {name} ({len(converted)}행)")
        
        if constraint1_list:
            # 모든 제약 조건 1 데이터 통합
            constraint1 = pd.concat(constraint1_list, ignore_index=True)
            # 그룹화하여 합계 계산 (중복 제거)
            constraint1 = constraint1.groupby(['Sido', 'Age_Group', 'Gender'])['value'].sum().reset_index()
            # 정규화
            constraint1_norm = self.normalize_constraints(constraint1, 'value')
            aggregates.append(constraint1_norm)
            dimensions.append(['Sido', 'Age_Group', 'Gender'])
            print(f"  제약 조건 1 준비 완료: {len(constraint1_norm)}행")
        
        # 제약 조건 2: 연령 x 소득분위 (또는 다른 제약 조건)
        # 소득분위 데이터는 별도로 찾아야 하므로, 일단 제약 조건 1만 사용
        # 필요시 추가 제약 조건을 여기에 추가
        
        print(f"  총 {len(aggregates)}개의 제약 조건 준비 완료")
        
        return aggregates, dimensions
    
    def run_ipf(self, 
                base_df: pd.DataFrame,
                aggregates: List[pd.DataFrame],
                dimensions: List[List[str]],
                convergence_rate: float = 1e-6,
                max_iterations: int = 50) -> pd.DataFrame:
        """
        IPF 알고리즘 실행
        
        Args:
            base_df: Base 테이블
            aggregates: 제약 조건 리스트
            dimensions: 각 제약 조건의 차원 리스트
            convergence_rate: 수렴 기준
            max_iterations: 최대 반복 횟수
            
        Returns:
            DataFrame: IPF 결과 (Weight 컬럼 포함)
        """
        print("\n[IPF 알고리즘 실행]")
        
        if not aggregates:
            print("  경고: 제약 조건이 없어 IPF를 실행할 수 없습니다.")
            # 기본 가중치만 정규화
            result_df = base_df.copy()
            result_df['Weight'] = result_df['total'] / result_df['total'].sum()
            result_df = result_df.drop('total', axis=1)
            return result_df
        
        result_df = base_df.copy()
        weight_col = 'total'
        
        for iteration in range(max_iterations):
            max_diff = 0.0
            
            # 각 제약 조건에 대해 순차적으로 적용
            for agg_df, dims in zip(aggregates, dimensions):
                # 제약 조건의 값 컬럼 찾기
                value_col = 'value' if 'value' in agg_df.columns else 'total'
                
                # Base table을 차원별로 그룹화하여 합계 계산
                # dims는 이미 Base table 컬럼명과 일치함 (Sido, Age_Group, Gender 등)
                base_dims = [d for d in dims if d in result_df.columns]
                
                if not base_dims:
                    continue
                
                # Base table 그룹화
                group_sum = result_df.groupby(base_dims)[weight_col].sum().reset_index()
                group_sum = group_sum.rename(columns={weight_col: 'current_sum'})
                
                # 제약 조건과 합치기
                merged = group_sum.merge(agg_df, on=base_dims, how='inner')
                
                if len(merged) == 0:
                    continue
                
                # 비율 계산 (목표값 / 현재값)
                merged['ratio'] = merged[value_col] / (merged['current_sum'] + 1e-10)
                
                # Base table과 합치기
                result_df = result_df.merge(merged[base_dims + ['ratio']], on=base_dims, how='left')
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
        
        # Weight 합계 검증 및 정규화
        weight_sum = result_df['Weight'].sum()
        print(f"\n[검증] 최종 Weight 합계: {weight_sum:.6f}")
        
        if abs(weight_sum - 1.0) > 0.0001:
            print(f"  정규화 수행 (현재 합계: {weight_sum:.6f})")
            result_df['Weight'] = result_df['Weight'] / weight_sum
            print(f"  정규화 후 Weight 합계: {result_df['Weight'].sum():.10f}")
        else:
            print("  검증 통과: Weight 합계가 1.0에 가깝습니다.")
        
        return result_df
