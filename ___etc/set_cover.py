import numpy as np
from gurobipy import Model, GRB, quicksum

# 데이터 생성 (예제 데이터)
np.random.seed(42)
n_points = 30
n_clusters = 3
X = np.random.rand(n_points, 2)

# Gurobi 모델 생성
model = Model()

# 변수 생성
# z[i,j]는 포인트 i가 클러스터 j에 할당되는지 여부를 나타내는 이진 변수
z = model.addVars(n_points, n_clusters, vtype=GRB.BINARY)

# mu[j,k]는 클러스터 j의 중심 k (각 클러스터의 중심 좌표)
mu = model.addVars(n_clusters, 2, lb=0, ub=1, vtype=GRB.CONTINUOUS)

# 목적 함수: 포인트와 클러스터 중심 간의 거리의 제곱을 최소화
objective = quicksum(z[i,j] * ((X[i,0] - mu[j,0])**2 + (X[i,1] - mu[j,1])**2) for i in range(n_points) for j in range(n_clusters))
model.setObjective(objective, GRB.MINIMIZE)

# 제약 조건
# 각 포인트는 정확히 하나의 클러스터에 할당되어야 함
for i in range(n_points):
    model.addConstr(quicksum(z[i,j] for j in range(n_clusters)) == 1)

# 클러스터 중심 mu는 할당된 포인트의 가중 평균이어야 함
for j in range(n_clusters):
    for k in range(2):
        model.addConstr(mu[j,k] == quicksum(z[i,j] * X[i,k] for i in range(n_points)) / quicksum(z[i,j] for i in range(n_points)))

# 최적화 수행
model.optimize()

# 결과 출력
cluster_assignments = np.zeros(n_points)
cluster_centers = np.zeros((n_clusters, 2))
for i in range(n_points):
    for j in range(n_clusters):
        if z[i,j].x > 0.5:
            cluster_assignments[i] = j
for j in range(n_clusters):
    cluster_centers[j] = [mu[j,0].x, mu[j,1].x]

print("Cluster assignments:", cluster_assignments)
print("Cluster centers:", cluster_centers)

# 시각화
import matplotlib.pyplot as plt

colors = ['r', 'g', 'b']
for i in range(n_points):
    plt.scatter(X[i,0], X[i,1], color=colors[int(cluster_assignments[i])])
for j in range(n_clusters):
    plt.scatter(cluster_centers[j,0], cluster_centers[j,1], color=colors[j], marker='x', s=200)
plt.show()
