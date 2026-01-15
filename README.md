# KOSIS 데이터 기반 IPF 가상 인구 프로필 생성

대한민국 성인 인구 약 4,000만 명을 대표하는 가상 인구 프로필(Synthetic Population)을 생성하기 위한 프로젝트입니다.

## 프로젝트 개요

파편화된 KOSIS 통계 데이터들을 통합하여 **[지역 x 연령 x 성별 x 소득분위]**의 고차원 결합 확률 분포 테이블을 생성합니다.

## 주요 기능

1. **KOSIS OpenAPI 데이터 수집**
   - Base 데이터: 연령 및 성별 인구 - 읍면동
   - 제약 조건 1: 성, 연령 및 혼인상태별 인구 - 시군구
   - 제약 조건 2: 소득 10분위별 가구/인구 분포

2. **데이터 클리닝**
   - 합계 행 제거 ('계', '소계')
   - 행정구역 필터링 ('전국', '동부', '읍부', '면부' 제외)

3. **IPF (Iterative Proportional Fitting) 알고리즘**
   - Base Table 구축 (Cartesian Product)
   - 제약 조건 정규화
   - 반복 계산을 통한 확률 분포 생성

## 설치 방법

```bash
pip install -r requirements.txt
```

## 사용 방법

```bash
python main.py
```

## 프로젝트 구조

```
.
├── doc/
│   └── plan.md                    # 프로젝트 계획서
├── kosis_data_collector.py        # KOSIS API 데이터 수집 모듈
├── ipf_processor.py               # IPF 알고리즘 처리 모듈
├── main.py                        # 메인 실행 스크립트
├── requirements.txt               # 필요한 라이브러리
└── README.md                      # 프로젝트 설명서
```

## 출력 파일

- `final_joint_distribution.csv`: 최종 결합 확률 분포 테이블 (CSV 형식)
- `final_joint_distribution.pkl`: 최종 결합 확률 분포 테이블 (Pickle 형식)

## 출력 컬럼

- `Sido`: 시도
- `Sigungu`: 시군구
- `Age_Group`: 연령대
- `Gender`: 성별
- `Income_Quintile`: 소득분위
- `Weight`: 확률 가중치

## 참고사항

- KOSIS API의 실제 통계표ID와 데이터 구조는 KOSIS 웹사이트에서 확인이 필요합니다.
- 데이터 수집 후 실제 데이터 구조에 맞게 컬럼명과 데이터 처리 로직을 조정해야 할 수 있습니다.
