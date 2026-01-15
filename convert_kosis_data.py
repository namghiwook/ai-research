"""
KOSIS API로 수집한 데이터를 IPF에 필요한 형식으로 변환
"""
import pandas as pd

def convert_constraint1_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    KOSIS API 데이터를 제약 조건 1 형식으로 변환
    입력: C1_NM(시도), C2_NM(연령대), ITM_NM(항목), DT(값)
    출력: Sigungu, Gender, Age_Group, value
    """
    result = []
    
    # '전국' 제외
    df = df[df['C1_NM'] != '전국'].copy()
    # '합계' 연령대 제외
    df = df[df['C2_NM'] != '합계'].copy()
    
    for _, row in df.iterrows():
        sido = row['C1_NM']
        age_group = row['C2_NM']
        itm_nm = row['ITM_NM']
        
        # DT 값 처리 (- 또는 빈 값 제외)
        dt_value = row['DT']
        try:
            value = int(dt_value) if str(dt_value) not in ['-', '', 'nan'] else 0
        except (ValueError, TypeError):
            value = 0
        
        if value == 0:
            continue
        
        # 항목명에서 성별과 혼인상태 추출
        # 예: "남자-미혼", "여자-배우자있음", "내국인(15세이상)-계" 등
        gender = None
        if '남자' in itm_nm or '남자' in itm_nm:
            gender = '남자'
        elif '여자' in itm_nm:
            gender = '여자'
        elif '내국인' in itm_nm:
            # 전체 데이터이므로 성별은 나중에 처리
            continue
        
        # 연령대 형식 변환 (예: "15~19세" -> "15-19")
        age_group_clean = age_group.replace('~', '-').replace('세', '').replace('이상', '+')
        if age_group_clean == '85+':
            age_group_clean = '85+'
        
        if gender:
            result.append({
                'Sido': sido,
                'Sigungu': sido,  # 시군구가 없으면 시도 사용
                'Age_Group': age_group_clean,
                'Gender': gender,
                'value': value
            })
    
    return pd.DataFrame(result)

if __name__ == "__main__":
    # 테스트
    df = pd.read_csv('kosis_api_test_result.csv', encoding='utf-8-sig')
    converted = convert_constraint1_data(df)
    print(f"원본: {len(df)}행")
    print(f"변환 후: {len(converted)}행")
    print("\n샘플:")
    print(converted.head(20))
