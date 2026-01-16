"""
KOSIS 데이터 수집 및 처리 (plan.md 요구사항 기반)
"""
import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import json
import re

class KOSISPlanDataCollector:
    def __init__(self, api_key: str):
        """
        KOSIS 데이터 수집기 초기화
        
        Args:
            api_key: KOSIS OpenAPI 키
        """
        self.api_key = api_key
        self.param_url = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
        self.all_data = {}
        
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
            
            response = requests.get(url, timeout=120)
            response.raise_for_status()
            
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
                print(f"  수집 완료: {len(df)}행, {len(df.columns)}컬럼")
                print(f"  컬럼: {list(df.columns)}")
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
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        데이터 클리닝: 합계 행 제거, 특정 값 제외
        
        Args:
            df: 원본 데이터프레임
            
        Returns:
            DataFrame: 클리닝된 데이터프레임
        """
        if df.empty:
            return df
        
        df_cleaned = df.copy()
        
        # 제외할 값들
        exclude_values = ['계', '소계', '전국', '동부', '읍부', '면부', '합계', '기타']
        
        # 모든 컬럼에서 제외 값 필터링 (한 번에 수행)
        mask = pd.Series([True] * len(df_cleaned))
        
        for col in df.columns:
            if col in df_cleaned.columns and df_cleaned[col].dtype == 'object':
                # 정확히 일치하는 값 제외
                col_mask = ~df_cleaned[col].isin(exclude_values)
                # 부분 일치도 제거 (예: "계"가 포함된 경우)
                col_mask = col_mask & df_cleaned[col].astype(str).apply(
                    lambda x: not any(exc in str(x) for exc in exclude_values)
                )
                mask = mask & col_mask
        
        df_cleaned = df_cleaned[mask]
        
        return df_cleaned.reset_index(drop=True)
    
    def normalize_sido(self, sido: str) -> str:
        """
        시도 이름 정규화
        
        Args:
            sido: 원본 시도 이름
            
        Returns:
            str: 정규화된 시도 이름
        """
        sido = str(sido).strip()
        
        # 특별자치도/특별시 통합
        if '강원특별자치도' in sido or '강원도' in sido:
            return '강원도'
        elif '전북특별자치도' in sido or '전라북도' in sido:
            return '전라북도'
        elif '제주특별자치도' in sido or '제주도' in sido:
            return '제주도'
        elif '세종특별자치시' in sido or '세종시' in sido:
            return '세종시'
        elif '서울특별시' in sido:
            return '서울특별시'
        elif '부산광역시' in sido:
            return '부산광역시'
        elif '대구광역시' in sido:
            return '대구광역시'
        elif '인천광역시' in sido:
            return '인천광역시'
        elif '광주광역시' in sido:
            return '광주광역시'
        elif '대전광역시' in sido:
            return '대전광역시'
        elif '울산광역시' in sido:
            return '울산광역시'
        elif '경기도' in sido:
            return '경기도'
        elif '경상남도' in sido:
            return '경상남도'
        elif '경상북도' in sido:
            return '경상북도'
        elif '전라남도' in sido:
            return '전라남도'
        elif '충청남도' in sido:
            return '충청남도'
        elif '충청북도' in sido:
            return '충청북도'
        else:
            return sido
    
    def extract_age_group(self, age_str: str) -> Optional[str]:
        """
        연령 문자열에서 연령대 추출
        
        Args:
            age_str: 연령 문자열 (예: "15세", "15-19세", "20~24세")
            
        Returns:
            Optional[str]: 연령대 (예: "15-19") 또는 None
        """
        if pd.isna(age_str):
            return None
        
        age_str = str(age_str).strip()
        
        # 연령대 매핑
        age_groups = [
            '15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49',
            '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80-84',
            '85-89', '90-94', '95-99', '100+'
        ]
        
        # 숫자 추출
        numbers = re.findall(r'\d+', age_str)
        if not numbers:
            return None
        
        age = int(numbers[0])
        
        # 연령대 매핑
        if age < 15:
            return None
        elif age >= 100:
            return '100+'
        else:
            # 5세 단위로 그룹화
            lower = (age // 5) * 5
            upper = lower + 4
            age_group = f"{lower}-{upper}"
            if age_group in age_groups:
                return age_group
        
        return None
    
    def extract_gender(self, gender_str: str) -> Optional[str]:
        """
        성별 추출
        
        Args:
            gender_str: 성별 문자열
            
        Returns:
            Optional[str]: "남자" 또는 "여자" 또는 None
        """
        if pd.isna(gender_str):
            return None
        
        gender_str = str(gender_str).strip()
        
        if '남자' in gender_str or '남' in gender_str:
            return '남자'
        elif '여자' in gender_str or '여' in gender_str:
            return '여자'
        
        return None
    
    def collect_all_data(self) -> Dict[str, pd.DataFrame]:
        """
        plan.md에 명시된 모든 KOSIS API URL에서 데이터 수집
        
        Returns:
            Dict[str, pd.DataFrame]: 데이터 이름별 데이터프레임 딕셔너리
        """
        urls = {
            '인구가구주택': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T100+T110+T120+T130+T131+T132+T140+T141+T142+T200+T210+T220+T230+T310+T311+T312+T313+T314+T315+T320+&objL1=00+04+05+03+11+11010+11020+11030+11040+11050+11060+11070+11080+11090+11100+11110+11120+11130+11140+11150+11160+11170+11180+11190+11200+11210+11220+11230+11240+11250+21+21004+21005+21003+21010+21020+21030+21040+21050+21060+21070+21080+21090+21100+21120+21130+21140+21150+21510+22+22004+22005+22003+22010+22020+22030+22040+22050+22060+22070+22510+22520+23+23004+23005+23003+23010+23020+23030+23040+23050+23060+23070+23080+23090+23510+23520+24+24010+24020+24030+24040+24050+25+25010+25020+25030+25040+25050+26+26004+26005+26003+26010+26020+26030+26040+26510+29+29004+29005+29003+29010+31+31004+31005+31003+31010+31011+31012+31013+31014+31020+31021+31022+31023+31030+31040+31041+31042+31050+31051+31052+31053+31060+31070+31080+31090+31091+31092+31100+31101+31103+31104+31110+31120+31130+31140+31150+31160+31170+31180+31190+31191+31192+31193+31200+31210+31220+31230+31240+31250+31260+31270+31280+31550+31570+31580+32+32004+32005+32003+32010+32020+32030+32040+32050+32060+32070+32510+32520+32530+32540+32550+32560+32570+32580+32590+32600+32610+33+33004+33005+33003+33020+33030+33040+33041+33042+33043+33044+33520+33530+33540+33550+33560+33570+33580+33590+34+34004+34005+34003+34010+34011+34012+34020+34030+34040+34050+34060+34070+34080+34510+34530+34540+34550+34560+34570+34580+35+35004+35005+35003+35010+35011+35012+35020+35030+35040+35050+35060+35510+35520+35530+35540+35550+35560+35570+35580+36+36004+36005+36003+36010+36020+36030+36040+36060+36510+36520+36530+36550+36560+36570+36580+36590+36600+36610+36620+36630+36640+36650+36660+36670+36680+37+37004+37005+37003+37010+37011+37012+37020+37030+37040+37050+37060+37070+37080+37090+37100+37510+37520+37530+37540+37550+37560+37570+37580+37590+37600+37610+37620+37630+38+38004+38005+38003+38030+38050+38060+38070+38080+38090+38100+38110+38111+38112+38113+38114+38115+38510+38520+38530+38540+38550+38560+38570+38580+38590+38600+39+39004+39005+39003+39010+39020+&objL2=&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=Y&newEstPrdCnt=3&orgId=101&tblId=DT_1IN1502',
            '연령성별인구': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T00+T01+T02+T03+T10+T11+T12+T13+&objL1=00+04+05+03+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=000+005+010+015+020+025+030+035+040+045+050+055+060+065+070+075+080+085+090+095+100+101+102+103+104+086+126+127+&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=Y&newEstPrdCnt=3&orgId=101&tblId=DT_1IN1503',
            '성연령혼인상태시군구': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T1+T2+T3+T4+T5+T6+T7+T8+T9+T10+T11+T12+&objL1=00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=ALL&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=Y&newEstPrdCnt=3&orgId=101&tblId=DT_1MR2060',
            '성연령교육정도': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T10+T20+T21+T22+T23+T30+T31+T32+T33+T40+T41+T42+T43+T50+T51+T52+T53+T54+T55+T60+T61+T62+T63+T64+T65+T70+T71+T72+T73+T74+T80+T81+T82+T83+T84+T90+&objL1=00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=0+&objL3=000+&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=F&newEstPrdCnt=3&orgId=101&tblId=DT_1PM2001',
            '성연령혼인교육정도': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T10+T20+T21+T22+T23+T30+T31+T32+T33+T40+T41+T42+T43+T50+T51+T52+T53+T54+T55+T60+T61+T62+T63+T64+T65+T70+T71+T72+T73+T74+T80+T81+T82+T83+T84+T90+&objL1=&objL2=00+&objL3=ALL&objL4=ALL&objL5=ALL&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=F&newEstPrdCnt=3&orgId=101&tblId=DT_1PM2003',
            '연령성별혼인상태': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T10+T11+T12+T13+T14+T20+T21+T22+T23+T24+T30+T31+T32+T33+T34+&objL1=00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=000+020+025+030+035+040+045+050+055+060+065+070+075+080+085+086+&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=F&newEstPrdCnt=3&orgId=101&tblId=DT_1PM2002',
            '성별연령혼인동읍면': 'https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY=&itmId=T1+&objL1=00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+&objL2=ALL&objL3=ALL&objL4=ALL&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=F&newEstPrdCnt=3&orgId=101&tblId=DT_1PM2007'
        }
        
        collected_data = {}
        
        for name, url in urls.items():
            df = self.fetch_from_url(url, name)
            if not df.empty:
                df_cleaned = self.clean_data(df)
                collected_data[name] = df_cleaned
                print(f"  [{name}] 클리닝 완료: {len(df_cleaned)}행")
        
        return collected_data
    
    def convert_age_group_format(self, age_str: str) -> Optional[str]:
        """
        연령 문자열을 plan.md 형식으로 변환
        
        Args:
            age_str: 연령 문자열 (예: "15~19세", "20-24세", "85세이상")
            
        Returns:
            Optional[str]: 변환된 연령대 (예: "15-19", "20-24", "100+") 또는 None
        """
        if pd.isna(age_str):
            return None
        
        age_str = str(age_str).strip()
        
        # plan.md에 명시된 연령대 목록
        target_age_groups = [
            '15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49',
            '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80-84',
            '85-89', '90-94', '95-99', '100+'
        ]
        
        # 이미 올바른 형식인 경우
        if age_str in target_age_groups:
            return age_str
        
        # 숫자 추출
        numbers = re.findall(r'\d+', age_str)
        if not numbers:
            return None
        
        # "이상" 처리
        if '이상' in age_str or '+' in age_str:
            age = int(numbers[0])
            if age >= 100:
                return '100+'
            elif age >= 85:
                # 85세 이상은 85-89로 매핑 (또는 100+)
                return '85-89' if age < 90 else ('90-94' if age < 95 else ('95-99' if age < 100 else '100+'))
            else:
                # 5세 단위로 그룹화
                lower = (age // 5) * 5
                if lower < 15:
                    return None
                upper = lower + 4
                age_group = f"{lower}-{upper}"
                return age_group if age_group in target_age_groups else None
        
        # 범위 처리 (예: "15~19세", "20-24세")
        if len(numbers) >= 2:
            lower = int(numbers[0])
            upper = int(numbers[1])
            age_group = f"{lower}-{upper}"
            if age_group in target_age_groups:
                return age_group
        
        # 단일 숫자 처리
        if len(numbers) == 1:
            age = int(numbers[0])
            if age < 15:
                return None
            elif age >= 100:
                return '100+'
            else:
                # 5세 단위로 그룹화
                lower = (age // 5) * 5
                upper = lower + 4
                age_group = f"{lower}-{upper}"
                if age_group in target_age_groups:
                    return age_group
        
        return None
    
    def extract_dimensions_from_data(self, all_data: Dict[str, pd.DataFrame]) -> Dict[str, List]:
        """
        수집된 데이터에서 차원 값들 추출
        
        Args:
            all_data: 수집된 데이터 딕셔너리
            
        Returns:
            Dict[str, List]: 차원별 고유 값 리스트
        """
        dimensions = {
            'Sido': set(),
            'Age_Group': set(),
            'Gender': set(),
            'Income_Quintile': set()
        }
        
        # plan.md에 명시된 연령대 (기본값)
        target_age_groups = [
            '15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49',
            '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80-84',
            '85-89', '90-94', '95-99', '100+'
        ]
        
        # plan.md에 명시된 시도 목록
        target_sidos = [
            '강원도', '경기도', '경상남도', '경상북도', '광주광역시', '대구광역시',
            '대전광역시', '부산광역시', '서울특별시', '세종시', '울산광역시',
            '인천광역시', '전라남도', '전라북도', '제주도', '충청남도', '충청북도'
        ]
        
        # 모든 데이터에서 차원 추출
        for name, df in all_data.items():
            if df.empty:
                continue
            
            # 시도 추출 (C1_NM)
            if 'C1_NM' in df.columns:
                for sido in df['C1_NM'].dropna().unique():
                    normalized = self.normalize_sido(str(sido))
                    if normalized and normalized in target_sidos:
                        dimensions['Sido'].add(normalized)
            
            # 연령대 추출 (C2_NM 또는 다른 컬럼)
            age_cols = [col for col in df.columns if 'C2' in col and 'NM' in col]
            for col in age_cols:
                for age_str in df[col].dropna().unique():
                    age_group = self.convert_age_group_format(str(age_str))
                    if age_group and age_group in target_age_groups:
                        dimensions['Age_Group'].add(age_group)
            
            # 성별 추출 (ITM_NM)
            if 'ITM_NM' in df.columns:
                for itm_nm in df['ITM_NM'].dropna().unique():
                    itm_str = str(itm_nm)
                    if '남자' in itm_str:
                        dimensions['Gender'].add('남자')
                    elif '여자' in itm_str:
                        dimensions['Gender'].add('여자')
            
            # 소득분위 추출
            for col in df.columns:
                if '소득' in str(col) or '분위' in str(col):
                    for val in df[col].dropna().unique():
                        val_str = str(val)
                        # 10분위 추출
                        for i in range(1, 11):
                            if f'{i}분위' in val_str:
                                dimensions['Income_Quintile'].add(f'{i}분위')
                        # 5분위 추출
                        for i in range(1, 6):
                            if f'{i}분위' in val_str and f'{i}0분위' not in val_str:
                                dimensions['Income_Quintile'].add(f'{i}분위')
        
        # 기본값 설정
        if not dimensions['Sido']:
            dimensions['Sido'] = set(target_sidos)
        if not dimensions['Age_Group']:
            dimensions['Age_Group'] = set(target_age_groups)
        if not dimensions['Gender']:
            dimensions['Gender'] = {'남자', '여자'}
        if not dimensions['Income_Quintile']:
            # 10분위 우선
            dimensions['Income_Quintile'] = {f'{i}분위' for i in range(1, 11)}
            print("  경고: 소득분위 데이터를 찾을 수 없어 기본값(10분위) 사용")
        
        # 정렬 및 리스트로 변환
        result = {
            'Sido': sorted(list(dimensions['Sido'])),
            'Age_Group': sorted(list(dimensions['Age_Group']), 
                              key=lambda x: (int(x.split('-')[0]) if '-' in x else (1000 if '+' in x else 999))),
            'Gender': sorted(list(dimensions['Gender'])),
            'Income_Quintile': sorted(list(dimensions['Income_Quintile']), 
                                     key=lambda x: int(re.findall(r'\d+', x)[0]))
        }
        
        return result
    
    def convert_to_constraint_format(self, df: pd.DataFrame, 
                                     constraint_type: str) -> pd.DataFrame:
        """
        KOSIS 데이터를 제약 조건 형식으로 변환
        
        Args:
            df: 원본 데이터프레임
            constraint_type: 제약 조건 타입 ('sido_age_gender', 'age_income' 등)
            
        Returns:
            DataFrame: 변환된 제약 조건 데이터프레임
        """
        result = []
        
        # 클리닝
        df = self.clean_data(df)
        
        # '전국' 제외
        if 'C1_NM' in df.columns:
            df = df[df['C1_NM'] != '전국'].copy()
        
        # DT 컬럼 찾기
        value_col = 'DT' if 'DT' in df.columns else None
        if not value_col:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                value_col = numeric_cols[0]
            else:
                return pd.DataFrame()
        
        for _, row in df.iterrows():
            # 값 추출
            try:
                value = float(row[value_col])
                if pd.isna(value) or value <= 0:
                    continue
            except (ValueError, TypeError):
                continue
            
            # 제약 조건 타입에 따라 변환
            if constraint_type == 'sido_age_gender':
                # 시도 x 연령 x 성별
                if 'C1_NM' not in df.columns or 'ITM_NM' not in df.columns:
                    continue
                
                sido = self.normalize_sido(str(row['C1_NM']))
                if sido not in ['강원도', '경기도', '경상남도', '경상북도', '광주광역시', '대구광역시',
                               '대전광역시', '부산광역시', '서울특별시', '세종시', '울산광역시',
                               '인천광역시', '전라남도', '전라북도', '제주도', '충청남도', '충청북도']:
                    continue
                
                # 연령대 추출
                age_cols = [col for col in df.columns if 'C2' in col and 'NM' in col]
                if not age_cols:
                    continue
                age_group = self.convert_age_group_format(str(row[age_cols[0]]))
                if not age_group:
                    continue
                
                # 성별 추출
                itm_nm = str(row['ITM_NM'])
                gender = None
                if '남자' in itm_nm:
                    gender = '남자'
                elif '여자' in itm_nm:
                    gender = '여자'
                else:
                    continue
                
                result.append({
                    'Sido': sido,
                    'Age_Group': age_group,
                    'Gender': gender,
                    'value': value
                })
            
            elif constraint_type == 'age_income':
                # 연령 x 소득분위
                # 소득분위 데이터는 별도로 찾아야 함
                pass
        
        return pd.DataFrame(result)
