"""
최종 결과 파일 및 수집된 데이터를 기반으로 통계 질문에 답변
"""
import pandas as pd
import numpy as np
from kosis_data_collector_plan import KOSISPlanDataCollector
import json

def calculate_unmarried_male_20_24():
    """
    20~24세 남자 중 미혼인 인구 수 계산
    """
    print("=" * 80)
    print("20~24세 남자 중 미혼인 인구 수 계산")
    print("=" * 80)
    
    API_KEY = "ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY="
    
    # 1. 혼인상태 데이터 수집 (필요한 경우)
    print("\n[1단계] 혼인상태 데이터 확인")
    collector = KOSISPlanDataCollector(API_KEY)
    
    # 혼인상태 관련 URL
    marital_urls = {
        '연령성별혼인상태': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T10+T11+T12+T13+T14+T20+T21+T22+T23+T24+T30+T31+T32+T33+T34+&objL1=00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=000+020+025+030+035+040+045+050+055+060+065+070+075+080+085+086+&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=F&newEstPrdCnt=3&orgId=101&tblId=DT_1PM2002',
        '성연령혼인상태시군구': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T1+T2+T3+T4+T5+T6+T7+T8+T9+T10+T11+T12+&objL1=00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=ALL&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=Y&newEstPrdCnt=3&orgId=101&tblId=DT_1MR2060'
    }
    
    all_marital_data = []
    
    for name, url in marital_urls.items():
        print(f"\n[{name}] 데이터 수집 중...")
        df = collector.fetch_from_url(url, name)
        if not df.empty:
            df_cleaned = collector.clean_data(df)
            all_marital_data.append((name, df_cleaned))
            print(f"  수집 완료: {len(df_cleaned)}행")
    
    # 2. 20~24세 남자 미혼 데이터 추출
    print("\n[2단계] 20~24세 남자 미혼 데이터 추출")
    
    unmarried_20_24_male = []
    total_20_24_male = []
    
    for name, df in all_marital_data:
        if df.empty:
            continue
        
        # 필요한 컬럼 확인
        print(f"\n[{name}] 컬럼: {list(df.columns)}")
        
        # 연령대 컬럼 찾기
        age_col = None
        for col in df.columns:
            if 'C2' in col and 'NM' in col:
                age_col = col
                break
        
        # 성별 컬럼 찾기 (ITM_NM에서 추출)
        gender_col = 'ITM_NM' if 'ITM_NM' in df.columns else None
        
        # 값 컬럼 찾기
        value_col = 'DT' if 'DT' in df.columns else None
        
        if not age_col or not gender_col or not value_col:
            print(f"  경고: 필요한 컬럼을 찾을 수 없습니다.")
            continue
        
        # 20~24세 데이터 필터링
        age_mask = df[age_col].astype(str).str.contains('20|21|22|23|24', na=False)
        # 더 정확하게 20~24세 범위만 추출
        age_values = df[age_col].astype(str)
        age_mask = age_values.str.contains('20~24|20-24|20세~24세|20-24세', na=False)
        
        if age_mask.sum() == 0:
            # 다른 형식 시도
            age_mask = age_values.str.contains('^20|^21|^22|^23|^24', na=False)
        
        df_age = df[age_mask].copy()
        
        if len(df_age) == 0:
            print(f"  20~24세 데이터 없음")
            continue
        
        print(f"  20~24세 데이터: {len(df_age)}행")
        
        # 남자 데이터 필터링
        if gender_col:
            male_mask = df_age[gender_col].astype(str).str.contains('남자', na=False)
            df_male = df_age[male_mask].copy()
            
            print(f"  남자 데이터: {len(df_male)}행")
            
            # 미혼 데이터 추출
            unmarried_mask = df_male[gender_col].astype(str).str.contains('미혼', na=False)
            df_unmarried = df_male[unmarried_mask].copy()
            
            print(f"  미혼 데이터: {len(df_unmarried)}행")
            
            # 값 합계 계산
            if value_col:
                # DT 값 처리
                df_unmarried[value_col] = pd.to_numeric(df_unmarried[value_col], errors='coerce')
                df_unmarried = df_unmarried[df_unmarried[value_col].notna()]
                df_unmarried = df_unmarried[df_unmarried[value_col] > 0]
                
                unmarried_sum = df_unmarried[value_col].sum()
                total_sum = df_male[value_col].apply(lambda x: pd.to_numeric(x, errors='coerce')).sum()
                
                print(f"  20~24세 남자 미혼 인구 수: {unmarried_sum:,.0f}명")
                print(f"  20~24세 남자 전체 인구 수: {total_sum:,.0f}명")
                if total_sum > 0:
                    print(f"  미혼 비율: {unmarried_sum/total_sum*100:.2f}%")
                
                unmarried_20_24_male.append(unmarried_sum)
                total_20_24_male.append(total_sum)
    
    # 3. 최종 결과 파일과 결합하여 계산
    print("\n[3단계] 최종 결과 파일 기반 계산")
    
    try:
        final_df = pd.read_csv('final_joint_distribution.csv')
        
        # 20~24세 남자 전체 인구 (가중치 합계)
        male_20_24 = final_df[(final_df['Age_Group'] == '20-24') & (final_df['Gender'] == '남자')]
        total_weight = male_20_24['Weight'].sum()
        
        # 전체 인구 4,000만 명 기준으로 계산
        total_population = 40_000_000
        male_20_24_count = total_weight * total_population
        
        print(f"\n최종 결과 파일 기준:")
        print(f"  20~24세 남자 전체 인구 (가중치 합계): {total_weight:.6f}")
        print(f"  20~24세 남자 전체 인구 수 (4,000만 명 기준): {male_20_24_count:,.0f}명")
        
        # 원본 데이터에서 미혼 비율 계산
        if unmarried_20_24_male and total_20_24_male:
            avg_unmarried_ratio = sum(unmarried_20_24_male) / sum(total_20_24_male) if sum(total_20_24_male) > 0 else 0
            unmarried_count = male_20_24_count * avg_unmarried_ratio
            
            print(f"\n원본 데이터 기반 미혼 비율: {avg_unmarried_ratio*100:.2f}%")
            print(f"  20~24세 남자 중 미혼인 인구 수: {unmarried_count:,.0f}명")
            
            return unmarried_count, male_20_24_count, avg_unmarried_ratio
        
    except FileNotFoundError:
        print("  경고: final_joint_distribution.csv 파일을 찾을 수 없습니다.")
    
    # 원본 데이터만 사용
    if unmarried_20_24_male:
        total_unmarried = sum(unmarried_20_24_male)
        total_male = sum(total_20_24_male) if total_20_24_male else 0
        
        print(f"\n원본 데이터 직접 합계:")
        print(f"  20~24세 남자 중 미혼인 인구 수: {total_unmarried:,.0f}명")
        if total_male > 0:
            print(f"  20~24세 남자 전체 인구 수: {total_male:,.0f}명")
            print(f"  미혼 비율: {total_unmarried/total_male*100:.2f}%")
        
        return total_unmarried, total_male, total_unmarried/total_male if total_male > 0 else 0
    
    return None, None, None

if __name__ == "__main__":
    unmarried_count, total_count, ratio = calculate_unmarried_male_20_24()
    
    print("\n" + "=" * 80)
    print("최종 답변")
    print("=" * 80)
    if unmarried_count is not None:
        print(f"20~24세 남자 중 미혼인 인구 수: {unmarried_count:,.0f}명")
        if total_count:
            print(f"20~24세 남자 전체 인구 수: {total_count:,.0f}명")
            print(f"미혼 비율: {ratio*100:.2f}%")
    else:
        print("데이터를 찾을 수 없습니다.")
