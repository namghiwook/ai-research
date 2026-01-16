"""
KOSIS 통계 목록을 조회하여 모든 수집 가능한 API URL 정리
plan.md 요구사항에 따라 경제/고용, 주거/가구 관련 통계를 찾아서 URL 생성
"""
import requests
import pandas as pd
import json
from typing import List, Dict
import time

API_KEY = "ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY="

def search_statistics_list(keyword: str = "", parent_list_id: str = None, org_id: str = "101") -> pd.DataFrame:
    """
    KOSIS 통계 목록 조회
    
    Args:
        keyword: 검색 키워드
        parent_list_id: 상위 목록 ID (A=인구, B=사회일반, D=노동, E=소득/소비/자산 등)
        org_id: 기관ID (101=통계청)
    """
    search_url = "https://kosis.kr/openapi/statisticsList.do"
    params = {
        "method": "getList",
        "apiKey": API_KEY,
        "format": "json",
        "jsonVD": "Y",
        "orgId": org_id,
    }
    
    if keyword:
        params["keyword"] = keyword
    if parent_list_id:
        params["vwCd"] = "MT_ZTITLE"
        params["parentListId"] = parent_list_id
    
    try:
        response = requests.get(search_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict) and 'list' in data:
            return pd.DataFrame(data['list'])
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"  오류: {str(e)}")
        return pd.DataFrame()

def find_statistics_for_categories():
    """
    plan.md에 명시된 카테고리별 통계표 찾기
    1. 경제 및 고용 관련 항목 (Socio-Economic)
    2. 주거 및 가구 환경 관련 항목 (Housing & Household)
    """
    
    print("=" * 80)
    print("KOSIS 통계 목록 조회 및 수집 가능한 API URL 정리")
    print("=" * 80)
    
    all_statistics = []
    
    # 1. 경제 및 고용 관련 항목 검색
    print("\n[1] 경제 및 고용 관련 항목 (Socio-Economic)")
    print("-" * 80)
    
    economic_keywords = [
        "소득분위",
        "가구소득",
        "소득",
        "직업",
        "산업",
        "종사상지위",
        "고용",
        "교육정도",
        "학력"
    ]
    
    economic_stats = []
    for keyword in economic_keywords:
        print(f"\n검색어: '{keyword}'")
        results = search_statistics_list(keyword=keyword)
        if not results.empty:
            print(f"  검색 결과: {len(results)}개")
            if 'TBL_NM' in results.columns:
                for _, row in results.head(10).iterrows():
                    tbl_id = row.get('TBL_ID', '')
                    tbl_nm = row.get('TBL_NM', '')
                    user_stats_id = row.get('USER_STATS_ID', '')
                    if tbl_id and tbl_id.startswith('DT_'):
                        economic_stats.append({
                            'category': '경제/고용',
                            'keyword': keyword,
                            'TBL_ID': tbl_id,
                            'TBL_NM': tbl_nm,
                            'USER_STATS_ID': user_stats_id
                        })
        time.sleep(0.5)  # API 호출 간격
    
    # 2. 주거 및 가구 환경 관련 항목 검색
    print("\n\n[2] 주거 및 가구 환경 관련 항목 (Housing & Household)")
    print("-" * 80)
    
    housing_keywords = [
        "주거",
        "주택",
        "점유형태",
        "자가",
        "전세",
        "월세",
        "아파트",
        "단독주택",
        "연립",
        "다세대",
        "가구원수",
        "세대구성",
        "가구"
    ]
    
    housing_stats = []
    for keyword in housing_keywords:
        print(f"\n검색어: '{keyword}'")
        results = search_statistics_list(keyword=keyword)
        if not results.empty:
            print(f"  검색 결과: {len(results)}개")
            if 'TBL_NM' in results.columns:
                for _, row in results.head(10).iterrows():
                    tbl_id = row.get('TBL_ID', '')
                    tbl_nm = row.get('TBL_NM', '')
                    user_stats_id = row.get('USER_STATS_ID', '')
                    if tbl_id and tbl_id.startswith('DT_'):
                        housing_stats.append({
                            'category': '주거/가구',
                            'keyword': keyword,
                            'TBL_ID': tbl_id,
                            'TBL_NM': tbl_nm,
                            'USER_STATS_ID': user_stats_id
                        })
        time.sleep(0.5)  # API 호출 간격
    
    # 3. 카테고리별 통계표 목록 조회
    print("\n\n[3] 카테고리별 통계표 목록 조회")
    print("-" * 80)
    
    categories = {
        'A': '인구',
        'B': '사회일반',
        'D': '노동',
        'E': '소득/소비/자산',
        'F': '주거'
    }
    
    category_stats = []
    for cat_id, cat_name in categories.items():
        print(f"\n카테고리: {cat_name} ({cat_id})")
        results = search_statistics_list(parent_list_id=cat_id)
        if not results.empty:
            print(f"  통계표 수: {len(results)}개")
            if 'TBL_NM' in results.columns:
                for _, row in results.head(20).iterrows():
                    tbl_id = row.get('TBL_ID', '')
                    tbl_nm = row.get('TBL_NM', '')
                    user_stats_id = row.get('USER_STATS_ID', '')
                    if tbl_id and tbl_id.startswith('DT_'):
                        category_stats.append({
                            'category': cat_name,
                            'TBL_ID': tbl_id,
                            'TBL_NM': tbl_nm,
                            'USER_STATS_ID': user_stats_id
                        })
        time.sleep(0.5)
    
    # 4. 결과 정리
    print("\n\n[4] 결과 정리")
    print("=" * 80)
    
    all_found = economic_stats + housing_stats + category_stats
    
    # 중복 제거
    unique_stats = {}
    for stat in all_found:
        tbl_id = stat['TBL_ID']
        if tbl_id not in unique_stats:
            unique_stats[tbl_id] = stat
        else:
            # 카테고리 정보 통합
            if stat['category'] not in unique_stats[tbl_id].get('category', ''):
                unique_stats[tbl_id]['category'] += f", {stat['category']}"
    
    print(f"\n총 발견된 통계표: {len(unique_stats)}개")
    
    # 결과 저장
    results_df = pd.DataFrame(list(unique_stats.values()))
    results_df = results_df.sort_values(['category', 'TBL_ID'])
    
    # CSV 저장
    results_df.to_csv('kosis_statistics_list.csv', index=False, encoding='utf-8-sig')
    print(f"  결과 저장: kosis_statistics_list.csv")
    
    # JSON 저장
    with open('kosis_statistics_list.json', 'w', encoding='utf-8') as f:
        json.dump(list(unique_stats.values()), f, ensure_ascii=False, indent=2)
    print(f"  결과 저장: kosis_statistics_list.json")
    
    # 카테고리별 요약
    print("\n카테고리별 통계표 수:")
    category_counts = results_df['category'].value_counts()
    for cat, count in category_counts.items():
        print(f"  {cat}: {count}개")
    
    # 상위 20개 출력
    print("\n주요 통계표 (상위 20개):")
    for i, (_, row) in enumerate(results_df.head(20).iterrows(), 1):
        print(f"  {i:2d}. [{row['category']}] {row['TBL_NM']} (TBL_ID: {row['TBL_ID']})")
    
    return results_df

if __name__ == "__main__":
    find_statistics_for_categories()
