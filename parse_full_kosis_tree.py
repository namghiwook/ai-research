"""
KOSIS 통계 트리 HTML 전체 파싱 및 2020년 이후 통계표 추출
"""
import re
import json
from urllib.parse import urlencode

API_KEY = "ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY="

def extract_statistics_from_html(html_content: str):
    """
    HTML에서 통계표 정보 추출 (2020년 이후 데이터만)
    """
    stats_list = []
    
    # showStats 패턴 찾기 (HTML 엔티티 &quot; 처리)
    pattern = r'showStats\(&quot;(\d+)&quot;,&quot;([^&]+)&quot;,&quot;([^&]*)&quot;,&quot;([^&]+)&quot;,&quot;([^&]+)&quot;,&quot;([^&]*)&quot;\)'
    matches = re.findall(pattern, html_content)
    
    for match in matches:
        org_id, tbl_id, tbl_se, parent_id, vw_cd, itm_id = match
        
        # 통계표명 추출 - 해당 통계표가 나타나는 전체 li 블록 찾기
        title = f'{tbl_id}'
        period_info = ""
        
        # treeDown_TBL_ID로 시작하는 li 블록 찾기 (따옴표 또는 &quot; 모두 처리)
        li_patterns = [
            rf'<li[^>]*id=[\"\']treeDown_{re.escape(tbl_id)}[\"\'][^>]*>(.*?)</li>',
            rf'<li[^>]*id=&quot;treeDown_{re.escape(tbl_id)}&quot;[^>]*>(.*?)</li>'
        ]
        
        li_content = None
        for pattern in li_patterns:
            li_match = re.search(pattern, html_content, re.DOTALL)
            if li_match:
                li_content = li_match.group(1)
                break
        
        if li_content:
            # alt 속성에서 찾기 (img 태그) - 따옴표 또는 &quot; 모두 처리
            alt_patterns = [
                r'alt=[\"\']([^\"\']+)[\"\']',
                r'alt=&quot;([^&]+)&quot;'
            ]
            for alt_pattern in alt_patterns:
                alt_match = re.search(alt_pattern, li_content)
                if alt_match:
                    title = alt_match.group(1)
                    break
            
            # title 속성에서 찾기 (span 태그)
            if title == f'{tbl_id}':
                title_patterns = [
                    r'<span[^>]*title=[\"\']([^\"\']+)[\"\']',
                    r'<span[^>]*title=&quot;([^&]+)&quot;'
                ]
                for title_pattern in title_patterns:
                    span_match = re.search(title_pattern, li_content)
                    if span_match:
                        title = span_match.group(1)
                        break
            
            # 기간 정보 추출 (년도 범위)
            period_patterns = [
                r'\(년\s*(\d{4})~(\d{4})\)',
                r'\(5년\s*(\d{4})~(\d{4})\)',
                r'\(월,년\s*(\d{4})\.\d+~(\d{4})\.\d+\)',
                r'\(년\s*(\d{4})~(\d{4})\.\d+\)'
            ]
            
            for period_pattern in period_patterns:
                period_match = re.search(period_pattern, li_content)
                if period_match:
                    start_year = int(period_match.group(1))
                    end_year = int(period_match.group(2))
                    period_info = f"{start_year}~{end_year}"
                    
                    # 2020년 이후 데이터만 필터링
                    if end_year >= 2020:
                        break
                    else:
                        # 2020년 이후 데이터가 없으면 스킵
                        period_info = None
                        break
        
        # 2020년 이후 데이터가 있는 경우만 추가
        if period_info and period_info != "None":
            stats_list.append({
                'orgId': org_id,
                'tblId': tbl_id,
                'tblSe': tbl_se,
                'parentId': parent_id,
                'vwCd': vw_cd,
                'itmId': itm_id,
                'title': title,
                'period': period_info
            })
    
    # 중복 제거
    seen = set()
    unique_stats = []
    for stat in stats_list:
        key = (stat['orgId'], stat['tblId'])
        if key not in seen:
            seen.add(key)
            unique_stats.append(stat)
    
    return unique_stats

def generate_api_url(stat_info: dict) -> str:
    """
    통계표 정보로부터 OpenAPI URL 생성
    """
    base_url = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
    
    params = {
        'method': 'getList',
        'apiKey': API_KEY,
        'format': 'json',
        'jsonVD': 'Y',
        'orgId': stat_info['orgId'],
        'tblId': stat_info['tblId'],
        'prdSe': 'Y',  # 최신 연도
        'newEstPrdCnt': '3'
    }
    
    # 기본 objL1 (시도 전체) - 기존 URL 패턴 참고
    params['objL1'] = '00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+'
    
    return f"{base_url}?{urlencode(params, doseq=True)}"

def categorize_statistics(stats_list: list) -> dict:
    """
    통계표를 카테고리별로 분류
    """
    categories = {
        '소득분위': [],
        '직업_산업': [],
        '종사상지위': [],
        '교육정도': [],
        '주거_점유형태': [],
        '주택종류': [],
        '가구원수_세대구성': [],
        '혼인상태': [],
        '기타_인구': []
    }
    
    keywords_map = {
        '소득분위': ['소득', '분위', '가구소득', '소득분배', '소득수준'],
        '직업_산업': ['직업', '산업', 'DT_1DA7001', '종사', '직종'],
        '종사상지위': ['종사상지위', '상용근로자', '임시근로자', '자영업자', '고용형태'],
        '교육정도': ['교육정도', '학력', '졸업', '재학', '교육상태'],
        '주거_점유형태': ['점유형태', '자가', '전세', '월세', '주택점유', '주거실태'],
        '주택종류': ['주택종류', '아파트', '단독주택', '연립', '다세대', '오피스텔', '주택유형'],
        '가구원수_세대구성': ['가구원수', '세대구성', '가구주', '1인가구', '부부', '가구형태'],
        '혼인상태': ['혼인상태', '혼인', '미혼', '기혼', '배우자']
    }
    
    for stat in stats_list:
        title = stat.get('title', '').lower()
        tbl_id = stat.get('tblId', '').upper()
        
        categorized = False
        
        for category, keywords in keywords_map.items():
            if any(keyword.lower() in title or keyword.upper() in tbl_id for keyword in keywords):
                categories[category].append(stat)
                categorized = True
                break
        
        # 인구 관련은 기타로
        if not categorized:
            if '인구' in title or 'DT_1IN' in tbl_id or 'DT_1PM' in tbl_id or 'DT_1MR' in tbl_id:
                categories['기타_인구'].append(stat)
            else:
                categories['기타_인구'].append(stat)
    
    return categories

def main():
    """
    메인 함수
    """
    print("=" * 80)
    print("KOSIS HTML 트리 메뉴 전체 파싱 및 2020년 이후 통계표 추출")
    print("=" * 80)
    
    # HTML 파일 읽기
    html_file = 'doc/kosis_tree.txt'
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"HTML 파일을 찾을 수 없습니다: {html_file}")
        return
    
    # HTML 파싱
    print("\n[1단계] HTML 파싱 중...")
    stats_list = extract_statistics_from_html(html_content)
    print(f"  추출된 통계표 (2020년 이후): {len(stats_list)}개")
    
    # 카테고리별 분류
    print("\n[2단계] 카테고리별 분류 중...")
    categorized = categorize_statistics(stats_list)
    
    for category, stats in categorized.items():
        if stats:
            print(f"  {category}: {len(stats)}개")
    
    # OpenAPI URL 생성
    print("\n[3단계] OpenAPI URL 생성 중...")
    all_urls = {}
    
    for category, stats in categorized.items():
        if not stats:
            continue
        
        all_urls[category] = []
        for stat in stats:
            url = generate_api_url(stat)
            all_urls[category].append({
                'tblId': stat['tblId'],
                'title': stat['title'],
                'orgId': stat['orgId'],
                'period': stat.get('period', ''),
                'url': url
            })
    
    # JSON 저장
    with open('kosis_statistics_2020plus.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total_count': len(stats_list),
            'filter': '2020년 이후 데이터만',
            'categories': all_urls
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n결과 저장: kosis_statistics_2020plus.json")
    
    # 요약 출력
    print("\n" + "=" * 80)
    print("추출 결과 요약 (2020년 이후 데이터)")
    print("=" * 80)
    
    total_useful = 0
    priority_categories = ['소득분위', '직업_산업', '주거_점유형태', '주택종류', '교육정도', '가구원수_세대구성']
    
    for category in priority_categories:
        stats = categorized.get(category, [])
        if stats:
            print(f"\n[{category}]: {len(stats)}개")
            for stat in stats[:10]:  # 상위 10개만
                period = stat.get('period', '')
                print(f"  - {stat['title'][:60]} ({stat['tblId']}) [{period}]")
            if len(stats) > 10:
                print(f"  ... 외 {len(stats) - 10}개")
            total_useful += len(stats)
    
    print(f"\n총 우선순위 통계표: {total_useful}개")
    print(f"전체 통계표: {len(stats_list)}개")
    
    return all_urls

if __name__ == "__main__":
    main()
