"""
KOSIS 통계표 검색 스크립트
실제 통계표ID를 찾기 위한 검색 도구
"""
import pandas as pd
from kosis_data_collector import KOSISDataCollector

def search_tables():
    """KOSIS에서 통계표 검색"""
    
    API_KEY = "ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY="
    collector = KOSISDataCollector(API_KEY)
    
    print("=" * 80)
    print("KOSIS 통계표 검색")
    print("=" * 80)
    
    # 검색 키워드들
    keywords = [
        "연령 성별 인구 읍면동",
        "연령별 인구",
        "성별 인구",
        "혼인상태별 인구",
        "소득분위",
        "가구소득"
    ]
    
    for keyword in keywords:
        print(f"\n검색어: '{keyword}'")
        print("-" * 80)
        
        results = collector.search_statistics(keyword=keyword)
        
        if not results.empty:
            print(f"검색 결과: {len(results)}개")
            
            # 주요 컬럼 확인
            print(f"\n컬럼: {list(results.columns)}")
            
            # 처음 몇 개만 출력
            if 'TBL_NM' in results.columns:
                print(f"\n통계표명 (처음 5개):")
                for i, row in results.head(5).iterrows():
                    print(f"  {i+1}. {row.get('TBL_NM', 'N/A')}")
                    print(f"     TBL_ID: {row.get('TBL_ID', 'N/A')}")
                    print(f"     USER_STATS_ID: {row.get('USER_STATS_ID', 'N/A')}")
        else:
            print("검색 결과 없음")
        
        print()

if __name__ == "__main__":
    search_tables()
