"""
KOSIS OpenAPI를 사용한 데이터 수집 모듈
"""
import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import json

class KOSISDataCollector:
    def __init__(self, api_key: str):
        """
        KOSIS 데이터 수집기 초기화
        
        Args:
            api_key: KOSIS OpenAPI 키
        """
        self.api_key = api_key
        self.base_url = "https://kosis.kr/openapi/statisticsData.do"
        self.param_url = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
        
    def search_statistics(self, keyword: str = "", org_id: str = "101") -> pd.DataFrame:
        """
        KOSIS에서 통계표를 검색합니다.
        
        Args:
            keyword: 검색 키워드
            org_id: 기관ID (101=통계청)
            
        Returns:
            DataFrame: 검색된 통계표 목록
        """
        search_url = "https://kosis.kr/openapi/statisticsList.do"
        params = {
            "method": "getList",
            "apiKey": self.api_key,
            "format": "json",
            "jsonVD": "Y",
            "orgId": org_id,
            "keyword": keyword
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict) and 'list' in data:
                return pd.DataFrame(data['list'])
            else:
                return pd.DataFrame()
        except Exception as e:
            print(f"  통계표 검색 오류: {str(e)}")
            return pd.DataFrame()
    
    def fetch_data(self, 
                   org_id: str,
                   tbl_id: str,
                   item_code1: Optional[str] = None,
                   item_code2: Optional[str] = None,
                   item_code3: Optional[str] = None,
                   item_code4: Optional[str] = None,
                   itm_id: Optional[str] = None,
                   obj_id: Optional[str] = None,
                   prd_de: Optional[str] = None,
                   load_gubun: str = "Json",
                   user_stats_id: Optional[str] = None,
                   **kwargs) -> pd.DataFrame:
        """
        KOSIS API에서 데이터를 조회합니다.
        
        Args:
            org_id: 기관ID
            tbl_id: 통계표ID
            item_code1-4: 항목 코드
            itm_id: 항목ID
            obj_id: 대상ID
            prd_de: 조회 기간 (예: "2020", "2021")
            load_gubun: 로드 구분 (Json, StatisticSearch 등)
            user_stats_id: 사용자 통계ID (필요시)
            **kwargs: 추가 파라미터
            
        Returns:
            DataFrame: 조회된 데이터
        """
        # 먼저 통계표 정보를 조회하여 userStatsId를 가져옴
        if not user_stats_id:
            stats_list = self.search_statistics(keyword=tbl_id, org_id=org_id)
            if not stats_list.empty and 'USER_STATS_ID' in stats_list.columns:
                matching = stats_list[stats_list['TBL_ID'] == tbl_id]
                if not matching.empty:
                    user_stats_id = matching.iloc[0]['USER_STATS_ID']
        
        params = {
            "method": "getList",
            "apiKey": self.api_key,
            "format": "json",
            "jsonVD": "Y",
            "orgId": org_id,
            "tblId": tbl_id,
            "loadGubun": load_gubun,
        }
        
        # userStatsId가 있으면 추가
        if user_stats_id:
            params["userStatsId"] = user_stats_id
        
        # 기간 파라미터 설정
        if prd_de:
            params["prdSe"] = "Y"  # 연도 단위
            params["startPrdDe"] = prd_de
            params["endPrdDe"] = prd_de
        
        # 항목 코드들 추가 (값이 있을 때만)
        if item_code1:
            params["itemCode1"] = item_code1
        if item_code2:
            params["itemCode2"] = item_code2
        if item_code3:
            params["itemCode3"] = item_code3
        if item_code4:
            params["itemCode4"] = item_code4
        if itm_id:
            params["itmId"] = itm_id
        if obj_id:
            params["objId"] = obj_id
            
        params.update(kwargs)
        
        try:
            print(f"  API 호출 URL: {self.base_url}")
            print(f"  파라미터: {params.get('orgId')}, {params.get('tblId')}, {params.get('startPrdDe')}")
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # 응답 데이터 확인
            try:
                data = response.json()
            except json.JSONDecodeError:
                print(f"  오류: JSON 파싱 실패. 응답 내용: {response.text[:500]}")
                return pd.DataFrame()
            
            # KOSIS API 응답 구조에 따라 처리
            if isinstance(data, dict):
                if 'StatisticSearch' in data:
                    # StatisticSearch 형식
                    items = data['StatisticSearch'].get('row', [])
                    if items:
                        df = pd.DataFrame(items)
                        return df
                elif 'RESULT' in data:
                    # 오류 응답
                    print(f"  오류: {data.get('RESULT', {}).get('CODE', '알 수 없음')}")
                    print(f"  메시지: {data.get('RESULT', {}).get('MESSAGE', '')}")
                    return pd.DataFrame()
                else:
                    # 기타 딕셔너리 응답
                    df = pd.DataFrame([data])
                    return df
            elif isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
                return df
            else:
                print(f"  경고: {tbl_id}에 대한 데이터가 없습니다. (응답 타입: {type(data)})")
                if isinstance(data, dict):
                    print(f"  응답 키: {list(data.keys())}")
                return pd.DataFrame()
                
        except requests.exceptions.RequestException as e:
            print(f"  오류 발생 ({tbl_id}): {str(e)}")
            return pd.DataFrame()
        except Exception as e:
            print(f"  예상치 못한 오류 ({tbl_id}): {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def clean_data(self, df: pd.DataFrame, 
                   exclude_values: List[str] = None) -> pd.DataFrame:
        """
        데이터 클리닝: 합계 행 및 불필요한 행정구역 제거
        
        Args:
            df: 원본 데이터프레임
            exclude_values: 제외할 값들의 리스트
            
        Returns:
            DataFrame: 정제된 데이터
        """
        if df.empty:
            return df
            
        df_cleaned = df.copy()
        
        # 기본 제외 값들
        default_exclude = ['계', '소계', '전국', '동부', '읍부', '면부']
        if exclude_values:
            default_exclude.extend(exclude_values)
        
        # 모든 컬럼에서 제외 값 제거
        for col in df_cleaned.columns:
            if df_cleaned[col].dtype == 'object':
                df_cleaned = df_cleaned[~df_cleaned[col].isin(default_exclude)]
        
        return df_cleaned.reset_index(drop=True)
    
    def fetch_data_with_params(self,
                                tbl_id: str,
                                itm_id: str,
                                obj_l1: str,
                                obj_l2: str,
                                obj_l3: str = "",
                                obj_l4: str = "",
                                obj_l5: str = "",
                                obj_l6: str = "",
                                obj_l7: str = "",
                                obj_l8: str = "",
                                prd_se: str = "F",
                                new_est_prd_cnt: int = 3,
                                org_id: str = "101",
                                **kwargs) -> pd.DataFrame:
        """
        KOSIS Parameter API를 사용하여 데이터 조회
        
        Args:
            tbl_id: 통계표ID
            itm_id: 항목ID (공백으로 구분된 여러 값)
            obj_l1: 객체 레벨1 (공백으로 구분된 여러 값)
            obj_l2: 객체 레벨2 (공백으로 구분된 여러 값)
            obj_l3-8: 객체 레벨3-8
            prd_se: 기간 구분 (F=최신, A=연간 등)
            new_est_prd_cnt: 최신 추정 기간 수
            org_id: 기관ID
            **kwargs: 추가 파라미터
            
        Returns:
            DataFrame: 조회된 데이터
        """
        params = {
            "method": "getList",
            "apiKey": self.api_key,
            "format": "json",
            "jsonVD": "Y",
            "orgId": org_id,
            "tblId": tbl_id,
            "itmId": itm_id,
            "objL1": obj_l1,
            "objL2": obj_l2,
            "objL3": obj_l3,
            "objL4": obj_l4,
            "objL5": obj_l5,
            "objL6": obj_l6,
            "objL7": obj_l7,
            "objL8": obj_l8,
            "prdSe": prd_se,
            "newEstPrdCnt": new_est_prd_cnt
        }
        params.update(kwargs)
        
        try:
            print(f"  API 호출 URL: {self.param_url}")
            print(f"  통계표ID: {tbl_id}")
            
            response = requests.get(self.param_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
                print(f"  데이터 수집 완료: {len(df)}행")
                return df
            else:
                print(f"  경고: 데이터가 없습니다.")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"  오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def fetch_base_population_data(self, year: str = "2023") -> pd.DataFrame:
        """
        Base 데이터: 연령 및 성별 인구 - 읍면동 (DT_1IN1503)
        
        Args:
            year: 조회 연도
            
        Returns:
            DataFrame: 지역, 연령, 성별별 인구 데이터
        """
        print(f"Base 데이터 수집 중 (연도: {year})...")
        
        # 실제 통계표ID는 KOSIS에서 확인 필요
        # 여기서는 예시로 일반적인 구조를 사용
        df = self.fetch_data(
            org_id="101",  # 통계청
            tbl_id="DT_1IN1503",
            prd_de=year
        )
        
        if not df.empty:
            df = self.clean_data(df)
            print(f"Base 데이터 수집 완료: {len(df)}행")
        
        return df
    
    def fetch_constraint1_data(self, year: str = "2023") -> pd.DataFrame:
        """
        제약 조건 1: 성, 연령 및 혼인상태별 인구 - 시군구 (DT_1PM2002)
        실제 KOSIS API 형식 사용
        
        Args:
            year: 조회 연도
            
        Returns:
            DataFrame: 시군구, 성별, 연령, 혼인상태별 인구 데이터
        """
        print(f"제약 조건 1 데이터 수집 중 (연도: {year})...")
        
        # 실제 KOSIS Parameter API 사용
        # 제공된 URL의 파라미터 구조 사용
        df = self.fetch_data_with_params(
            tbl_id="DT_1PM2002",
            itm_id="T10+T11+T12+T13+T14+T20+T21+T22+T23+T24+T30+T31+T32+T33+T34+",
            obj_l1="00+03+04+05+11+21+22+23+24+25+26+29+31+32+33+34+35+36+37+38+39+",
            obj_l2="000+020+025+030+035+040+045+050+055+060+065+070+075+080+085+086+",
            prd_se="F",
            new_est_prd_cnt=3,
            org_id="101"
        )
        
        if not df.empty:
            # KOSIS 데이터 형식을 IPF에 필요한 형식으로 변환
            df = self.convert_constraint1_format(df)
            df = self.clean_data(df)
            print(f"제약 조건 1 데이터 수집 완료: {len(df)}행")
        else:
            # 기존 방식으로 fallback
            print("  Parameter API 실패, 기존 방식 시도...")
            df = self.fetch_data(
                org_id="101",
                tbl_id="DT_1MR2060",
                prd_de=year
            )
            if not df.empty:
                df = self.clean_data(df)
                print(f"제약 조건 1 데이터 수집 완료: {len(df)}행")
        
        return df
    
    def convert_constraint1_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        KOSIS API 데이터를 제약 조건 1 형식으로 변환
        입력: C1_NM(시도), C2_NM(연령대), ITM_NM(항목), DT(값)
        출력: Sido, Sigungu, Age_Group, Gender, value
        """
        result = []
        
        # '전국' 제외
        df = df[df['C1_NM'] != '전국'].copy()
        # '합계' 연령대 제외
        df = df[df['C2_NM'] != '합계'].copy()
        
        for _, row in df.iterrows():
            sido = row['C1_NM']
            age_group = row['C2_NM']
            itm_nm = row['ITM_NM']
            
            # DT 값 처리 (- 또는 빈 값 제외)
            dt_value = row['DT']
            try:
                value = int(dt_value) if str(dt_value) not in ['-', '', 'nan'] else 0
            except (ValueError, TypeError):
                value = 0
            
            if value == 0:
                continue
            
            # 항목명에서 성별 추출
            gender = None
            if '남자' in itm_nm:
                gender = '남자'
            elif '여자' in itm_nm:
                gender = '여자'
            elif '내국인' in itm_nm:
                # 전체 데이터이므로 성별 구분 없음 - 건너뛰기
                continue
            
            # 연령대 형식 변환 (예: "15~19세" -> "15-19", "85세이상" -> "85+")
            age_group_clean = age_group.replace('~', '-').replace('세', '').replace('이상', '+')
            if '85' in age_group_clean and '+' not in age_group_clean:
                age_group_clean = '85+'
            
            if gender:
                result.append({
                    'Sido': sido,
                    'Sigungu': sido,  # 시군구 정보가 없으면 시도 사용
                    'Age_Group': age_group_clean,
                    'Gender': gender,
                    'value': value
                })
        
        return pd.DataFrame(result)
    
    def fetch_constraint2_data(self, year: str = "2023") -> pd.DataFrame:
        """
        제약 조건 2: 소득 10분위별 가구/인구 분포
        
        Args:
            year: 조회 연도
            
        Returns:
            DataFrame: 연령대별 소득분위 비율 데이터
        """
        print(f"제약 조건 2 데이터 수집 중 (연도: {year})...")
        
        # 소득 분위별 데이터는 여러 통계표에서 수집 가능
        # 예: 가구소득 및 소비지출 통계 등
        # 실제 통계표ID는 KOSIS에서 확인 필요
        df = self.fetch_data(
            org_id="101",
            tbl_id="DT_1ST0628",  # 예시 - 실제 ID 확인 필요
            prd_de=year
        )
        
        if not df.empty:
            df = self.clean_data(df)
            print(f"제약 조건 2 데이터 수집 완료: {len(df)}행")
        
        return df
