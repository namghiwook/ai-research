"""
알려진 통계표 ID와 패턴을 기반으로 모든 수집 가능한 KOSIS API URL 생성
"""
import json
from urllib.parse import urlencode

API_KEY = "ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY="

# plan.md에 명시된 기본 URL들
PLAN_MD_BASE_URLS = {
    '인구가구주택': {
        'tbl_id': 'DT_1IN1502',
        'url': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T100+T110+T120+T130+T131+T132+T140+T141+T142+T200+T210+T220+T230+T310+T311+T312+T313+T314+T315+T320+&objL1=00+04+05+03+11+11010+11020+11030+11040+11050+11060+11070+11080+11090+11100+11110+11120+11130+11140+11150+11160+11170+11180+11190+11200+11210+11220+11230+11240+11250+21+21004+21005+21003+21010+21020+21030+21040+21050+21060+21070+21080+21090+21100+21120+21130+21140+21150+21510+22+22004+22005+22003+22010+22020+22030+22040+22050+22060+22070+22510+22520+23+23004+23005+23003+23010+23020+23030+23040+23050+23060+23070+23080+23090+23510+23520+24+24010+24020+24030+24040+24050+25+25010+25020+25030+25040+25050+26+26004+26005+26003+26010+26020+26030+26040+26510+29+29004+29005+29003+29010+31+31004+31005+31003+31010+31011+31012+31013+31014+31020+31021+31022+31023+31030+31040+31041+31042+31050+31051+31052+31053+31060+31070+31080+31090+31091+31092+31100+31101+31103+31104+31110+31120+31130+31140+31150+31160+31170+31180+31190+31191+31192+31193+31200+31210+31220+31230+31240+31250+31260+31270+31280+31550+31570+31580+32+32004+32005+32003+32010+32020+32030+32040+32050+32060+32070+32510+32520+32530+32540+32550+32560+32570+32580+32590+32600+32610+33+33004+33005+33003+33020+33030+33040+33041+33042+33043+33044+33520+33530+33540+33550+33560+33570+33580+33590+34+34004+34005+34003+34010+34011+34012+34020+34030+34040+34050+34060+34070+34080+34510+34530+34540+34550+34560+34570+34580+35+35004+35005+35003+35010+35011+35012+35020+35030+35040+35050+35060+35510+35520+35530+35540+35550+35560+35570+35580+36+36004+36005+36003+36010+36020+36030+36040+36060+36510+36520+36530+36550+36560+36570+36580+36590+36600+36610+36620+36630+36640+36650+36660+36670+36680+37+37004+37005+37003+37010+37011+37012+37020+37030+37040+37050+37060+37070+37080+37090+37100+37510+37520+37530+37540+37550+37560+37570+37580+37590+37600+37610+37620+37630+38+38004+38005+38003+38030+38050+38060+38070+38080+38090+38100+38110+38111+38112+38113+38114+38115+38510+38520+38530+38540+38550+38560+38570+38580+38590+38600+39+39004+39005+39003+39010+39020+&objL2=&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=Y&newEstPrdCnt=3&orgId=101&tblId=DT_1IN1502'
    },
    '연령성별인구': {
        'tbl_id': 'DT_1IN1503',
        'url': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T00+T01+T02+T03+T10+T11+T12+T13+&objL1=00+04+05+03+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=000+005+010+015+020+025+030+035+040+045+050+055+060+065+070+075+080+085+090+095+100+101+102+103+104+086+126+127+&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=Y&newEstPrdCnt=3&orgId=101&tblId=DT_1IN1503'
    },
    '성연령혼인상태시군구': {
        'tbl_id': 'DT_1MR2060',
        'url': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T1+T2+T3+T4+T5+T6+T7+T8+T9+T10+T11+T12+&objL1=00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=ALL&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=Y&newEstPrdCnt=3&orgId=101&tblId=DT_1MR2060'
    },
    '성연령교육정도': {
        'tbl_id': 'DT_1PM2001',
        'url': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T10+T20+T21+T22+T23+T30+T31+T32+T33+T40+T41+T42+T43+T50+T51+T52+T53+T54+T55+T60+T61+T62+T63+T64+T65+T70+T71+T72+T73+T74+T80+T81+T82+T83+T84+T90+&objL1=00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=0+&objL3=000+&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=F&newEstPrdCnt=3&orgId=101&tblId=DT_1PM2001'
    },
    '성연령혼인교육정도': {
        'tbl_id': 'DT_1PM2003',
        'url': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T10+T20+T21+T22+T23+T30+T31+T32+T33+T40+T41+T42+T43+T50+T51+T52+T53+T54+T55+T60+T61+T62+T63+T64+T65+T70+T71+T72+T73+T74+T80+T81+T82+T83+T84+T90+&objL1=&objL2=00+&objL3=ALL&objL4=ALL&objL5=ALL&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=F&newEstPrdCnt=3&orgId=101&tblId=DT_1PM2003'
    },
    '연령성별혼인상태': {
        'tbl_id': 'DT_1PM2002',
        'url': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T10+T11+T12+T13+T14+T20+T21+T22+T23+T24+T30+T31+T32+T33+T34+&objL1=00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=000+020+025+030+035+040+045+050+055+060+065+070+075+080+085+086+&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=F&newEstPrdCnt=3&orgId=101&tblId=DT_1PM2002'
    },
    '성별연령혼인동읍면': {
        'tbl_id': 'DT_1PM2007',
        'url': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T1+&objL1=00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=ALL&objL3=ALL&objL4=ALL&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=F&newEstPrdCnt=3&orgId=101&tblId=DT_1PM2007'
    }
}

# 추가로 찾아야 할 통계표들 (알려진 TBL_ID 패턴 기반)
# 주의: 실제 존재 여부 확인 필요
ADDITIONAL_STATISTICS = {
    '소득분위': [
        {
            'tbl_id': 'DT_1HD1501',  # 가계금융복지조사 - 가구소득
            'description': '가계금융복지조사 가구소득 (추정)',
            'note': '실제 TBL_ID 확인 필요'
        },
        {
            'tbl_id': 'DT_1HD1502',  # 가계금융복지조사 - 소득분위
            'description': '가계금융복지조사 소득분위 (추정)',
            'note': '실제 TBL_ID 확인 필요'
        }
    ],
    '산업_직업': [
        {
            'tbl_id': 'DT_1DA7001',  # plan.md에 명시됨
            'description': '산업 및 직업 대분류',
            'note': 'plan.md에 명시된 통계표'
        }
    ],
    '주거_점유형태': [
        {
            'tbl_id': 'DT_1HS1501',  # 주거실태조사 - 점유형태 (추정)
            'description': '주거실태조사 점유형태',
            'note': '실제 TBL_ID 확인 필요'
        }
    ],
    '주택종류': [
        {
            'tbl_id': 'DT_1HS1502',  # 주거실태조사 - 주택종류 (추정)
            'description': '주거실태조사 주택종류',
            'note': '실제 TBL_ID 확인 필요'
        }
    ],
    '가구원수': [
        {
            'tbl_id': 'DT_1IN1502',  # 이미 수집 중 (인구가구주택)
            'description': '인구, 가구 및 주택',
            'note': '이미 수집 중인 통계표'
        }
    ]
}

def generate_url_for_tbl(tbl_id: str, base_params: dict = None) -> str:
    """
    TBL_ID를 기반으로 기본 API URL 생성
    """
    base_url = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
    
    params = {
        'method': 'getList',
        'apiKey': API_KEY,
        'format': 'json',
        'jsonVD': 'Y',
        'orgId': '101',
        'tblId': tbl_id,
        'prdSe': 'Y',
        'newEstPrdCnt': '3'
    }
    
    # 기본 objL1 (시도 전체) - 기존 URL 패턴 참고
    if base_params:
        params.update(base_params)
    else:
        params['objL1'] = '00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+'
    
    return f"{base_url}?{urlencode(params, doseq=True)}"

def build_complete_url_list():
    """
    모든 수집 가능한 KOSIS API URL 정리
    """
    print("=" * 80)
    print("모든 수집 가능한 KOSIS API URL 정리")
    print("=" * 80)
    
    all_urls = {
        'plan_md_기본_urls': PLAN_MD_BASE_URLS,
        '추가_통계표_후보': {}
    }
    
    # 추가 통계표 URL 생성
    for category, stats in ADDITIONAL_STATISTICS.items():
        all_urls['추가_통계표_후보'][category] = []
        for stat in stats:
            url = generate_url_for_tbl(stat['tbl_id'])
            all_urls['추가_통계표_후보'][category].append({
                'TBL_ID': stat['tbl_id'],
                'description': stat['description'],
                'note': stat['note'],
                'url': url,
                'status': '확인_필요'
            })
    
    # JSON 저장
    with open('all_kosis_urls_complete.json', 'w', encoding='utf-8') as f:
        json.dump(all_urls, f, ensure_ascii=False, indent=2)
    
    # 마크다운 형식으로도 저장
    with open('all_kosis_urls.md', 'w', encoding='utf-8') as f:
        f.write("# 모든 수집 가능한 KOSIS API URL 목록\n\n")
        f.write("## 1. plan.md에 명시된 기본 URL (7개)\n\n")
        for i, (name, info) in enumerate(PLAN_MD_BASE_URLS.items(), 1):
            f.write(f"### {i}. {name}\n")
            f.write(f"- **TBL_ID**: `{info['tbl_id']}`\n")
            f.write(f"- **URL**: {info['url']}\n\n")
        
        f.write("## 2. 추가 통계표 후보 (확인 필요)\n\n")
        for category, stats in ADDITIONAL_STATISTICS.items():
            f.write(f"### {category}\n\n")
            for stat in stats:
                f.write(f"- **TBL_ID**: `{stat['tbl_id']}`\n")
                f.write(f"- **설명**: {stat['description']}\n")
                f.write(f"- **비고**: {stat['note']}\n")
                url = generate_url_for_tbl(stat['tbl_id'])
                f.write(f"- **URL**: {url}\n\n")
    
    print("\n[1] plan.md에 명시된 기본 URL (7개)")
    print("-" * 80)
    for i, (name, info) in enumerate(PLAN_MD_BASE_URLS.items(), 1):
        print(f"{i}. {name} ({info['tbl_id']})")
    
    print("\n[2] 추가 통계표 후보 (확인 필요)")
    print("-" * 80)
    for category, stats in ADDITIONAL_STATISTICS.items():
        print(f"\n{category}:")
        for stat in stats:
            print(f"  - {stat['tbl_id']}: {stat['description']}")
            print(f"    비고: {stat['note']}")
    
    print("\n" + "=" * 80)
    print("결과 저장:")
    print("  - all_kosis_urls_complete.json")
    print("  - all_kosis_urls.md")
    print("=" * 80)
    
    return all_urls

if __name__ == "__main__":
    build_complete_url_list()
