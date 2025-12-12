import gurobipy
import numpy as np
from gurobipy import Model, GRB

class Solvers:
    dim = int
    P_symmetric = list[list[float]]
    skills = list[list[bool]]
    req_skills = list[int]
    sub_m = gurobipy.Model
    zeta = gurobipy.MVar

    master_m = gurobipy.Model
    y = gurobipy.MVar

    C1 = list[tuple[int]]
    C2 = list[tuple[int]]

    def __init__(self, dim, P_symmetric, skills, req_skills):
        self.dim = dim
        self.P_symmetric = P_symmetric
        self.skills = skills
        self.req_skills = req_skills
        self.instantiate_subproblem_model()
        self.instantiate_master_model()
        self.C1 = []
        self.C2 = []


    def set_C1(self, C1):
        self.C1 = C1
    def set_C2(self, C2):
        self.C2 = C2



    def instantiate_subproblem_model(self):
        print("instantiating subproblem model")
        self.sub_m = Model("sub_model")
        self.sub_m.setParam('OutputFlag', 0)
        self.sub_m.setParam("Heuristics", 0)
        self.sub_m.setParam("Presolve", 0)

        self.zeta = self.sub_m.addMVar(shape=self.dim, name="zeta", vtype=GRB.BINARY)

        self.sub_m.setObjective(0)

        # list of skill constraints
        self.skill_constr = {}
        for skill_no in self.req_skills:
            constr = self.sub_m.addConstr(sum(self.skills[i][skill_no] * self.zeta[i] for i in range(self.dim)) >= 1,
                                          name = f"skill_{skill_no}")
            self.skill_constr[skill_no] = constr

        self.C1_constr_sub = []
        self.C2_constr_sub = []



    def instantiate_master_model(self):
        print("instantiating master model")
        self.master_m = Model("master_model")
        self.master_m.setParam('OutputFlag', 0)
        self.master_m.setParam("Heuristics", 0)
        self.master_m.setParam("Presolve", 0)

        self.y = self.master_m.addMVar(shape=self.dim, name="y", vtype=GRB.BINARY)
        self.master_m.setObjective(0)
        for skill_no in self.req_skills:
            # TODO write constraint with LinExpr
            self.master_m.addConstr(sum(self.skills[i][skill_no] * self.y[i] for i in range(self.dim)) >= 1,
                                          name = f"skill_{skill_no}")

        self.C1_constr_master = []
        self.C2_constr_master = []



    def solve_subproblem_root(self, n:int):
        coef = np.array(self.P_symmetric)[:,n]
        self.sub_m.setObjective(gurobipy.LinExpr(coef, self.zeta.tolist()), GRB.MINIMIZE)

        # skill constraint
        for skill_no in self.req_skills:
            constr = self.skill_constr[skill_no]

            # candidate n does not possess the skill. Another member of the team has to have it
            if self.skills[n][skill_no] == 0:
                constr.RHS = 1      # constraint is active
            else:
                constr.RHS = 0      # constraint is inactive
                # TODO make sure rhs is restored after each iteration


        self.sub_m.optimize()
        # print(f"Runtime: {self.m.Runtime}")
        if self.sub_m.status == GRB.OPTIMAL:
            zeta_opt = self.sub_m.getAttr("X", self.sub_m.getVars())
            value_opt = self.sub_m.ObjVal

            #        print(f"zeta_opt = {zeta_opt}")
            #        print(f"value_opt = {value_opt})")
            return zeta_opt, value_opt

        elif self.sub_m.status == GRB.INFEASIBLE:
            print("unfeasible")
            return None, None


    def solve_subproblem_node(self,n:int,C1:list[tuple[int]], C2:list[tuple[int]]):
        print("solving subproblem node")
        self.set_C1(C1)
        self.set_C2(C2)

        coef = np.array(self.P_symmetric)[:, n]
        self.sub_m.setObjective(gurobipy.LinExpr(coef, self.zeta.tolist()), GRB.MINIMIZE)

        # skill constraint
        for skill_no in self.req_skills:
            constr = self.skill_constr[skill_no]

            # candidate n does not possess the skill. Another member of the team has to have it
            if self.skills[n][skill_no] == 0:
                constr.RHS = 1  # constraint is active
            else:
                constr.RHS = 0  # constraint is inactive

        # C1, C2 constraints

        # remove old constraints
        for c in self.C1_constr_sub:
            self.sub_m.remove(c)
        for c in self.C2_constr_sub:
            self.sub_m.remove(c)
        self.sub_m.update()
        self.C1_constr_sub = []
        self.C2_constr_sub = []

        # add new constraints
        for (i, j) in C1:
            if i == n:
                con = self.sub_m.addConstr(self.zeta[j] == 0)
            elif j == n:
                con = self.sub_m.addConstr(self.zeta[i] == 0)
            else:
                continue
            self.C1_constr_sub.append(con)

        for (i, j) in C2:
            if i == n:
                con = self.sub_m.addConstr(self.zeta[j] == 1)
            elif j == n:
                con = self.sub_m.addConstr(self.zeta[i] == 1)
            else:
                continue
            self.C2_constr_sub.append(con)


        self.sub_m.optimize()
        # print(f"Runtime: {self.m.Runtime}")
        if self.sub_m.status == GRB.OPTIMAL:
            zeta_opt = self.sub_m.getAttr("X", self.sub_m.getVars())
            value_opt = self.sub_m.ObjVal

            #        print(f"zeta_opt = {zeta_opt}")
            #        print(f"value_opt = {value_opt})")
            return zeta_opt, value_opt

        elif self.sub_m.status == GRB.INFEASIBLE:
            print("unfeasible")
            return None, None


    def solve_master(self, v:list[float], C1:list[tuple[int]], C2:list[tuple[int]] ):
        self.set_C1(C1)
        self.set_C2(C2)
        print("solving master")

        self.master_m.setObjective((gurobipy.LinExpr(v, self.y.tolist()))/2, GRB.MINIMIZE)

        # remove old constraints
        for c in self.C1_constr_master:
            self.master_m.remove(c)
        for c in self.C2_constr_master:
            self.master_m.remove(c)
        self.master_m.update()
        self.C1_constr_master = []
        self.C2_constr_master = []

        # add new constraints
        for (i,j) in C1:
            con = self.master_m.addConstr(self.y[i]+self.y[j] <=1)
            self.C1_constr_master.append(con)

        for (i,j) in C2:
            con1 = self.master_m.addConstr(self.y[i]==1)
            con2 = self.master_m.addConstr(self.y[j]==1)
            self.C1_constr_master.append(con1)
            self.C2_constr_master.append(con2)

        self.master_m.optimize()

        if self.master_m.status == GRB.OPTIMAL:

            y_opt = self.master_m.getAttr("X", self.master_m.getVars())
            val_opt = self.master_m.ObjVal


            return y_opt, val_opt

        elif self.master_m.status == GRB.INFEASIBLE:
            print("unfeasible")
            return None, None


    # to delete after
def solve_subproblem(n:int, C1:list[tuple[int]], C2:list[tuple[int]], dim:int, P_symmetric:list[list[float]], skills:list[list[bool]], req_skills:list[int]):
#    print("\n ---- solving subproblem n=", n)
    m = Model("subproblem")

    zeta = m.addMVar(shape=dim, name="zeta", vtype=GRB.BINARY)

    obj = sum(P_symmetric[i][n] * zeta[i] for i in range (0, n)) + sum(P_symmetric[i][n] * zeta[i] for i in range (n + 1, dim))
    m.setObjective(obj, GRB.MINIMIZE)

    # All skills should be covered
    for skill_no in req_skills:
        if skills[n][skill_no] == 0:    # candidate n does not possess the skill. Another member of the team has to have it
            m.addConstr(sum(skills[i][skill_no] * zeta[i] for i in range (0, n))
                        +sum(skills[i][skill_no] * zeta[i] for i in range (n+1, dim)) >= 1)

    for pair in C1:    # pair of candidates that should not be on the same team
        if n in pair:   # check only pairs that contain n       # TODO: maybe some optimization on the loop?
            i = pair[0] if pair[0] != n else pair[1]
            m.addConstr(zeta[i]==0)

    for pair in C2:    # pair of candidates that should be on the same team
        if n in pair:   # check only pairs that contain n
            i = pair[0] if pair[0] != n else pair[1]
            m.addConstr(zeta[i]==1)

    m.setParam('OutputFlag', 0)
    m.optimize()
    print(m.getA())
    print(f"Runtime: {m.Runtime}")
    if m.status == GRB.OPTIMAL:
        zeta_opt = m.getAttr("X", m.getVars())
        value_opt = m.ObjVal


#        print(f"zeta_opt = {zeta_opt}")
#        print(f"value_opt = {value_opt})")
        return zeta_opt, value_opt

    elif m.status == GRB.INFEASIBLE:
        print("unfeasible")
        return None, None

    # TODO what if status is FEASIBLE  or other?


# v: values of the subproblems. Size N
def solve_master_problem(v:list[float], C1:list[tuple[int]], C2:list[tuple[int]], dim:int, skills:list[list[bool]], req_skills:list[int]):
#    print("\n ----- solving master problem")

    m = Model("master_problem")

    y = m.addMVar(shape=dim, name="y", vtype=GRB.BINARY)

    obj = sum(v[j]*y[j] for j in range (dim))/2
    m.setObjective(obj, GRB.MINIMIZE)

    # All skills should be covered
    for skill_no in req_skills:
        m.addConstr(sum(skills[j][skill_no]*y[j] for j in range(dim)) >= 1)

    for pair in C1:     # pair of candidates that should not be on the same team
        m.addConstr(y[pair[0]] + y[pair[1]] <= 1)

    for pair in C2:     # pair of candidates that should be on the same team
        m.addConstr(y[pair[0]] == 1)
        m.addConstr(y[pair[1]] == 1)

    m.setParam('OutputFlag', 0)
    m.optimize()
    print(f"Runtime: {m.Runtime}")

    if m.status == GRB.OPTIMAL:

        y_opt = m.getAttr("X", m.getVars())
        val_opt = m.ObjVal

#        print(f"subproblem y_opt = {y_opt}")
#        print(f"subproblem val_opt = {val_opt}")

        return y_opt, val_opt

    elif m.status == GRB.INFEASIBLE:
#        print("unfeasible")
        return None, None


