"""
여러 KOSIS API URL을 사용한 데이터 수집 및 처리
"""
import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import json

class KOSISMultiDataCollector:
    def __init__(self, api_key: str):
        """
        KOSIS 다중 데이터 수집기 초기화
        
        Args:
            api_key: KOSIS OpenAPI 키
        """
        self.api_key = api_key
        self.param_url = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
        self.all_data = {}
        self.all_dimensions = {}
        
    def fetch_from_url(self, url: str, data_name: str) -> pd.DataFrame:
        """
        URL에서 직접 데이터 조회
        
        Args:
            url: KOSIS API URL
            data_name: 데이터 이름
            
        Returns:
            DataFrame: 조회된 데이터
        """
        try:
            print(f"\n[{data_name}] 데이터 수집 중...")
            print(f"  URL: {url[:100]}...")
            
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
                print(f"  수집 완료: {len(df)}행, {len(df.columns)}컬럼")
                self.all_data[data_name] = df
                return df
            else:
                print(f"  경고: 데이터가 없습니다.")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"  오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def extract_dimensions(self, df: pd.DataFrame, data_name: str) -> Dict[str, List]:
        """
        데이터프레임에서 차원 값들 추출
        
        Args:
            df: 데이터프레임
            data_name: 데이터 이름
            
        Returns:
            Dict: 차원별 고유 값 리스트
        """
        dimensions = {}
        
        # 시도/지역 관련 컬럼
        if 'C1_NM' in df.columns:
            dimensions['Sido'] = sorted(df['C1_NM'].unique().tolist())
        if 'C2_NM' in df.columns:
            dimensions['Sigungu'] = sorted(df['C2_NM'].unique().tolist())
        if 'C3_NM' in df.columns:
            dimensions['Dong'] = sorted(df['C3_NM'].unique().tolist())
        if 'C4_NM' in df.columns:
            dimensions['EupMyeon'] = sorted(df['C4_NM'].unique().tolist())
        
        # 연령 관련
        if 'C2_NM' in df.columns and any('세' in str(x) or '~' in str(x) for x in df['C2_NM'].unique()):
            age_groups = sorted([x for x in df['C2_NM'].unique() if '세' in str(x) or '~' in str(x)])
            if age_groups:
                dimensions['Age_Group'] = age_groups
        
        # 성별 관련 (ITM_NM에서 추출)
        if 'ITM_NM' in df.columns:
            genders = set()
            for itm_nm in df['ITM_NM'].unique():
                if '남자' in str(itm_nm):
                    genders.add('남자')
                elif '여자' in str(itm_nm):
                    genders.add('여자')
            if genders:
                dimensions['Gender'] = sorted(list(genders))
        
        # 혼인상태 관련
        if 'ITM_NM' in df.columns:
            marital_statuses = set()
            for itm_nm in df['ITM_NM'].unique():
                if '미혼' in str(itm_nm):
                    marital_statuses.add('미혼')
                elif '배우자있음' in str(itm_nm) or '배우자' in str(itm_nm):
                    marital_statuses.add('배우자있음')
                elif '사별' in str(itm_nm):
                    marital_statuses.add('사별')
                elif '이혼' in str(itm_nm):
                    marital_statuses.add('이혼')
            if marital_statuses:
                dimensions['Marital_Status'] = sorted(list(marital_statuses))
        
        # 교육정도 관련
        if 'ITM_NM' in df.columns:
            educations = set()
            for itm_nm in df['ITM_NM'].unique():
                if '졸업' in str(itm_nm) or '재학' in str(itm_nm) or '중퇴' in str(itm_nm):
                    educations.add(str(itm_nm))
            if educations:
                dimensions['Education'] = sorted(list(educations))
        
        # 기타 차원들 추출
        for col in df.columns:
            if col.startswith('C') and col.endswith('_NM') and col not in ['C1_NM', 'C2_NM', 'C3_NM', 'C4_NM']:
                unique_vals = sorted([x for x in df[col].unique() if pd.notna(x) and str(x) not in ['-', '', 'nan']])
                if len(unique_vals) > 0 and len(unique_vals) < 100:  # 너무 많은 값은 제외
                    dimensions[col] = unique_vals
        
        # 제외 값 필터링
        exclude_values = ['전국', '계', '소계', '합계', '동부', '읍부', '면부']
        for dim_name, dim_values in dimensions.items():
            dimensions[dim_name] = [v for v in dim_values if str(v) not in exclude_values]
        
        self.all_dimensions[data_name] = dimensions
        
        print(f"  추출된 차원: {list(dimensions.keys())}")
        for dim_name, dim_values in dimensions.items():
            print(f"    {dim_name}: {len(dim_values)}개 ({dim_values[:5] if len(dim_values) > 5 else dim_values})")
        
        return dimensions
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """데이터 클리닝"""
        if df.empty:
            return df
        
        df_cleaned = df.copy()
        exclude_values = ['계', '소계', '전국', '동부', '읍부', '면부', '합계']
        
        for col in df_cleaned.columns:
            if df_cleaned[col].dtype == 'object':
                df_cleaned = df_cleaned[~df_cleaned[col].isin(exclude_values)]
        
        return df_cleaned.reset_index(drop=True)
    
    def collect_all_data(self):
        """모든 KOSIS API URL에서 데이터 수집"""
        
        urls = {
            '인구가구주택': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T100+T110+T120+T130+T131+T132+T140+T141+T142+T200+T210+T220+T230+T310+T311+T312+T313+T314+T315+T320+&objL1=00+04+05+03+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=Y&newEstPrdCnt=3&orgId=101&tblId=DT_1IN1502',
            '연령성별인구': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T00+T01+T02+T03+T10+T11+T12+T13+&objL1=00+04+05+03+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=000+005+010+015+020+025+030+035+040+045+050+055+060+065+070+075+080+085+090+095+100+101+102+103+104+086+126+127+&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=Y&newEstPrdCnt=3&orgId=101&tblId=DT_1IN1503',
            '성연령혼인상태시군구': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T1+T2+T3+T4+T5+T6+T7+T8+T9+T10+T11+T12+&objL1=00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=ALL&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=Y&newEstPrdCnt=3&orgId=101&tblId=DT_1MR2060',
            '성연령교육정도': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T10+T20+T21+T22+T23+T30+T31+T32+T33+T40+T41+T42+T43+T50+T51+T52+T53+T54+T55+T60+T61+T62+T63+T64+T65+T70+T71+T72+T73+T74+T80+T81+T82+T83+T84+T90+&objL1=00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=0+&objL3=000+&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=F&newEstPrdCnt=3&orgId=101&tblId=DT_1PM2001',
            '성연령혼인교육정도': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T10+T20+T21+T22+T23+T30+T31+T32+T33+T40+T41+T42+T43+T50+T51+T52+T53+T54+T55+T60+T61+T62+T63+T64+T65+T70+T71+T72+T73+T74+T80+T81+T82+T83+T84+T90+&objL1=&objL2=00+&objL3=ALL&objL4=ALL&objL5=ALL&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=F&newEstPrdCnt=3&orgId=101&tblId=DT_1PM2003',
            '연령성별혼인상태': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T10+T11+T12+T13+T14+T20+T21+T22+T23+T24+T30+T31+T32+T33+T34+&objL1=00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=000+020+025+030+035+040+045+050+055+060+065+070+075+080+085+086+&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=F&newEstPrdCnt=3&orgId=101&tblId=DT_1PM2002',
            '성별연령혼인동읍면': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T1+&objL1=00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=ALL&objL3=ALL&objL4=ALL&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=F&newEstPrdCnt=3&orgId=101&tblId=DT_1PM2007'
        }
        
        all_dimensions_combined = {}
        
        for name, url in urls.items():
            df = self.fetch_from_url(url, name)
            if not df.empty:
                df_cleaned = self.clean_data(df)
                dimensions = self.extract_dimensions(df_cleaned, name)
                
                # 모든 차원 통합
                for dim_name, dim_values in dimensions.items():
                    if dim_name in all_dimensions_combined:
                        # 중복 제거하여 통합
                        all_dimensions_combined[dim_name] = sorted(list(set(all_dimensions_combined[dim_name] + dim_values)))
                    else:
                        all_dimensions_combined[dim_name] = dim_values
        
        return all_dimensions_combined
