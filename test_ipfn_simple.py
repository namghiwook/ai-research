"""
ipfn 라이브러리 간단한 테스트
"""
import pandas as pd
import numpy as np
from ipfn import ipfn

# 간단한 예제로 ipfn 테스트
print("=" * 60)
print("ipfn 라이브러리 간단한 테스트")
print("=" * 60)

# Base table 생성 (간단한 예제)
base = pd.DataFrame({
    'A': ['a1', 'a1', 'a2', 'a2'] * 2,
    'B': ['b1', 'b2', 'b1', 'b2'] * 2,
    'C': ['c1'] * 4 + ['c2'] * 4,
    'total': [1.0] * 8
})

print("\nBase Table:")
print(base)
print(f"Base Table 총합: {base['total'].sum()}")

# 제약 조건 1: A x B
agg1 = pd.DataFrame({
    'A': ['a1', 'a1', 'a2', 'a2'],
    'B': ['b1', 'b2', 'b1', 'b2'],
    'total': [0.4, 0.3, 0.2, 0.1]
})

print("\n제약 조건 1 (A x B):")
print(agg1)
print(f"제약 조건 1 총합: {agg1['total'].sum()}")

# 제약 조건 2: B x C
agg2 = pd.DataFrame({
    'B': ['b1', 'b1', 'b2', 'b2'],
    'C': ['c1', 'c2', 'c1', 'c2'],
    'total': [0.5, 0.3, 0.15, 0.05]
})

print("\n제약 조건 2 (B x C):")
print(agg2)
print(f"제약 조건 2 총합: {agg2['total'].sum()}")

# IPF 실행
print("\nIPF 실행 중...")
aggregates = [agg1, agg2]
dimensions = [['A', 'B'], ['B', 'C']]

ipf = ipfn.ipfn(
    original=base,
    aggregates=aggregates,
    dimensions=dimensions,
    weight_col='total',
    convergence_rate=1e-6,
    max_iteration=50,
    verbose=1
)

result = ipf.iteration()

print("\n결과:")
print(result)
print(f"\n결과 총합: {result['total'].sum()}")
