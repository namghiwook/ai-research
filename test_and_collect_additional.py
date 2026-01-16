"""
추가 통계표 후보 테스트 및 데이터 수집
"""
import requests
import pandas as pd
import json
import time
from urllib.parse import urlencode

API_KEY = "ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY="

# 추가 통계표 후보 목록
ADDITIONAL_CANDIDATES = {
    '소득분위': [
        {'tbl_id': 'DT_1HD1501', 'name': '가계금융복지조사 가구소득'},
        {'tbl_id': 'DT_1HD1502', 'name': '가계금융복지조사 소득분위'},
    ],
    '산업_직업': [
        {'tbl_id': 'DT_1DA7001', 'name': '산업 및 직업 대분류'},
    ],
    '주거_점유형태': [
        {'tbl_id': 'DT_1HS1501', 'name': '주거실태조사 점유형태'},
    ],
    '주택종류': [
        {'tbl_id': 'DT_1HS1502', 'name': '주거실태조사 주택종류'},
    ]
}

def test_tbl_id(tbl_id: str, name: str) -> dict:
    """
    TBL_ID 테스트 - 실제 데이터 조회 가능한지 확인
    """
    print(f"\n[{name}] 테스트 중... (TBL_ID: {tbl_id})")
    
    # 기본 파라미터로 테스트
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
        },
        {
            'method': 'getList',
            'apiKey': API_KEY,
            'format': 'json',
            'jsonVD': 'Y',
            'orgId': '101',
            'tblId': tbl_id,
            'prdSe': 'Y',
            'newEstPrdCnt': '3'
        }
    ]
    
    for i, params in enumerate(test_params_list, 1):
        try:
            url = f"{base_url}?{urlencode(params, doseq=True)}"
            print(f"  시도 {i}: {url[:100]}...")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # 오류 확인
            if isinstance(data, dict):
                if 'err' in data:
                    print(f"    오류: {data.get('errMsg', '알 수 없는 오류')}")
                    continue
                elif 'list' in data:
                    data = data['list']
            
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
                print(f"    ✓ 성공! {len(df)}행 수집됨")
                print(f"    컬럼: {list(df.columns)[:10]}...")
                return {
                    'status': 'success',
                    'tbl_id': tbl_id,
                    'name': name,
                    'url': url,
                    'row_count': len(df),
                    'columns': list(df.columns),
                    'sample_data': df.head(3).to_dict('records') if len(df) > 0 else []
                }
            elif isinstance(data, list) and len(data) == 0:
                print(f"    경고: 데이터 없음")
            else:
                print(f"    경고: 예상치 못한 응답 형식")
                
        except Exception as e:
            print(f"    오류: {str(e)}")
        
        time.sleep(0.3)
    
    return {
        'status': 'failed',
        'tbl_id': tbl_id,
        'name': name,
        'url': None
    }

def test_all_candidates():
    """
    모든 후보 통계표 테스트
    """
    print("=" * 80)
    print("추가 통계표 후보 테스트")
    print("=" * 80)
    
    results = {}
    valid_stats = []
    
    for category, candidates in ADDITIONAL_CANDIDATES.items():
        print(f"\n[{category}]")
        print("-" * 80)
        results[category] = []
        
        for candidate in candidates:
            result = test_tbl_id(candidate['tbl_id'], candidate['name'])
            results[category].append(result)
            
            if result['status'] == 'success':
                valid_stats.append(result)
    
    # 결과 저장
    with open('additional_statistics_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 80)
    print("테스트 결과 요약")
    print("=" * 80)
    
    total_tested = sum(len(candidates) for candidates in ADDITIONAL_CANDIDATES.values())
    total_valid = len(valid_stats)
    
    print(f"\n총 테스트: {total_tested}개")
    print(f"유효한 통계표: {total_valid}개")
    
    if valid_stats:
        print("\n유효한 통계표 목록:")
        for stat in valid_stats:
            print(f"  ✓ {stat['name']} ({stat['tbl_id']}) - {stat['row_count']}행")
    
    print(f"\n결과 저장: additional_statistics_test_results.json")
    
    return results, valid_stats

def collect_valid_statistics(valid_stats):
    """
    유효한 통계표 데이터 수집 및 고유값 추출
    """
    if not valid_stats:
        print("\n수집할 유효한 통계표가 없습니다.")
        return
    
    print("\n" + "=" * 80)
    print("유효한 통계표 데이터 수집")
    print("=" * 80)
    
    collected_data = {}
    extracted_dimensions = {}
    
    for stat in valid_stats:
        tbl_id = stat['tbl_id']
        name = stat['name']
        url = stat['url']
        
        print(f"\n[{name}] 데이터 수집 중...")
        
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, dict) and 'list' in data:
                data = data['list']
            
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
                collected_data[tbl_id] = {
                    'name': name,
                    'data': df,
                    'row_count': len(df),
                    'columns': list(df.columns)
                }
                
                print(f"  수집 완료: {len(df)}행, {len(df.columns)}컬럼")
                
                # 고유값 추출
                dimensions = extract_dimensions(df, name)
                if dimensions:
                    extracted_dimensions[tbl_id] = dimensions
                    print(f"  추출된 차원: {list(dimensions.keys())}")
                    for dim_name, dim_values in dimensions.items():
                        print(f"    {dim_name}: {len(dim_values)}개")
                        if len(dim_values) <= 10:
                            print(f"      → {dim_values}")
                        else:
                            print(f"      → {dim_values[:5]} ... (총 {len(dim_values)}개)")
            
        except Exception as e:
            print(f"  오류: {str(e)}")
        
        time.sleep(0.5)
    
    # 결과 저장
    # DataFrame은 JSON으로 저장할 수 없으므로, 메타데이터만 저장
    metadata = {}
    for tbl_id, info in collected_data.items():
        metadata[tbl_id] = {
            'name': info['name'],
            'row_count': info['row_count'],
            'columns': info['columns'],
            'dimensions': extracted_dimensions.get(tbl_id, {})
        }
        # 실제 데이터는 CSV로 저장
        info['data'].to_csv(f'additional_data_{tbl_id}.csv', index=False, encoding='utf-8-sig')
        print(f"\n  데이터 저장: additional_data_{tbl_id}.csv")
    
    with open('additional_statistics_collected.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"\n결과 저장: additional_statistics_collected.json")
    
    return collected_data, extracted_dimensions

def extract_dimensions(df: pd.DataFrame, name: str) -> dict:
    """
    데이터프레임에서 고유값 추출
    """
    dimensions = {}
    
    # 시도 추출
    if 'C1_NM' in df.columns:
        sidos = df['C1_NM'].dropna().unique()
        sidos = [s for s in sidos if str(s) not in ['전국', '계', '소계', '합계']]
        if len(sidos) > 0:
            dimensions['Sido'] = sorted(list(sidos))
    
    # 연령대 추출
    if 'C2_NM' in df.columns:
        ages = df['C2_NM'].dropna().unique()
        ages = [a for a in ages if str(a) not in ['전국', '계', '소계', '합계', 'ALL']]
        if len(ages) > 0:
            dimensions['Age_Group'] = sorted(list(ages))
    
    # 성별 추출
    if 'ITM_NM' in df.columns:
        items = df['ITM_NM'].dropna().unique()
        genders = []
        for item in items:
            if '남자' in str(item) or '남' in str(item):
                genders.append('남자')
            elif '여자' in str(item) or '여' in str(item):
                genders.append('여자')
        if genders:
            dimensions['Gender'] = sorted(list(set(genders)))
    
    # 소득분위 추출
    for col in df.columns:
        if '소득' in str(col) or '분위' in str(col) or 'ITM_NM' in col:
            for val in df[col].dropna().unique():
                val_str = str(val)
                if '분위' in val_str:
                    import re
                    numbers = re.findall(r'\d+', val_str)
                    if numbers:
                        dimensions.setdefault('Income_Quintile', set()).add(val_str)
    
    # 직업/산업 추출
    for col in df.columns:
        if '직업' in str(col) or '산업' in str(col) or '종사' in str(col):
            values = df[col].dropna().unique()
            values = [v for v in values if str(v) not in ['전국', '계', '소계', '합계']]
            if len(values) > 0:
                dimensions[col] = sorted(list(values))
    
    # 주거 관련 추출
    for col in df.columns:
        if '점유' in str(col) or '주택' in str(col) or '거주' in str(col):
            values = df[col].dropna().unique()
            values = [v for v in values if str(v) not in ['전국', '계', '소계', '합계']]
            if len(values) > 0:
                dimensions[col] = sorted(list(values))
    
    # Income_Quintile을 리스트로 변환
    if 'Income_Quintile' in dimensions:
        dimensions['Income_Quintile'] = sorted(list(dimensions['Income_Quintile']))
    
    return dimensions

if __name__ == "__main__":
    # 1. 테스트
    test_results, valid_stats = test_all_candidates()
    
    # 2. 유효한 통계표 데이터 수집
    if valid_stats:
        collected_data, extracted_dimensions = collect_valid_statistics(valid_stats)
        
        print("\n" + "=" * 80)
        print("작업 완료!")
        print("=" * 80)
        print(f"\n유효한 통계표 {len(valid_stats)}개 확인 및 수집 완료")
    else:
        print("\n유효한 통계표를 찾을 수 없습니다.")
