"""
소득 관련 통계표 데이터 확인 - 특히 성별 연령대별 소득 분포
"""
import requests
import pandas as pd
import json
from urllib.parse import urlencode

API_KEY = "ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY="

# 소득 관련 통계표 목록
INCOME_STATS = [
    {
        'tblId': 'DT_1EP_2010',
        'title': '성별 연령대별 소득',
        'description': '사용자가 언급한 통계표 - 만원 단위 범위값, 성별, 연령대별 퍼센트'
    },
    {
        'tblId': 'DT_1EP_2021',
        'title': '평균소득, 중위소득, 소득분포',
        'description': '소득분포 포함'
    },
    {
        'tblId': 'DT_1EP_2005',
        'title': '성별 소득',
        'description': '성별 소득 통계'
    },
    {
        'tblId': 'DT_1EP_2006',
        'title': '연령대별 소득',
        'description': '연령대별 소득 통계'
    }
]

def test_income_statistic(tbl_id: str, title: str):
    """
    소득 통계표 데이터 조회 및 분석
    """
    print(f"\n{'='*80}")
    print(f"[{title}] ({tbl_id})")
    print(f"{'='*80}")
    
    base_url = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
    
    # 여러 파라미터 조합 시도
    test_params_list = [
        {
            'method': 'getList',
            'apiKey': API_KEY,
            'format': 'json',
            'jsonVD': 'Y',
            'orgId': '101',
            'tblId': tbl_id,
            'prdSe': 'Y',
            'newEstPrdCnt': '3',
            'objL1': '00'  # 전국만
        },
        {
            'method': 'getList',
            'apiKey': API_KEY,
            'format': 'json',
            'jsonVD': 'Y',
            'orgId': '101',
            'tblId': tbl_id,
            'prdSe': 'F',
            'newEstPrdCnt': '3',
            'objL1': '00'
        }
    ]
    
    for i, params in enumerate(test_params_list, 1):
        try:
            url = f"{base_url}?{urlencode(params, doseq=True)}"
            print(f"\n시도 {i}: {params.get('prdSe', 'N')} (연도/분기)")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # 오류 확인
            if isinstance(data, dict):
                if 'err' in data:
                    print(f"  오류: {data.get('errMsg', '알 수 없는 오류')}")
                    continue
                elif 'list' in data:
                    data = data['list']
            
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
                print(f"  ✓ 성공! {len(df)}행 수집됨")
                print(f"  컬럼: {list(df.columns)[:15]}")
                
                # 데이터 샘플 확인
                print(f"\n  데이터 샘플 (처음 5행):")
                print(df.head().to_string())
                
                # 소득 범위 관련 컬럼 찾기
                income_cols = [col for col in df.columns if '소득' in str(col) or 'INCOME' in str(col).upper() or 'ITM_NM' in col]
                if income_cols:
                    print(f"\n  소득 관련 컬럼:")
                    for col in income_cols:
                        unique_vals = df[col].dropna().unique()[:10]
                        print(f"    - {col}: {len(df[col].dropna().unique())}개 고유값")
                        if len(unique_vals) > 0:
                            print(f"      샘플: {list(unique_vals)[:5]}")
                
                # 연령대 관련 컬럼 찾기
                age_cols = [col for col in df.columns if '연령' in str(col) or 'AGE' in str(col).upper() or 'C2' in col]
                if age_cols:
                    print(f"\n  연령대 관련 컬럼:")
                    for col in age_cols:
                        unique_vals = df[col].dropna().unique()[:10]
                        print(f"    - {col}: {len(df[col].dropna().unique())}개 고유값")
                        if len(unique_vals) > 0:
                            print(f"      샘플: {list(unique_vals)[:5]}")
                
                # 성별 관련 컬럼 찾기
                gender_cols = [col for col in df.columns if '성별' in str(col) or 'GENDER' in str(col).upper() or 'C1' in col or 'ITM_NM' in col]
                if gender_cols:
                    print(f"\n  성별 관련 컬럼:")
                    for col in gender_cols:
                        unique_vals = df[col].dropna().unique()[:10]
                        print(f"    - {col}: {len(df[col].dropna().unique())}개 고유값")
                        if len(unique_vals) > 0:
                            print(f"      샘플: {list(unique_vals)[:5]}")
                
                # 값 컬럼 찾기 (DT, 숫자 등)
                value_cols = [col for col in df.columns if col in ['DT', 'VALUE', 'VAL'] or (df[col].dtype in ['int64', 'float64'] and col not in ['ORG_ID', 'TBL_ID'])]
                if value_cols:
                    print(f"\n  값 컬럼:")
                    for col in value_cols:
                        print(f"    - {col}: {df[col].dtype}")
                        if len(df[col].dropna()) > 0:
                            sample_vals = df[col].dropna().head(5).tolist()
                            print(f"      샘플: {sample_vals}")
                
                return df
            else:
                print(f"  경고: 데이터 없음")
                
        except Exception as e:
            print(f"  오류: {str(e)}")
        
        import time
        time.sleep(0.3)
    
    return None

def main():
    """
    메인 함수
    """
    print("=" * 80)
    print("소득 관련 통계표 데이터 확인")
    print("=" * 80)
    
    results = {}
    
    for stat in INCOME_STATS:
        df = test_income_statistic(stat['tblId'], stat['title'])
        if df is not None:
            results[stat['tblId']] = {
                'title': stat['title'],
                'row_count': len(df),
                'columns': list(df.columns),
                'sample_data': df.head(10).to_dict('records')
            }
    
    # 결과 저장
    if results:
        with open('income_statistics_test.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n결과 저장: income_statistics_test.json")
    
    print("\n" + "=" * 80)
    print("요약")
    print("=" * 80)
    print(f"테스트한 통계표: {len(INCOME_STATS)}개")
    print(f"데이터 조회 성공: {len(results)}개")
    
    # DT_1EP_2010이 성공했는지 확인
    if 'DT_1EP_2010' in results:
        print("\n✓ DT_1EP_2010 (성별 연령대별 소득) 데이터 조회 성공!")
        print("  이 통계표가 사용자가 언급한 통계표일 가능성이 높습니다.")

if __name__ == "__main__":
    main()
