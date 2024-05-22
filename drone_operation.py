import gurobipy as gp
from gurobipy import GRB
import random
import json

# 모델 생성
model = gp.Model("drone_operation")
seed = random.seed(42)

# 데이터/파라미터 초기화
T = 100
N = 50
u = 0
e_consumption = 10
bandwidth = 10
distance = [[random.randint(5, 9) for _ in range(N)] for _ in range(N)]
drone_capa = 100

# 변수 생성
x = model.addVars(N,N,T,vtype=GRB.BINARY, name="x")
a = model.addVars(T,vtype=GRB.BINARY, name="a")
c = model.addVars(T,vtype=GRB.BINARY, name="c")
m = model.addVars(T,vtype=GRB.BINARY, name="m")
level = model.addVars(T,vtype=GRB.CONTINUOUS, name='level')
battery = model.addVars(T,vtype=GRB.CONTINUOUS,name='battery')
charge = model.addVars(T,vtype=GRB.CONTINUOUS,name='charge')
consumption = model.addVars(T,vtype=GRB.CONTINUOUS,name='consumption')
# node = model.addVars(T,vtype=GRB.INTEGER,name='node')

# 목적 함수 설정
model.setObjective(gp.quicksum(distance[i][j] *  x[i,j,t] for i in range(N) for j in range(N) for t in range(T)), sense=GRB.MINIMIZE)

# 제약 조건 추가
for t in range(1, T):
    model.addConstr(m[t] + c[t] <= 1, 'status_constr')                  # c1

    model.addConstr(level[t] <= battery[t], 'return_constr')            # c2
    # model.addConstr(level[t] == distance[node[t]][u] * e_consumption)   # c2
    model.addConstr(level[t] == gp.quicksum(distance[i][j] * x[i,j,t] for i in range(N) for j in range(N)) * e_consumption)   # c2

    model.addConstr(charge[t] <= bandwidth * c[t])                      # c3
    model.addConstr(consumption[t] == e_consumption * m[t])             # c3

    model.addConstr(battery[t] <= battery[t-1] + charge[t] - consumption[t]) # c3
    
    model.addConstr(gp.quicksum(x[i,j,t] for i in range(N) for j in range(N)) == m[t])              # c4
    
    model.addConstr(gp.quicksum(x[i,i,t] for i in range(N)) == 0)                                # c4

    model.addConstr(c[t] <= gp.quicksum(x[i,u,t] for i in range(N)))           # c5

    model.addConstr(battery[t] <= drone_capa)

for i in range(N):
    model.addConstr(gp.quicksum(x[i,j,t] for t in range(1,T) for j in range(N)) == 1)          # c6

for j in range(N):
    model.addConstr(gp.quicksum(x[i,j,t] for t in range(1,T) for i in range(N)) == 1)          # c6

model.addConstr(battery[0] == drone_capa)

# 모델 최적화
model.optimize()

# 최적해 출력
# print("Optimal solution:")
# for v in model.getVars():
#     print(f"{v.varName} = {v.x}")

# print(f"Optimal objective value: {model.objVal}")

if model.status == GRB.OPTIMAL:
    model.write("solution.sol")
    solution = {v.varName: v.x for v in model.getVars() if v.x != 0}
    
    with open('solution.json', 'w') as file:
        json.dump(solution, file, indent=4)