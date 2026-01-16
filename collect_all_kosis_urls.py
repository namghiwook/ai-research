"""
plan.md에 명시된 URL과 추가로 수집 가능한 모든 KOSIS API URL 정리
"""
import json

API_KEY = "ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY="

# plan.md에 명시된 기본 URL들
PLAN_MD_URLS = {
    '인구가구주택': {
        'url': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T100+T110+T120+T130+T131+T132+T140+T141+T142+T200+T210+T220+T230+T310+T311+T312+T313+T314+T315+T320+&objL1=00+04+05+03+11+11010+11020+11030+11040+11050+11060+11070+11080+11090+11100+11110+11120+11130+11140+11150+11160+11170+11180+11190+11200+11210+11220+11230+11240+11250+21+21004+21005+21003+21010+21020+21030+21040+21050+21060+21070+21080+21090+21100+21120+21130+21140+21150+21510+22+22004+22005+22003+22010+22020+22030+22040+22050+22060+22070+22510+22520+23+23004+23005+23003+23010+23020+23030+23040+23050+23060+23070+23080+23090+23510+23520+24+24010+24020+24030+24040+24050+25+25010+25020+25030+25040+25050+26+26004+26005+26003+26010+26020+26030+26040+26510+29+29004+29005+29003+29010+31+31004+31005+31003+31010+31011+31012+31013+31014+31020+31021+31022+31023+31030+31040+31041+31042+31050+31051+31052+31053+31060+31070+31080+31090+31091+31092+31100+31101+31103+31104+31110+31120+31130+31140+31150+31160+31170+31180+31190+31191+31192+31193+31200+31210+31220+31230+31240+31250+31260+31270+31280+31550+31570+31580+32+32004+32005+32003+32010+32020+32030+32040+32050+32060+32070+32510+32520+32530+32540+32550+32560+32570+32580+32590+32600+32610+33+33004+33005+33003+33020+33030+33040+33041+33042+33043+33044+33520+33530+33540+33550+33560+33570+33580+33590+34+34004+34005+34003+34010+34011+34012+34020+34030+34040+34050+34060+34070+34080+34510+34530+34540+34550+34560+34570+34580+35+35004+35005+35003+35010+35011+35012+35020+35030+35040+35050+35060+35510+35520+35530+35540+35550+35560+35570+35580+36+36004+36005+36003+36010+36020+36030+36040+36060+36510+36520+36530+36550+36560+36570+36580+36590+36600+36610+36620+36630+36640+36650+36660+36670+36680+37+37004+37005+37003+37010+37011+37012+37020+37030+37040+37050+37060+37070+37080+37090+37100+37510+37520+37530+37540+37550+37560+37570+37580+37590+37600+37610+37620+37630+38+38004+38005+38003+38030+38050+38060+38070+38080+38090+38100+38110+38111+38112+38113+38114+38115+38510+38520+38530+38540+38550+38560+38570+38580+38590+38600+39+39004+39005+39003+39010+39020+&objL2=&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=Y&newEstPrdCnt=3&orgId=101&tblId=DT_1IN1502',
        'tbl_id': 'DT_1IN1502',
        'description': '인구, 가구 및 주택 – 읍면동(연도 끝자리 0, 5), 시군구(그 외 연도)'
    },
    '연령성별인구': {
        'url': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T00+T01+T02+T03+T10+T11+T12+T13+&objL1=00+04+05+03+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=000+005+010+015+020+025+030+035+040+045+050+055+060+065+070+075+080+085+090+095+100+101+102+103+104+086+126+127+&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=Y&newEstPrdCnt=3&orgId=101&tblId=DT_1IN1503',
        'tbl_id': 'DT_1IN1503',
        'description': '연령 및 성별 인구 – 읍면동'
    },
    '성연령혼인상태시군구': {
        'url': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T1+T2+T3+T4+T5+T6+T7+T8+T9+T10+T11+T12+&objL1=00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=ALL&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=Y&newEstPrdCnt=3&orgId=101&tblId=DT_1MR2060',
        'tbl_id': 'DT_1MR2060',
        'description': '성, 연령 및 혼인상태별 인구 - 시군구'
    },
    '성연령교육정도': {
        'url': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T10+T20+T21+T22+T23+T30+T31+T32+T33+T40+T41+T42+T43+T50+T51+T52+T53+T54+T55+T60+T61+T62+T63+T64+T65+T70+T71+T72+T73+T74+T80+T81+T82+T83+T84+T90+&objL1=00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=0+&objL3=000+&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=F&newEstPrdCnt=3&orgId=101&tblId=DT_1PM2001',
        'tbl_id': 'DT_1PM2001',
        'description': '성, 연령 및 교육정도, 교육상태별 인구(6세이상, 내국인)-시군구'
    },
    '성연령혼인교육정도': {
        'url': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T10+T20+T21+T22+T23+T30+T31+T32+T33+T40+T41+T42+T43+T50+T51+T52+T53+T54+T55+T60+T61+T62+T63+T64+T65+T70+T71+T72+T73+T74+T80+T81+T82+T83+T84+T90+&objL1=&objL2=00+&objL3=ALL&objL4=ALL&objL5=ALL&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=F&newEstPrdCnt=3&orgId=101&tblId=DT_1PM2003',
        'tbl_id': 'DT_1PM2003',
        'description': '성, 연령, 혼인상태 및 교육정도별 인구(15세 이상, 내국인)-시군구'
    },
    '연령성별혼인상태': {
        'url': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T10+T11+T12+T13+T14+T20+T21+T22+T23+T24+T30+T31+T32+T33+T34+&objL1=00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=000+020+025+030+035+040+045+050+055+060+065+070+075+080+085+086+&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=F&newEstPrdCnt=3&orgId=101&tblId=DT_1PM2002',
        'tbl_id': 'DT_1PM2002',
        'description': '연령별/성별/혼인상태별 인구(15세이상,내국인)-시군구'
    },
    '성별연령혼인동읍면': {
        'url': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T1+&objL1=00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=ALL&objL3=ALL&objL4=ALL&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=F&newEstPrdCnt=3&orgId=101&tblId=DT_1PM2007',
        'tbl_id': 'DT_1PM2007',
        'description': '성별/연령별/혼인상태별 인구(15세이상, 내국인)-동읍면'
    }
}

# plan.md에서 요구하는 추가 통계표들 (찾아야 할 항목)
REQUIRED_ADDITIONAL_STATS = {
    '경제_고용': {
        '산업_직업': {
            'keywords': ['산업', '직업', '종사상지위', 'DT_1DA7001'],
            'description': '산업 및 직업 대분류'
        },
        '종사상지위': {
            'keywords': ['종사상지위', '상용근로자', '임시근로자', '자영업자'],
            'description': '종사상 지위: 상용근로자, 임시근로자, 자영업자(고용원 유/무), 무급가족종사자'
        },
        '교육정도': {
            'keywords': ['교육정도', '학력', '중졸', '고졸', '대졸'],
            'description': '교육정도 (학력): 중졸/고졸/대졸/대학원졸'
        },
        '소득분위': {
            'keywords': ['소득분위', '가구소득', '소득'],
            'description': '소득분위 데이터 (10분위 또는 5분위)'
        }
    },
    '주거_가구': {
        '점유형태': {
            'keywords': ['점유형태', '자가', '전세', '월세'],
            'description': '점유형태 (자가, 전세, 월세)'
        },
        '거주주택종류': {
            'keywords': ['주택종류', '아파트', '단독주택', '연립', '다세대', '오피스텔'],
            'description': '거주주택 종류: 아파트, 단독주택, 연립/다세대, 오피스텔'
        },
        '가구원수_세대구성': {
            'keywords': ['가구원수', '세대구성', '1인가구', '부부', '3세대'],
            'description': '가구원수 및 세대구성: 1인 가구, 부부+자녀 가구, 3세대 가구'
        }
    }
}

def generate_all_urls():
    """
    모든 수집 가능한 KOSIS API URL 정리
    """
    print("=" * 80)
    print("KOSIS API URL 전체 정리")
    print("=" * 80)
    
    all_urls = {
        'plan_md_기본_urls': PLAN_MD_URLS,
        '추가_필요_통계표': REQUIRED_ADDITIONAL_STATS
    }
    
    # JSON 저장
    with open('all_kosis_urls.json', 'w', encoding='utf-8') as f:
        json.dump(all_urls, f, ensure_ascii=False, indent=2)
    
    print("\n[1] plan.md에 명시된 기본 URL (7개)")
    print("-" * 80)
    for i, (name, info) in enumerate(PLAN_MD_URLS.items(), 1):
        print(f"{i}. {name}")
        print(f"   TBL_ID: {info['tbl_id']}")
        print(f"   설명: {info['description']}")
        print()
    
    print("\n[2] plan.md에서 요구하는 추가 통계표 (찾아야 할 항목)")
    print("-" * 80)
    print("\n2-1. 경제 및 고용 관련 항목 (Socio-Economic):")
    for cat, items in REQUIRED_ADDITIONAL_STATS['경제_고용'].items():
        print(f"  - {cat}: {items['description']}")
        print(f"    검색 키워드: {', '.join(items['keywords'])}")
    
    print("\n2-2. 주거 및 가구 환경 관련 항목 (Housing & Household):")
    for cat, items in REQUIRED_ADDITIONAL_STATS['주거_가구'].items():
        print(f"  - {cat}: {items['description']}")
        print(f"    검색 키워드: {', '.join(items['keywords'])}")
    
    print("\n" + "=" * 80)
    print("결론")
    print("=" * 80)
    print("현재 상태:")
    print("  ✓ plan.md에 명시된 7개 URL만 사용됨")
    print("  ✗ 추가 통계표 (경제/고용, 주거/가구) 미수집")
    print("\n필요한 작업:")
    print("  1. KOSIS 통계 목록 조회하여 관련 통계표 찾기")
    print("  2. 각 통계표의 TBL_ID 확인")
    print("  3. API URL 생성 (기존 URL 형식 참고)")
    print("  4. 데이터 수집 및 고유값 추출")
    
    print(f"\n결과 저장: all_kosis_urls.json")
    
    return all_urls

if __name__ == "__main__":
    generate_all_urls()
