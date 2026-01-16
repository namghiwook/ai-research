"""
KOSIS 통계 목록 조회하여 실제 TBL_ID 찾기 및 API URL 생성
"""
import requests
import pandas as pd
import json
import time
from urllib.parse import urlencode

API_KEY = "ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY="

def search_statistics_by_keyword(keyword: str, org_id: str = "101") -> pd.DataFrame:
    """
    키워드로 통계표 검색
    """
    search_url = "https://kosis.kr/openapi/statisticsList.do"
    params = {
        "method": "getList",
        "apiKey": API_KEY,
        "format": "json",
        "jsonVD": "Y",
        "orgId": org_id,
        "keyword": keyword
    }
    
    try:
        response = requests.get(search_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            if 'list' in data:
                return pd.DataFrame(data['list'])
            elif 'err' in data:
                print(f"  오류: {data.get('errMsg', '알 수 없는 오류')}")
                return pd.DataFrame()
        return pd.DataFrame()
    except Exception as e:
        print(f"  오류: {str(e)}")
        return pd.DataFrame()

def get_statistics_by_category(category_id: str) -> pd.DataFrame:
    """
    카테고리별 통계표 조회
    """
    search_url = "https://kosis.kr/openapi/statisticsList.do"
    params = {
        "method": "getList",
        "apiKey": API_KEY,
        "format": "json",
        "jsonVD": "Y",
        "orgId": "101",
        "vwCd": "MT_ZTITLE",
        "parentListId": category_id
    }
    
    try:
        response = requests.get(search_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            if 'list' in data:
                return pd.DataFrame(data['list'])
        return pd.DataFrame()
    except Exception as e:
        print(f"  오류: {str(e)}")
        return pd.DataFrame()

def find_all_statistics():
    """
    plan.md에서 요구하는 모든 통계표 찾기
    """
    print("=" * 80)
    print("KOSIS 통계표 검색 및 URL 생성")
    print("=" * 80)
    
    found_statistics = {
        '소득분위': [],
        '산업_직업': [],
        '종사상지위': [],
        '주거_점유형태': [],
        '주택종류': [],
        '가구원수': []
    }
    
    # 1. 소득분위 관련 검색
    print("\n[1] 소득분위 관련 통계표 검색")
    print("-" * 80)
    income_keywords = ['소득분위', '가구소득', '소득분배', '소득10분위', '소득5분위']
    for keyword in income_keywords:
        print(f"\n검색어: '{keyword}'")
        results = search_statistics_by_keyword(keyword)
        if not results.empty:
            print(f"  결과: {len(results)}개")
            for _, row in results.head(5).iterrows():
                tbl_id = row.get('TBL_ID', '')
                tbl_nm = row.get('TBL_NM', '')
                if tbl_id and tbl_id.startswith('DT_'):
                    found_statistics['소득분위'].append({
                        'TBL_ID': tbl_id,
                        'TBL_NM': tbl_nm,
                        'USER_STATS_ID': row.get('USER_STATS_ID', ''),
                        'keyword': keyword
                    })
                    print(f"    - {tbl_nm} ({tbl_id})")
        time.sleep(0.3)
    
    # 2. 산업/직업 관련 검색
    print("\n\n[2] 산업/직업 관련 통계표 검색")
    print("-" * 80)
    job_keywords = ['산업', '직업', '종사상지위', 'DT_1DA7001']
    for keyword in job_keywords:
        print(f"\n검색어: '{keyword}'")
        results = search_statistics_by_keyword(keyword)
        if not results.empty:
            print(f"  결과: {len(results)}개")
            for _, row in results.head(5).iterrows():
                tbl_id = row.get('TBL_ID', '')
                tbl_nm = row.get('TBL_NM', '')
                if tbl_id and tbl_id.startswith('DT_'):
                    found_statistics['산업_직업'].append({
                        'TBL_ID': tbl_id,
                        'TBL_NM': tbl_nm,
                        'USER_STATS_ID': row.get('USER_STATS_ID', ''),
                        'keyword': keyword
                    })
                    print(f"    - {tbl_nm} ({tbl_id})")
        time.sleep(0.3)
    
    # 3. 주거 관련 검색
    print("\n\n[3] 주거 관련 통계표 검색")
    print("-" * 80)
    housing_keywords = ['점유형태', '주택점유', '자가', '전세', '월세', '주택종류', '아파트', '단독주택', '가구원수', '세대구성']
    for keyword in housing_keywords:
        print(f"\n검색어: '{keyword}'")
        results = search_statistics_by_keyword(keyword)
        if not results.empty:
            print(f"  결과: {len(results)}개")
            for _, row in results.head(5).iterrows():
                tbl_id = row.get('TBL_ID', '')
                tbl_nm = row.get('TBL_NM', '')
                if tbl_id and tbl_id.startswith('DT_'):
                    # 키워드에 따라 분류
                    if keyword in ['점유형태', '주택점유', '자가', '전세', '월세']:
                        found_statistics['주거_점유형태'].append({
                            'TBL_ID': tbl_id,
                            'TBL_NM': tbl_nm,
                            'USER_STATS_ID': row.get('USER_STATS_ID', ''),
                            'keyword': keyword
                        })
                    elif keyword in ['주택종류', '아파트', '단독주택']:
                        found_statistics['주택종류'].append({
                            'TBL_ID': tbl_id,
                            'TBL_NM': tbl_nm,
                            'USER_STATS_ID': row.get('USER_STATS_ID', ''),
                            'keyword': keyword
                        })
                    elif keyword in ['가구원수', '세대구성']:
                        found_statistics['가구원수'].append({
                            'TBL_ID': tbl_id,
                            'TBL_NM': tbl_nm,
                            'USER_STATS_ID': row.get('USER_STATS_ID', ''),
                            'keyword': keyword
                        })
                    print(f"    - {tbl_nm} ({tbl_id})")
        time.sleep(0.3)
    
    # 4. 카테고리별 조회 (소득/소비/자산, 주거)
    print("\n\n[4] 카테고리별 통계표 조회")
    print("-" * 80)
    
    categories = {
        'E': '소득/소비/자산',
        'F': '주거'
    }
    
    for cat_id, cat_name in categories.items():
        print(f"\n카테고리: {cat_name} ({cat_id})")
        results = get_statistics_by_category(cat_id)
        if not results.empty:
            print(f"  통계표 수: {len(results)}개")
            for _, row in results.head(20).iterrows():
                tbl_id = row.get('TBL_ID', '')
                tbl_nm = row.get('TBL_NM', '')
                if tbl_id and tbl_id.startswith('DT_'):
                    # 키워드로 분류
                    if '소득' in tbl_nm or '분위' in tbl_nm:
                        found_statistics['소득분위'].append({
                            'TBL_ID': tbl_id,
                            'TBL_NM': tbl_nm,
                            'USER_STATS_ID': row.get('USER_STATS_ID', ''),
                            'keyword': f'카테고리_{cat_name}'
                        })
                    elif '점유' in tbl_nm or '자가' in tbl_nm or '전세' in tbl_nm or '월세' in tbl_nm:
                        found_statistics['주거_점유형태'].append({
                            'TBL_ID': tbl_id,
                            'TBL_NM': tbl_nm,
                            'USER_STATS_ID': row.get('USER_STATS_ID', ''),
                            'keyword': f'카테고리_{cat_name}'
                        })
                    elif '주택' in tbl_nm or '아파트' in tbl_nm:
                        found_statistics['주택종류'].append({
                            'TBL_ID': tbl_id,
                            'TBL_NM': tbl_nm,
                            'USER_STATS_ID': row.get('USER_STATS_ID', ''),
                            'keyword': f'카테고리_{cat_name}'
                        })
                    elif '가구' in tbl_nm:
                        found_statistics['가구원수'].append({
                            'TBL_ID': tbl_id,
                            'TBL_NM': tbl_nm,
                            'USER_STATS_ID': row.get('USER_STATS_ID', ''),
                            'keyword': f'카테고리_{cat_name}'
                        })
        time.sleep(0.3)
    
    # 5. 중복 제거 및 정리
    print("\n\n[5] 결과 정리")
    print("=" * 80)
    
    # 중복 제거
    for key in found_statistics:
        seen = set()
        unique_list = []
        for item in found_statistics[key]:
            tbl_id = item['TBL_ID']
            if tbl_id not in seen:
                seen.add(tbl_id)
                unique_list.append(item)
        found_statistics[key] = unique_list
    
    # 결과 출력
    total_count = 0
    for category, stats in found_statistics.items():
        count = len(stats)
        total_count += count
        print(f"\n{category}: {count}개")
        for stat in stats[:5]:  # 상위 5개만 출력
            print(f"  - {stat['TBL_NM']} ({stat['TBL_ID']})")
        if count > 5:
            print(f"  ... 외 {count - 5}개")
    
    print(f"\n총 발견된 통계표: {total_count}개")
    
    # JSON 저장
    with open('found_kosis_statistics.json', 'w', encoding='utf-8') as f:
        json.dump(found_statistics, f, ensure_ascii=False, indent=2)
    print(f"\n결과 저장: found_kosis_statistics.json")
    
    return found_statistics

def generate_api_urls(found_statistics):
    """
    발견된 통계표에 대한 API URL 생성
    기존 URL 형식을 참고하여 생성
    """
    print("\n\n[6] API URL 생성")
    print("=" * 80)
    
    base_url = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
    
    generated_urls = {}
    
    for category, stats in found_statistics.items():
        if not stats:
            continue
        
        print(f"\n{category}:")
        generated_urls[category] = []
        
        for stat in stats:
            tbl_id = stat['TBL_ID']
            
            # 기본 파라미터 (기존 URL 형식 참고)
            params = {
                'method': 'getList',
                'apiKey': API_KEY,
                'format': 'json',
                'jsonVD': 'Y',
                'orgId': '101',
                'tblId': tbl_id,
                'prdSe': 'Y',  # 최신 연도
                'newEstPrdCnt': '3'
            }
            
            # 기본 objL1 (시도 전체)
            params['objL1'] = '00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+'
            
            # URL 생성
            url = f"{base_url}?{urlencode(params, doseq=True)}"
            
            generated_urls[category].append({
                'TBL_ID': tbl_id,
                'TBL_NM': stat['TBL_NM'],
                'url': url,
                'description': stat.get('keyword', '')
            })
            
            print(f"  - {stat['TBL_NM']} ({tbl_id})")
            print(f"    URL: {url[:100]}...")
    
    # JSON 저장
    with open('generated_kosis_urls.json', 'w', encoding='utf-8') as f:
        json.dump(generated_urls, f, ensure_ascii=False, indent=2)
    print(f"\n생성된 URL 저장: generated_kosis_urls.json")
    
    return generated_urls

if __name__ == "__main__":
    found_stats = find_all_statistics()
    generated_urls = generate_api_urls(found_stats)
    
    print("\n" + "=" * 80)
    print("작업 완료!")
    print("=" * 80)
