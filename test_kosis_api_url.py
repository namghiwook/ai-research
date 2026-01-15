"""
제공된 KOSIS API URL 테스트
"""
import requests
import pandas as pd
import json

def test_kosis_api():
    """제공된 KOSIS API URL 테스트"""
    
    url = "https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T10+T11+T12+T13+T14+T20+T21+T22+T23+T24+T30+T31+T32+T33+T34+&objL1=00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=000+020+025+030+035+040+045+050+055+060+065+070+075+080+085+086+&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=F&newEstPrdCnt=3&orgId=101&tblId=DT_1PM2002"
    
    print("=" * 80)
    print("KOSIS API URL 테스트")
    print("=" * 80)
    print(f"\nURL: {url[:100]}...")
    
    try:
        print("\n[1] API 호출 중...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        print(f"상태 코드: {response.status_code}")
        
        # JSON 파싱
        print("\n[2] 응답 데이터 파싱 중...")
        data = response.json()
        
        if isinstance(data, list):
            print(f"데이터 타입: 리스트")
            print(f"데이터 개수: {len(data)}개")
            
            # DataFrame으로 변환
            df = pd.DataFrame(data)
            
            print("\n[3] 데이터 구조 분석")
            print("-" * 80)
            print(f"행 수: {len(df)}")
            print(f"컬럼 수: {len(df.columns)}")
            print(f"\n컬럼 목록:")
            for i, col in enumerate(df.columns, 1):
                print(f"  {i}. {col}")
            
            print(f"\n[4] 데이터 샘플 (처음 5행):")
            print("-" * 80)
            print(df.head().to_string())
            
            print(f"\n[5] 데이터 통계 정보:")
            print("-" * 80)
            print(f"고유한 통계표ID: {df['TBL_ID'].nunique() if 'TBL_ID' in df.columns else 'N/A'}")
            print(f"고유한 기간: {df['PRD_DE'].unique() if 'PRD_DE' in df.columns else 'N/A'}")
            print(f"고유한 시도: {df['C1_NM'].nunique() if 'C1_NM' in df.columns else 'N/A'}")
            if 'C1_NM' in df.columns:
                print(f"시도 목록 (처음 10개): {df['C1_NM'].unique()[:10].tolist()}")
            
            # 데이터 저장
            output_file = "kosis_api_test_result.csv"
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\n[6] 데이터 저장 완료: {output_file}")
            
            # JSON으로도 저장 (원본 형태 보존)
            json_file = "kosis_api_test_result.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"JSON 저장 완료: {json_file}")
            
            print("\n" + "=" * 80)
            print("[성공] API 호출 및 데이터 수집 완료!")
            print("=" * 80)
            
            return df
            
        elif isinstance(data, dict):
            print(f"데이터 타입: 딕셔너리")
            print(f"키: {list(data.keys())}")
            print(f"데이터: {data}")
            return pd.DataFrame([data])
        else:
            print(f"알 수 없는 데이터 타입: {type(data)}")
            return pd.DataFrame()
            
    except requests.exceptions.RequestException as e:
        print(f"\n[오류] API 호출 실패: {str(e)}")
        return pd.DataFrame()
    except json.JSONDecodeError as e:
        print(f"\n[오류] JSON 파싱 실패: {str(e)}")
        print(f"응답 내용 (처음 500자): {response.text[:500]}")
        return pd.DataFrame()
    except Exception as e:
        print(f"\n[오류] 예상치 못한 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

if __name__ == "__main__":
    test_kosis_api()
