"""
사용자가 제공한 HTML에서 통계표 추출 및 OpenAPI URL 생성
"""
import re
import json
from urllib.parse import urlencode

API_KEY = "ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY="

# 사용자가 제공한 HTML에서 showStats 패턴 추출
html_snippet = """
<li id="treeDown_DT_1IN1502" style="background-color: rgb(216, 236, 241); width: 466px;"><img src="images/tree/icon_file.png" alt="인구, 가구 및 주택 – 읍면동(연도 끝자리 0, 5), 시군구(그 외 연도)"> <a href="javascript:showStats(&quot;101&quot;,&quot;DT_1IN1502&quot;,&quot;N&quot;,&quot;A11_2015_1_10_10&quot;,&quot;MT_ZTITLE&quot;,&quot;&quot;)"><span class="statistics" title="인구, 가구 및 주택 – 읍면동(연도 끝자리 0, 5), 시군구(그 외 연도)" style="background-color: rgb(216, 236, 241);">인구, 가구 및 주택 – 읍면동(연도 끝자리 0, 5), 시군구(그 외 연도) (년 2015~2024) </span></a></li>
<li id="treeDown_DT_1IN1503"><img src="images/tree/icon_file.png" alt="연령 및 성별 인구 – 읍면동"> <a href="javascript:showStats(&quot;101&quot;,&quot;DT_1IN1503&quot;,&quot;N&quot;,&quot;A11_2015_1_10_10&quot;,&quot;MT_ZTITLE&quot;,&quot;&quot;)"><span class="statistics" title="연령 및 성별 인구 – 읍면동">연령 및 성별 인구 – 읍면동 (년 2015~2024) </span></a></li>
<li id="treeDown_DT_1IN2030"><img src="images/tree/icon_file.png" alt="주요 인구지표(부양비, 노령화지수, 중위연령 등) - 시군구"> <a href="javascript:showStats(&quot;101&quot;,&quot;DT_1IN2030&quot;,&quot;N&quot;,&quot;A11_2015_1_10_10&quot;,&quot;MT_ZTITLE&quot;,&quot;&quot;)"><span class="statistics" title="주요 인구지표(부양비, 노령화지수, 중위연령 등) - 시군구">주요 인구지표(부양비, 노령화지수, 중위연령 등) - 시군구 (년 2015~2024) </span></a></li>
<li id="treeDown_DT_1IN1507"><img src="images/tree/icon_file.png" alt="성, 연령 및 가구주와의 관계별 인구 - 시군구"> <a href="javascript:showStats(&quot;101&quot;,&quot;DT_1IN1507&quot;,&quot;N&quot;,&quot;A11_2015_1_10_10&quot;,&quot;MT_ZTITLE&quot;,&quot;&quot;)"><span class="statistics" title="성, 연령 및 가구주와의 관계별 인구 - 시군구">성, 연령 및 가구주와의 관계별 인구 - 시군구 (년 2015~2024) </span></a></li>
<li id="treeDown_DT_1IN1509"><img src="images/tree/icon_file.png" alt="성, 연령 및 세대구성별 인구 - 시군구"> <a href="javascript:showStats(&quot;101&quot;,&quot;DT_1IN1509&quot;,&quot;N&quot;,&quot;A11_2015_1_10_10&quot;,&quot;MT_ZTITLE&quot;,&quot;&quot;)"><span class="statistics" title="성, 연령 및 세대구성별 인구 - 시군구">성, 연령 및 세대구성별 인구 - 시군구 (년 2015~2024) </span></a></li>
<li id="treeDown_DT_1MR2060" class="last"><img src="images/tree/icon_file.png" alt="성, 연령 및 혼인상태별 인구 - 시군구"> <a href="javascript:showStats(&quot;101&quot;,&quot;DT_1MR2060&quot;,&quot;N&quot;,&quot;A11_2015_1_10_10&quot;,&quot;MT_ZTITLE&quot;,&quot;&quot;)"><span class="statistics" title="성, 연령 및 혼인상태별 인구 - 시군구">성, 연령 및 혼인상태별 인구 - 시군구 (년 2022~2024) </span></a></li>
<li id="treeDown_DT_1PM2001"><img src="images/tree/icon_file.png" alt="성, 연령 및 교육정도, 교육상태별 인구(6세이상, 내국인)-시군구"> <a href="javascript:showStats(&quot;101&quot;,&quot;DT_1PM2001&quot;,&quot;N&quot;,&quot;A11_2015_1_001_001&quot;,&quot;MT_ZTITLE&quot;,&quot;&quot;)"><span class="statistics" title="성, 연령 및 교육정도, 교육상태별 인구(6세이상, 내국인)-시군구">성, 연령 및 교육정도, 교육상태별 인구(6세이상, 내국인)-시군구 (5년 2020~2020) </span></a></li>
<li id="treeDown_DT_1PM2002" style=""><img src="images/tree/icon_file.png" alt="연령별/성별/혼인상태별 인구(15세이상,내국인)-시군구"> <a href="javascript:showStats(&quot;101&quot;,&quot;DT_1PM2002&quot;,&quot;N&quot;,&quot;A11_2015_1_001_001&quot;,&quot;MT_ZTITLE&quot;,&quot;&quot;)"><span class="statistics" title="연령별/성별/혼인상태별 인구(15세이상,내국인)-시군구" style="">연령별/성별/혼인상태별 인구(15세이상,내국인)-시군구 (5년 2020~2020) </span></a></li>
<li id="treeDown_DT_1PM2003"><img src="images/tree/icon_file.png" alt="성, 연령, 혼인상태 및 교육정도별 인구(15세 이상, 내국인)-시군구"> <a href="javascript:showStats(&quot;101&quot;,&quot;DT_1PM2003&quot;,&quot;N&quot;,&quot;A11_2015_1_001_001&quot;,&quot;MT_ZTITLE&quot;,&quot;&quot;)"><span class="statistics" title="성, 연령, 혼인상태 및 교육정도별 인구(15세 이상, 내국인)-시군구">성, 연령, 혼인상태 및 교육정도별 인구(15세 이상, 내국인)-시군구 (5년 2020~2020) </span></a></li>
<li id="treeDown_DT_1PM2004"><img src="images/tree/icon_file.png" alt="가구주와의 관계별/성별/혼인상태별 인구(일반가구)-시군구"> <a href="javascript:showStats(&quot;101&quot;,&quot;DT_1PM2004&quot;,&quot;N&quot;,&quot;A11_2015_1_001_001&quot;,&quot;MT_ZTITLE&quot;,&quot;&quot;)"><span class="statistics" title="가구주와의 관계별/성별/혼인상태별 인구(일반가구)-시군구">가구주와의 관계별/성별/혼인상태별 인구(일반가구)-시군구 (5년 2020~2020) </span></a></li>
<li id="treeDown_DT_1PM2005"><img src="images/tree/icon_file.png" alt="성별/연령별/혼인상태별/세대구성별 인구(일반가구)-시군구"> <a href="javascript:showStats(&quot;101&quot;,&quot;DT_1PM2005&quot;,&quot;N&quot;,&quot;A11_2015_1_001_001&quot;,&quot;MT_ZTITLE&quot;,&quot;&quot;)"><span class="statistics" title="성별/연령별/혼인상태별/세대구성별 인구(일반가구)-시군구">성별/연령별/혼인상태별/세대구성별 인구(일반가구)-시군구 (5년 2020~2020) </span></a></li>
<li id="treeDown_DT_1PM2006"><img src="images/tree/icon_file.png" alt="성별/연령별/교육정도별 인구(6세이상, 내국인)-동읍면"> <a href="javascript:showStats(&quot;101&quot;,&quot;DT_1PM2006&quot;,&quot;N&quot;,&quot;A11_2015_1_001_001&quot;,&quot;MT_ZTITLE&quot;,&quot;&quot;)"><span class="statistics" title="성별/연령별/교육정도별 인구(6세이상, 내국인)-동읍면">성별/연령별/교육정도별 인구(6세이상, 내국인)-동읍면 (5년 2020~2020) </span></a></li>
<li id="treeDown_DT_1PM2007" class="last"><img src="images/tree/icon_file.png" alt="성별/연령별/혼인상태별 인구(15세이상, 내국인)-동읍면"> <a href="javascript:showStats(&quot;101&quot;,&quot;DT_1PM2007&quot;,&quot;N&quot;,&quot;A11_2015_1_001_001&quot;,&quot;MT_ZTITLE&quot;,&quot;&quot;)"><span class="statistics" title="성별/연령별/혼인상태별 인구(15세이상, 내국인)-동읍면">성별/연령별/혼인상태별 인구(15세이상, 내국인)-동읍면 (5년 2020~2020) </span></a></li>
"""

def extract_statistics(html_content: str):
    """
    HTML에서 통계표 정보 추출
    """
    stats_list = []
    
    # showStats 패턴 찾기 (HTML 엔티티 &quot; 처리)
    pattern = r'showStats\(&quot;(\d+)&quot;,&quot;([^&]+)&quot;,&quot;([^&]*)&quot;,&quot;([^&]+)&quot;,&quot;([^&]+)&quot;,&quot;([^&]*)&quot;\)'
    matches = re.findall(pattern, html_content)
    
    for match in matches:
        org_id, tbl_id, tbl_se, parent_id, vw_cd, itm_id = match
        
        # 통계표명 추출 - 해당 통계표가 나타나는 전체 li 블록 찾기
        title = f'{tbl_id}'
        
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
        '교육정도': [],
        '주거_점유형태': [],
        '주택종류': [],
        '가구원수_세대구성': [],
        '기타_인구': []
    }
    
    keywords_map = {
        '소득분위': ['소득', '분위', '가구소득', '소득분배'],
        '직업_산업': ['직업', '산업', 'DT_1DA7001', '종사'],
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
            categories['기타_인구'].append(stat)
    
    return categories

def main():
    """
    메인 함수
    """
    print("=" * 80)
    print("KOSIS HTML 트리 메뉴 파싱 및 통계표 추출")
    print("=" * 80)
    
    # HTML 파싱
    print("\n[1단계] HTML 파싱 중...")
    stats_list = extract_statistics(html_snippet)
    print(f"  추출된 통계표: {len(stats_list)}개")
    
    for stat in stats_list:
        print(f"    - {stat['tblId']}: {stat['title'][:50]}...")
    
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
        if stats:
            print(f"\n[{category}]: {len(stats)}개")
            for stat in stats[:5]:  # 상위 5개만
                print(f"  - {stat['title'][:60]} ({stat['tblId']})")
            if len(stats) > 5:
                print(f"  ... 외 {len(stats) - 5}개")
            if category != '기타_인구':
                total_useful += len(stats)
    
    print(f"\n총 유용한 통계표: {total_useful}개")
    
    return all_urls

if __name__ == "__main__":
    main()
