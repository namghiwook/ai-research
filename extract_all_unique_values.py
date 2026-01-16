"""
기존 수집 데이터에서 모든 고유값 추출 및 정리
"""
import pandas as pd
import json
from kosis_data_collector_plan import KOSISPlanDataCollector
import re

API_KEY = "ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY="

def extract_all_dimensions_from_collected_data():
    """
    기존 수집 데이터에서 모든 차원과 고유값 추출
    """
    print("=" * 80)
    print("기존 수집 데이터에서 모든 고유값 추출")
    print("=" * 80)
    
    # 데이터 수집
    collector = KOSISPlanDataCollector(API_KEY)
    all_data = collector.collect_all_data()
    
    print(f"\n수집된 데이터: {len(all_data)}개")
    
    # 모든 차원 추출
    all_dimensions = {
        'Sido': set(),
        'Sigungu': set(),
        'Age_Group': set(),
        'Gender': set(),
        'Marital_Status': set(),
        'Education': set(),
        'Income_Quintile': set(),
        'Housing_Type': set(),
        'Occupation': set(),
        'Industry': set(),
        'Employment_Status': set(),
        'Household_Size': set(),
        'Other': {}
    }
    
    for name, df in all_data.items():
        if df.empty:
            continue
        
        print(f"\n[{name}] 분석 중... ({len(df)}행)")
        
        # 시도 추출
        if 'C1_NM' in df.columns:
            for sido in df['C1_NM'].dropna().unique():
                normalized = collector.normalize_sido(str(sido))
                if normalized and normalized not in ['기타', '전국', '계', '소계']:
                    all_dimensions['Sido'].add(normalized)
        
        # 시군구 추출
        if 'C2_NM' in df.columns and '시군구' in name:
            for sigungu in df['C2_NM'].dropna().unique():
                sigungu_str = str(sigungu)
                if sigungu_str not in ['전국', '계', '소계', 'ALL']:
                    all_dimensions['Sigungu'].add(sigungu_str)
        
        # 연령대 추출
        age_cols = [col for col in df.columns if 'C2' in col and 'NM' in col]
        for col in age_cols:
            for age_str in df[col].dropna().unique():
                age_group = collector.convert_age_group_format(str(age_str))
                if age_group:
                    all_dimensions['Age_Group'].add(age_group)
        
        # 성별 추출
        if 'ITM_NM' in df.columns:
            for itm_nm in df['ITM_NM'].dropna().unique():
                itm_str = str(itm_nm)
                if '남자' in itm_str or '남' in itm_str:
                    all_dimensions['Gender'].add('남자')
                elif '여자' in itm_str or '여' in itm_str:
                    all_dimensions['Gender'].add('여자')
                
                # 혼인상태 추출
                if '미혼' in itm_str:
                    all_dimensions['Marital_Status'].add('미혼')
                elif '배우자있음' in itm_str or '배우자' in itm_str or '기혼' in itm_str:
                    all_dimensions['Marital_Status'].add('배우자있음')
                elif '사별' in itm_str:
                    all_dimensions['Marital_Status'].add('사별')
                elif '이혼' in itm_str:
                    all_dimensions['Marital_Status'].add('이혼')
                
                # 교육정도 추출
                if '졸업' in itm_str or '재학' in itm_str or '중퇴' in itm_str:
                    # 구체적인 교육정도 추출
                    if '중졸' in itm_str:
                        all_dimensions['Education'].add('중졸')
                    elif '고졸' in itm_str:
                        all_dimensions['Education'].add('고졸')
                    elif '대졸' in itm_str or '대학졸업' in itm_str:
                        all_dimensions['Education'].add('대졸')
                    elif '대학원' in itm_str:
                        all_dimensions['Education'].add('대학원졸')
                    else:
                        all_dimensions['Education'].add(itm_str)
        
        # 소득분위 추출
        for col in df.columns:
            if '소득' in str(col) or '분위' in str(col):
                for val in df[col].dropna().unique():
                    val_str = str(val)
                    # 10분위 추출
                    for i in range(1, 11):
                        if f'{i}분위' in val_str:
                            all_dimensions['Income_Quintile'].add(f'{i}분위')
                    # 5분위 추출
                    for i in range(1, 6):
                        if f'{i}분위' in val_str and f'{i}0분위' not in val_str:
                            all_dimensions['Income_Quintile'].add(f'{i}분위')
        
        # 주거 관련 추출 (ITM_NM이나 다른 컬럼에서)
        for col in df.columns:
            col_str = str(col).lower()
            if '주택' in col_str or '주거' in col_str or '점유' in col_str:
                values = df[col].dropna().unique()
                for val in values:
                    val_str = str(val)
                    if val_str not in ['전국', '계', '소계']:
                        all_dimensions['Housing_Type'].add(val_str)
        
        # 기타 컬럼 분석
        for col in df.columns:
            if col not in ['C1_NM', 'C2_NM', 'C3_NM', 'C4_NM', 'ITM_NM', 'DT', 'PRD_DE']:
                unique_vals = df[col].dropna().unique()
                if len(unique_vals) > 0 and len(unique_vals) < 50:  # 너무 많은 값은 제외
                    filtered_vals = [v for v in unique_vals if str(v) not in ['전국', '계', '소계', '-', 'nan']]
                    if len(filtered_vals) > 0:
                        all_dimensions['Other'][col] = sorted(list(filtered_vals))
    
    # 정리 및 변환
    result = {}
    for key, value in all_dimensions.items():
        if isinstance(value, set):
            if key == 'Age_Group':
                result[key] = sorted(list(value), 
                                   key=lambda x: (int(x.split('-')[0]) if '-' in x else (1000 if '+' in x else 999)))
            elif key == 'Income_Quintile':
                result[key] = sorted(list(value), 
                                   key=lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 0)
            else:
                result[key] = sorted(list(value))
        else:
            result[key] = value
    
    return result, all_data

def main():
    """
    메인 함수
    """
    # 모든 고유값 추출
    all_dimensions, all_data = extract_all_dimensions_from_collected_data()
    
    # 결과 출력
    print("\n" + "=" * 80)
    print("추출된 모든 고유값")
    print("=" * 80)
    
    for dim_name, dim_values in all_dimensions.items():
        if isinstance(dim_values, list):
            print(f"\n[{dim_name}]: {len(dim_values)}개")
            if len(dim_values) <= 20:
                for i, val in enumerate(dim_values, 1):
                    print(f"  {i:2d}. {val}")
            else:
                for i, val in enumerate(dim_values[:10], 1):
                    print(f"  {i:2d}. {val}")
                print(f"  ... 외 {len(dim_values) - 10}개")
        elif isinstance(dim_values, dict):
            print(f"\n[{dim_name}]: {len(dim_values)}개 컬럼")
            for col, vals in list(dim_values.items())[:5]:
                print(f"  - {col}: {len(vals)}개")
    
    # JSON 저장
    with open('all_extracted_dimensions.json', 'w', encoding='utf-8') as f:
        json.dump(all_dimensions, f, ensure_ascii=False, indent=2)
    
    print(f"\n결과 저장: all_extracted_dimensions.json")
    
    # 요약 통계
    print("\n" + "=" * 80)
    print("요약 통계")
    print("=" * 80)
    total_combinations = 1
    for dim_name, dim_values in all_dimensions.items():
        if isinstance(dim_values, list) and dim_name in ['Sido', 'Age_Group', 'Gender', 'Income_Quintile']:
            count = len(dim_values)
            print(f"{dim_name}: {count}개")
            total_combinations *= count
    
    print(f"\n현재 Base Table 조합 수: {total_combinations:,}개")
    
    # 소득분위 확인
    if all_dimensions.get('Income_Quintile'):
        print(f"\n소득분위 발견: {all_dimensions['Income_Quintile']}")
    else:
        print("\n⚠ 소득분위 데이터를 찾을 수 없습니다.")
        print("  → 기본값(10분위) 사용 중")
    
    # 혼인상태 확인
    if all_dimensions.get('Marital_Status'):
        print(f"\n혼인상태 발견: {all_dimensions['Marital_Status']}")
    
    # 교육정도 확인
    if all_dimensions.get('Education'):
        print(f"\n교육정도 발견: {len(all_dimensions['Education'])}개")
        print(f"  → {list(all_dimensions['Education'])[:10]}")

if __name__ == "__main__":
    main()
