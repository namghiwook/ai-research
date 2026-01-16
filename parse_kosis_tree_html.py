"""
KOSIS 통계화면 HTML에서 트리 메뉴 파싱하여 통계표 추출 및 OpenAPI URL 생성
"""
import re
import json
from urllib.parse import urlencode

API_KEY = "ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY="

def parse_html_tree(html_content: str):
    """
    HTML에서 통계표 정보 추출
    """
    stats_list = []
    
    # showStats 함수 호출 패턴 찾기 (HTML 엔티티 포함)
    # &quot; 또는 " 모두 처리
    patterns = [
        r'showStats\(&quot;(\d+)&quot;,&quot;([^&]+)&quot;,&quot;([^&]*)&quot;,&quot;([^&]+)&quot;,&quot;([^&]+)&quot;,&quot;([^&]*)&quot;\)',
        r'showStats\("(\d+)","([^"]+)","([^"]*)","([^"]+)","([^"]+)","([^"]*)"\)',
        r'showStats\(&quot;(\d+)&quot;,\s*&quot;([^&]+)&quot;,\s*&quot;([^&]*)&quot;,\s*&quot;([^&]+)&quot;,\s*&quot;([^&]+)&quot;,\s*&quot;([^&]*)&quot;\)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html_content)
        for match in matches:
            org_id, tbl_id, tbl_se, parent_id, vw_cd, itm_id = match
            
            # 통계표명 추출 (title 속성)
            title_pattern = rf'<span[^>]*class=["\']statistics["\'][^>]*title=["\']([^"\']+)["\']'
            title_match = re.search(title_pattern, html_content)
            title = title_match.group(1) if title_match else f'{tbl_id}'
            
            # 해당 통계표 주변에서 title 찾기
            tbl_context_pattern = rf'treeDown_{re.escape(tbl_id)}[^<]*<span[^>]*title=["\']([^"\']+)["\']'
            context_match = re.search(tbl_context_pattern, html_content)
            if context_match:
                title = context_match.group(1)
            
            stats_list.append({
                'orgId': org_id,
                'tblId': tbl_id,
                'tblSe': tbl_se,
                'parentId': parent_id,
                'vwCd': vw_cd,
                'itmId': itm_id,
                'title': title
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
        '기타_인구': []
    }
    
    keywords_map = {
        '소득분위': ['소득', '분위', '가구소득', '소득분배'],
        '직업_산업': ['직업', '산업', 'DT_1DA7001', '종사'],
        '종사상지위': ['종사상지위', '상용근로자', '임시근로자', '자영업자'],
        '교육정도': ['교육정도', '학력', '졸업', '재학'],
        '주거_점유형태': ['점유형태', '자가', '전세', '월세', '주택점유'],
        '주택종류': ['주택종류', '아파트', '단독주택', '연립', '다세대', '오피스텔'],
        '가구원수_세대구성': ['가구원수', '세대구성', '가구주', '1인가구', '부부']
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
    print("KOSIS HTML 트리 메뉴 파싱 및 통계표 추출")
    print("=" * 80)
    
    # HTML 파일 읽기
    html_file = 'kosis_tree.html'
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"HTML 파일을 찾을 수 없습니다: {html_file}")
        print("HTML에서 직접 showStats 패턴을 찾습니다...")
        # 사용자가 제공한 HTML에서 직접 패턴 찾기
        html_content = """
        <li id="treeDown_DT_1IN1502"><a href="javascript:showStats(&quot;101&quot;,&quot;DT_1IN1502&quot;,&quot;N&quot;,&quot;A11_2015_1_10_10&quot;,&quot;MT_ZTITLE&quot;,&quot;&quot;)"><span class="statistics" title="인구, 가구 및 주택">인구, 가구 및 주택</span></a></li>
        <li id="treeDown_DT_1IN1503"><a href="javascript:showStats(&quot;101&quot;,&quot;DT_1IN1503&quot;,&quot;N&quot;,&quot;A11_2015_1_10_10&quot;,&quot;MT_ZTITLE&quot;,&quot;&quot;)"><span class="statistics" title="연령 및 성별 인구">연령 및 성별 인구</span></a></li>
        <li id="treeDown_DT_1PM2001"><a href="javascript:showStats(&quot;101&quot;,&quot;DT_1PM2001&quot;,&quot;N&quot;,&quot;A11_2015_1_001_001&quot;,&quot;MT_ZTITLE&quot;,&quot;&quot;)"><span class="statistics" title="성, 연령 및 교육정도">성, 연령 및 교육정도</span></a></li>
        <li id="treeDown_DT_1PM2002"><a href="javascript:showStats(&quot;101&quot;,&quot;DT_1PM2002&quot;,&quot;N&quot;,&quot;A11_2015_1_001_001&quot;,&quot;MT_ZTITLE&quot;,&quot;&quot;)"><span class="statistics" title="연령별/성별/혼인상태별">연령별/성별/혼인상태별</span></a></li>
        <li id="treeDown_DT_1PM2003"><a href="javascript:showStats(&quot;101&quot;,&quot;DT_1PM2003&quot;,&quot;N&quot;,&quot;A11_2015_1_001_001&quot;,&quot;MT_ZTITLE&quot;,&quot;&quot;)"><span class="statistics" title="성, 연령, 혼인상태 및 교육정도">성, 연령, 혼인상태 및 교육정도</span></a></li>
        <li id="treeDown_DT_1PM2007"><a href="javascript:showStats(&quot;101&quot;,&quot;DT_1PM2007&quot;,&quot;N&quot;,&quot;A11_2015_1_001_001&quot;,&quot;MT_ZTITLE&quot;,&quot;&quot;)"><span class="statistics" title="성별/연령별/혼인상태별">성별/연령별/혼인상태별</span></a></li>
        <li id="treeDown_DT_1MR2060"><a href="javascript:showStats(&quot;101&quot;,&quot;DT_1MR2060&quot;,&quot;N&quot;,&quot;A11_2015_1_10_10&quot;,&quot;MT_ZTITLE&quot;,&quot;&quot;)"><span class="statistics" title="성, 연령 및 혼인상태별">성, 연령 및 혼인상태별</span></a></li>
        """
    
    # HTML 파싱
    print("\n[1단계] HTML 파싱 중...")
    stats_list = parse_html_tree(html_content)
    print(f"  추출된 통계표: {len(stats_list)}개")
    
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
                'url': url
            })
    
    # JSON 저장
    with open('parsed_kosis_statistics.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total_count': len(stats_list),
            'categories': all_urls
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n결과 저장: parsed_kosis_statistics.json")
    
    # 요약 출력
    print("\n" + "=" * 80)
    print("추출 결과 요약")
    print("=" * 80)
    
    total_useful = 0
    for category, stats in categorized.items():
        if stats and category != '기타_인구':
            print(f"\n[{category}]: {len(stats)}개")
            for stat in stats[:5]:  # 상위 5개만
                print(f"  - {stat['title']} ({stat['tblId']})")
            if len(stats) > 5:
                print(f"  ... 외 {len(stats) - 5}개")
            total_useful += len(stats)
    
    print(f"\n총 유용한 통계표: {total_useful}개")
    
    return all_urls

if __name__ == "__main__":
    main()
