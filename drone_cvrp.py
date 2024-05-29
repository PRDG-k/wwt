import gurobipy as gp
from gurobipy import GRB

# 예제 데이터
n = 5  # 고객 수
m = 2  # 차량 수
D = 100  # 각 차량의 최대 이동 거리
c = [[0, 10, 20, 30, 40, 50],
     [10, 0, 15, 25, 35, 45],
     [20, 15, 0, 30, 20, 40],
     [30, 25, 30, 0, 15, 35],
     [40, 35, 20, 15, 0, 25],
     [50, 45, 40, 35, 25, 0]]  # 거리 행렬

# 모델 생성
model = gp.Model('CVRP')

# 변수 생성: x[i, j, k]는 차량 k가 노드 i에서 노드 j로 이동하는지 여부를 나타냅니다.
x = model.addVars(n+1, n+1, m, vtype=GRB.BINARY, name="x")

# 목적 함수: 총 비용(거리) 최소화
model.setObjective(gp.quicksum(c[i][j] * x[i, j, k] for i in range(n+1) for j in range(n+1) for k in range(m)), GRB.MINIMIZE)

# 제약 조건 1: 각 노드는 한 번만 방문
for j in range(1, n+1):
    model.addConstr(gp.quicksum(x[i, j, k] for i in range(n+1) for k in range(m) if i != j) == 1, name=f"visit_{j}")

# 제약 조건 2: 차량의 출발과 도착은 일관성 유지
for k in range(m):
    model.addConstr(gp.quicksum(x[0, j, k] for j in range(1, n+1)) == gp.quicksum(x[j, 0, k] for j in range(1, n+1)), name=f"depot_return_{k}")

# 제약 조건 3: 각 차량은 출발점에서 출발하고 돌아와야 함
for k in range(m):
    model.addConstr(gp.quicksum(x[0, j, k] for j in range(1, n+1)) <= 1, name=f"start_{k}")
    model.addConstr(gp.quicksum(x[j, 0, k] for j in range(1, n+1)) <= 1, name=f"end_{k}")

# 제약 조건 4: 하위 투어 제거 (MTZ 제약)
u = model.addVars(n+1, m, vtype=GRB.CONTINUOUS, name="u")
for k in range(m):
    for i in range(1, n+1):
        for j in range(1, n+1):
            if i != j:
                model.addConstr(u[i, k] - u[j, k] + (n+1) * x[i, j, k] <= n, name=f"subtour_{i}_{j}_{k}")

# 초기 상태 설정
for k in range(m):
    model.addConstr(u[0, k] == 0, name=f"initial_{k}")

# 제약 조건 5: 차량의 최대 이동 거리 제한
for k in range(m):
    model.addConstr(gp.quicksum(c[i][j] * x[i, j, k] for i in range(n+1) for j in range(n+1)) <= D, name=f"max_distance_{k}")

# 모델 최적화
model.optimize()

# 결과 출력
if model.status == GRB.OPTIMAL:
    solution = model.getAttr('x', x)
    for k in range(m):
        print(f"Vehicle {k}:")
        route = [0]
        next_node = 0
        while True:
            for j in range(n+1):
                if solution[next_node, j, k] > 0.5:
                    route.append(j)
                    next_node = j
                    break
            if next_node == 0:
                break
        print(" -> ".join(map(str, route)))
