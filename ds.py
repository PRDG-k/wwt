import gurobipy as gp
from gurobipy import GRB
import random
import matplotlib.pyplot as plt

# random 모듈 시드 설정
random.seed(42)

# 모델 생성
model = gp.Model("pesticide_application")

# 데이터/파라미터 초기화
N = 612  # 그리드의 가로 크기
M = 511  # 그리드의 세로 크기
J = range(N * M)  # 전체 그리드 픽셀 집합
I = random.sample(J, 50)  # 농약 살포가 필요한 픽셀 집합 (랜덤으로 1000개의 픽셀 선택)
large_constant = 10000  # 충분히 큰 상수
z_values = {j: random.randint(1, 3) for j in J}  # 각 픽셀의 z 좌표 (범위 제한: 1-3)

def a(z):
    return z  # z 좌표에 따른 농약 살포 범위 (예시 함수)

# 변수 생성
S = model.addVars(J, vtype=GRB.BINARY, name="S")  # 살포 지점 j가 선택되었는지를 나타내는 이진 변수
C = model.addVars(I, J, vtype=GRB.BINARY, name="C")  # 지점 j에 의해서 지점 i가 커버될 수 있는지를 나타내는 이진 변수

# 목적 함수 설정: 최소한의 살포 지점 선택
model.setObjective(gp.quicksum(S[j] for j in J), sense=GRB.MINIMIZE)

# 제약 조건 추가
for i in I:
    xi, yi = divmod(i, N)  # i 픽셀의 (x, y) 좌표
    for j in J:
        xj, yj = divmod(j, N)  # j 픽셀의 (x, y) 좌표
        zj = z_values[j]  # j 픽셀의 z 좌표
        aj = a(zj)  # z 좌표에 따른 농약 살포 범위

        # i 픽셀이 j 픽셀에 의해 커버될 수 있는지에 대한 제약 조건
        model.addConstr(xj - aj <= xi + large_constant * (1 - C[i, j]))
        model.addConstr(xi <= xj + aj + large_constant * (1 - C[i, j]))
        model.addConstr(yj - aj <= yi + large_constant * (1 - C[i, j]))
        model.addConstr(yi <= yj + aj + large_constant * (1 - C[i, j]))
        model.addConstr(S[j] >= C[i, j])

# 모든 i가 적어도 하나의 j에 의해 커버되어야 한다는 제약 조건
for i in I:
    model.addConstr(gp.quicksum(C[i, j] for j in J) >= 1)

# 모델 최적화
model.optimize()

# 최적해 출력 및 시각화 준비
if model.status == GRB.OPTIMAL:
    solution = {v.varName: v.x for v in model.getVars() if v.x != 0}
    print("Solution:")
    print(solution)

    # 시각화 코드
    fig, ax = plt.subplots(figsize=(12, 10))

    # 전체 그리드 픽셀
    for j in J:
        xj, yj = divmod(j, N)
        ax.scatter(xj, yj, color='lightgrey', marker='s', s=10)

    # 농약 살포가 필요한 픽셀
    for i in I:
        xi, yi = divmod(i, N)
        ax.scatter(xi, yi, color='red', marker='s', s=10)

    # 선택된 살포 지점 및 커버 범위
    for j in J:
        if S[j].x > 0.5:
            xj, yj = divmod(j, N)
            zj = z_values[j]
            aj = a(zj)
            rect = plt.Rectangle((xj - aj, yj - aj), 2 * aj, 2 * aj, color='blue', fill=False, linestyle='dotted')
            ax.add_artist(rect)
            ax.scatter(xj, yj, color='blue', marker='o', s=10)

    plt.xlim(-1, N)
    plt.ylim(-1, M)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(True)
    plt.title('Pesticide Application Optimization with Varying Z Range')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.show()
else:
    print("No optimal solution found.")