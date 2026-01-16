"""
추가 통계표 수집 및 IPF 재실행
"""
import json
import pandas as pd
import numpy as np
from kosis_data_collector_plan import KOSISPlanDataCollector
from ipf_processor_plan import IPFProcessorPlan
import pickle
from typing import Dict, List
import time

API_KEY = "ZDcwZjllMDU5NTYwOTlhMjkyYTRmNjFjZDhiMmFlMGY="
YEAR = "2020"

def load_additional_urls():
    """
    kosis_statistics_2020plus.json에서 추가 통계표 URL 로드
    """
    print("=" * 80)
    print("추가 통계표 URL 로드")
    print("=" * 80)
    
    with open('kosis_statistics_2020plus.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 우선순위 카테고리별로 정리
    priority_stats = []
    
    # 소득분위 (가장 중요)
    if '소득분위' in data['categories']:
        for stat in data['categories']['소득분위']:
            priority_stats.append({
                'category': '소득분위',
                'tblId': stat['tblId'],
                'title': stat['title'],
                'url': stat['url'],
                'priority': 1
            })
    
    # 직업/산업
    if '직업_산업' in data['categories']:
        for stat in data['categories']['직업_산업']:
            priority_stats.append({
                'category': '직업_산업',
                'tblId': stat['tblId'],
                'title': stat['title'],
                'url': stat['url'],
                'priority': 2
            })
    
    # 교육정도
    if '교육정도' in data['categories']:
        for stat in data['categories']['교육정도']:
            priority_stats.append({
                'category': '교육정도',
                'tblId': stat['tblId'],
                'title': stat['title'],
                'url': stat['url'],
                'priority': 3
            })
    
    print(f"\n총 {len(priority_stats)}개의 우선순위 통계표 발견")
    print(f"  - 소득분위: {sum(1 for s in priority_stats if s['category'] == '소득분위')}개")
    print(f"  - 직업/산업: {sum(1 for s in priority_stats if s['category'] == '직업_산업')}개")
    print(f"  - 교육정도: {sum(1 for s in priority_stats if s['category'] == '교육정도')}개")
    
    return priority_stats

def collect_additional_data(collector: KOSISPlanDataCollector, priority_stats: List[Dict]):
    """
    추가 통계표 데이터 수집
    """
    print("\n" + "=" * 80)
    print("추가 통계표 데이터 수집")
    print("=" * 80)
    
    collected_count = 0
    failed_count = 0
    
    for i, stat in enumerate(priority_stats, 1):
        print(f"\n[{i}/{len(priority_stats)}] {stat['category']}: {stat['title']} ({stat['tblId']})")
        
        try:
            df = collector.fetch_from_url(stat['url'], f"{stat['category']}_{stat['tblId']}")
            
            if not df.empty:
                # 데이터 클리닝
                df_cleaned = collector.clean_data(df)
                
                if not df_cleaned.empty:
                    collected_count += 1
                    print(f"  ✓ 수집 성공: {len(df_cleaned)}행")
                else:
                    failed_count += 1
                    print(f"  ✗ 클리닝 후 데이터 없음")
            else:
                failed_count += 1
                print(f"  ✗ 데이터 수집 실패")
                
        except Exception as e:
            failed_count += 1
            print(f"  ✗ 오류: {str(e)}")
        
        # API 호출 간격
        time.sleep(0.5)
    
    print(f"\n수집 완료: 성공 {collected_count}개, 실패 {failed_count}개")
    return collector.all_data

def main():
    """
    메인 함수
    """
    print("=" * 80)
    print("추가 통계표 수집 및 IPF 재실행")
    print("=" * 80)
    
    # 1. 추가 통계표 URL 로드
    priority_stats = load_additional_urls()
    
    # 2. 기존 데이터 수집 (plan.md의 기본 URL들)
    print("\n" + "=" * 80)
    print("기존 통계표 데이터 수집 (plan.md)")
    print("=" * 80)
    
    collector = KOSISPlanDataCollector(API_KEY)
    existing_data = collector.collect_all_data()
    print(f"\n기존 데이터 수집 완료: {len(existing_data)}개")
    
    # 3. 추가 통계표 데이터 수집
    additional_data = collect_additional_data(collector, priority_stats)
    
    # 4. 모든 데이터 통합
    all_data = {**existing_data, **additional_data}
    print(f"\n전체 데이터: {len(all_data)}개")
    
    # 5. 고유값 추출
    print("\n" + "=" * 80)
    print("고유값 추출")
    print("=" * 80)
    
    all_dimensions = collector.extract_dimensions_from_data(all_data)
    
    print("\n추출된 고유값:")
    for dim_name, values in all_dimensions.items():
        if values:
            # set을 list로 변환
            if isinstance(values, set):
                values = sorted(list(values))
            print(f"  {dim_name}: {len(values)}개")
            if len(values) <= 20:
                print(f"    {values}")
            else:
                print(f"    {values[:10]} ... (총 {len(values)}개)")
    
    # 6. Base Table 생성
    print("\n" + "=" * 80)
    print("Base Table 생성")
    print("=" * 80)
    
    processor = IPFProcessorPlan()
    
    # set을 list로 변환
    sidos = sorted(list(all_dimensions.get('Sido', set())))
    age_groups = sorted(list(all_dimensions.get('Age_Group', set())))
    genders = sorted(list(all_dimensions.get('Gender', set())))
    income_quintiles = sorted(list(all_dimensions.get('Income_Quintile', set())))
    
    # 소득분위가 없으면 기본값 사용
    if not income_quintiles:
        print("⚠ 소득분위 데이터 없음. 기본값(10분위) 사용")
        income_quintiles = [f"{i}분위" for i in range(1, 11)]
        all_dimensions['Income_Quintile'] = income_quintiles
    
    print(f"\n차원 크기:")
    print(f"  Sido: {len(sidos)}개")
    print(f"  Age_Group: {len(age_groups)}개")
    print(f"  Gender: {len(genders)}개")
    print(f"  Income_Quintile: {len(income_quintiles)}개")
    print(f"  총 조합: {len(sidos) * len(age_groups) * len(genders) * len(income_quintiles):,}개")
    
    base_df = processor.create_base_table(sidos, age_groups, genders, income_quintiles)
    print(f"\nBase Table 생성 완료: {len(base_df):,}행")
    
    # 7. 제약 조건 준비
    print("\n" + "=" * 80)
    print("제약 조건 준비")
    print("=" * 80)
    
    aggregates, dimensions = processor.prepare_constraints(all_data, collector)
    print(f"\n제약 조건: {len(aggregates)}개")
    for i, (agg, dim) in enumerate(zip(aggregates, dimensions), 1):
        print(f"  {i}. {dim}: {len(agg)}행")
    
    # 8. IPF 실행
    print("\n" + "=" * 80)
    print("IPF 실행")
    print("=" * 80)
    
    result_df = processor.run_ipf(base_df, aggregates, dimensions)
    
    print(f"\nIPF 완료: {len(result_df):,}행")
    print(f"가중치 합: {result_df['Weight'].sum():.6f}")
    
    # 9. 결과 저장
    print("\n" + "=" * 80)
    print("결과 저장")
    print("=" * 80)
    
    result_df.to_csv('final_joint_distribution.csv', index=False, encoding='utf-8-sig')
    print("✓ CSV 저장 완료: final_joint_distribution.csv")
    
    with open('final_joint_distribution.pkl', 'wb') as f:
        pickle.dump(result_df, f)
    print("✓ Pickle 저장 완료: final_joint_distribution.pkl")
    
    # 10. 요약 통계
    print("\n" + "=" * 80)
    print("최종 결과 요약")
    print("=" * 80)
    
    print(f"\n고유값:")
    print(f"  Sido: {len(result_df['Sido'].unique())}개")
    print(f"  Age_Group: {len(result_df['Age_Group'].unique())}개")
    print(f"  Gender: {len(result_df['Gender'].unique())}개")
    print(f"  Income_Quintile: {len(result_df['Income_Quintile'].unique())}개")
    
    print(f"\n가중치 통계:")
    print(f"  최소: {result_df['Weight'].min():.8f}")
    print(f"  최대: {result_df['Weight'].max():.8f}")
    print(f"  평균: {result_df['Weight'].mean():.8f}")
    print(f"  합계: {result_df['Weight'].sum():.6f}")
    
    print("\n" + "=" * 80)
    print("완료!")
    print("=" * 80)

if __name__ == "__main__":
    main()
