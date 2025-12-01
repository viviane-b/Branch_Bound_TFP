import numpy as np
from data_importer import *
from gurobipy import Model, GRB

dim = 1021
P, skills = read_data()
P_symmetric = P + np.transpose(P)
req_skills = get_req_skills(4, 8)

# there are N candidates

def branch_bound():
    ub = np.inf     # upper bound
    T = None        # incumbent solution

    # Create root node 0
    root = RootNode(0)

    for n in range(dim):
        zeta_opt, value_opt = solve_subproblem(n, root.get_C1(), root.get_C2())
        root.set_sub_value(value_opt, n)
        root.set_zeta(zeta_opt, n)

        ###
        # update UB and T if possible.
        ###

    solve_master_problem(root.get_sub_values(), root.get_C1(), root.get_C2())
    # why does set_sub_value not seem to work?



def solve_subproblem(n:int, C1:list[tuple[int]], C2:list[tuple[int]]):
    m = Model("subproblem")

    zeta = m.addMVar(shape=dim-1, name="zeta", vtype=GRB.BINARY)

    obj = np.sum(P_symmetric[i][n] * zeta[i] for i in range (0, n)) + np.sum(P_symmetric[i][n] * zeta[i] for i in range (n + 1, dim))
    m.setObjective(obj, GRB.MINIMIZE)

    # All skills should be covered
    for skill_no in req_skills:
        if skills[n][skill_no] == 0:    # candidate n does not possess the skill. Another member of the team has to have it
            m.addConstr(np.sum(skills[i][skill_no] * zeta[i] for i in range (0, n))
                        +np.sum(skills[i][skill_no] * zeta[i] for i in range (n+1, dim)) >= 1)

    for pair in C1:    # pair of candidates that should not be on the same team
        if n in pair:   # check only pairs that contain n
            i = pair[0] if pair[0] != n else pair[1]
            m.addConstr(zeta[i]==0)

    for pair in C2:    # pair of candidates that should be on the same team
        if n in pair:   # check only pairs that contain n
            i = pair[0] if pair[0] != n else pair[1]
            m.addConstr(zeta[i]==1)

    m.optimize()

    zeta_opt = m.getAttr("X", m.getVars())
    value_opt = m.ObjVal

    return zeta_opt, value_opt


# v: values of the subproblems. Size N
def solve_master_problem(v:list[float], C1:list[tuple[int]], C2:list[tuple[int]]):
    m = Model("master_problem")

    y = m.addMVar(shape=dim, name="y", vtype=GRB.BINARY)

    obj = np.sum(v[j]*y[j] for j in range (dim))/2
    m.setObjective(obj, GRB.MINIMIZE)

    # All skills should be covered
    for skill_no in req_skills:
        m.addConstr(np.sum(skills[j][skill_no]*y[j] for j in range(dim)) >= 1)

    for pair in C1:     # pair of candidates that should not be on the same team
        m.addConstr(y[pair[0]] + y[pair[1]] <= 1)

    for pair in C2:     # pair of candidates that should be on the same team
        m.addConstr(y[pair[0]] == 1)
        m.addConstr(y[pair[1]] == 1)

    m.optimize()

    y_opt = m.getAttr("X", m.getVars())
    val_opt = m.ObjVal

    """
    # compute z values
    z = list[list[bool]]
    z = [[None for j in range(dim)] for i in range(dim)]    #N*N matrix
    for i in range (dim):
        for j in range (dim):
            if i != j:
                z[i][j] = y[j]*zeta_j[i]

    """

    return y_opt, val_opt


class Node:

    value = float     # v'
    C1 = list[tuple[int]]
    C2 = list[tuple[int]]

    sub_values = list[float]       # v_n' for every n in N
    zetas = list[list[bool]]         # optimal ζn' for every n in N


    def __init__(self, l:int):
        self.l = l      #l: node number
        self.sub_values = [None for i in range(dim)]
        self.zetas = [None for i in range(dim)]

    def set_value(self, value:float): self.value = value

    def set_C01(self, C1: list[tuple[int]]): self.C1 = C1

    def set_C02(self, C2: list[tuple[int]]): self.C2 = C2

    def set_sub_value(self, sub_value: float, index:int): self.sub_values[index] = sub_value

    def set_zeta(self, zeta: list[bool], index:int): self.zetas[index] = zeta

    def get_value(self): return self.value

    def get_C1(self): return self.C1

    def get_C2(self): return self.C2

    def get_sub_values(self): return self.sub_values

    def get_zetas(self): return self.zetas




class RootNode(Node):

    def __init__(self, l:int):
        super().__init__(l)
        self.value = np.inf
        self.C1 = []
        self.C2 = []