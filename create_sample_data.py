"""
KOSIS 데이터 구조를 모방한 샘플 데이터 생성
실제 API 연동 전에 IPF 로직을 검증하기 위한 샘플 데이터
"""
import pandas as pd
import numpy as np

def create_sample_base_data():
    """Base 데이터 샘플 생성: 지역, 연령, 성별별 인구"""
    
    # 시도 목록
    sidos = ['서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시']
    
    # 시군구 목록 (간단한 예시)
    sigungus = {
        '서울특별시': ['종로구', '중구', '용산구'],
        '부산광역시': ['중구', '서구', '동구'],
        '대구광역시': ['중구', '동구', '서구'],
        '인천광역시': ['중구', '동구', '미추홀구'],
        '광주광역시': ['동구', '서구', '남구']
    }
    
    # 연령대 (5세 단위)
    age_groups = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', 
                  '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', 
                  '65-69', '70-74', '75-79', '80+']
    
    # 성별
    genders = ['남자', '여자']
    
    # 데이터 생성
    data = []
    for sido in sidos:
        for sigungu in sigungus[sido]:
            for age_group in age_groups:
                for gender in genders:
                    # 랜덤한 인구수 생성 (1000 ~ 100000)
                    population = np.random.randint(1000, 100000)
                    data.append({
                        'Sido': sido,
                        'Sigungu': sigungu,
                        'Age_Group': age_group,
                        'Gender': gender,
                        'Population': population
                    })
    
    df = pd.DataFrame(data)
    return df

def create_sample_constraint1_data():
    """제약 조건 1 샘플: 시군구, 성별, 연령별 인구 (혼인상태 제외)"""
    
    sidos = ['서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시']
    sigungus = {
        '서울특별시': ['종로구', '중구', '용산구'],
        '부산광역시': ['중구', '서구', '동구'],
        '대구광역시': ['중구', '동구', '서구'],
        '인천광역시': ['중구', '동구', '미추홀구'],
        '광주광역시': ['동구', '서구', '남구']
    }
    
    age_groups = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', 
                  '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', 
                  '65-69', '70-74', '75-79', '80+']
    genders = ['남자', '여자']
    
    data = []
    for sido in sidos:
        for sigungu in sigungus[sido]:
            for age_group in age_groups:
                for gender in genders:
                    population = np.random.randint(1000, 100000)
                    data.append({
                        'Sido': sido,
                        'Sigungu': sigungu,
                        'Age_Group': age_group,
                        'Gender': gender,
                        'value': population
                    })
    
    df = pd.DataFrame(data)
    return df

def create_sample_constraint2_data():
    """제약 조건 2 샘플: 연령대별 소득분위 비율"""
    
    age_groups = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', 
                  '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', 
                  '65-69', '70-74', '75-79', '80+']
    
    income_quintiles = ['1분위', '2분위', '3분위', '4분위', '5분위']
    
    data = []
    for age_group in age_groups:
        # 각 연령대별로 소득분위 비율 생성 (합이 1이 되도록)
        ratios = np.random.dirichlet(np.ones(len(income_quintiles)))
        for i, quintile in enumerate(income_quintiles):
            data.append({
                'Age_Group': age_group,
                'Income_Quintile': quintile,
                'value': ratios[i]
            })
    
    df = pd.DataFrame(data)
    return df

def main():
    """샘플 데이터 생성 및 저장"""
    
    print("샘플 데이터 생성 중...")
    
    base_df = create_sample_base_data()
    constraint1_df = create_sample_constraint1_data()
    constraint2_df = create_sample_constraint2_data()
    
    # 저장
    base_df.to_csv("sample_base_data.csv", index=False, encoding='utf-8-sig')
    constraint1_df.to_csv("sample_constraint1_data.csv", index=False, encoding='utf-8-sig')
    constraint2_df.to_csv("sample_constraint2_data.csv", index=False, encoding='utf-8-sig')
    
    print(f"\nBase 데이터 생성 완료: {len(base_df)}행")
    print(f"제약 조건 1 데이터 생성 완료: {len(constraint1_df)}행")
    print(f"제약 조건 2 데이터 생성 완료: {len(constraint2_df)}행")
    
    print("\n생성된 파일:")
    print("  - sample_base_data.csv")
    print("  - sample_constraint1_data.csv")
    print("  - sample_constraint2_data.csv")
    
    print("\n샘플 데이터 미리보기:")
    print("\nBase 데이터:")
    print(base_df.head())
    print("\n제약 조건 1:")
    print(constraint1_df.head())
    print("\n제약 조건 2:")
    print(constraint2_df.head())

if __name__ == "__main__":
    main()
