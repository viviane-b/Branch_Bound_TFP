from gurobipy import Model, GRB
import time


# req_skills: set of skills required on the team
def first_model(P:list[list[float]], skills:list[list[bool]], req_skills:list[int], dim:int):
    start = time.time()

    # model
    m = Model("first")
    m.setParam("Presolve", 0)
    m.setParam("Heuristics", 0)

    # Create variables
    y = m.addMVar(shape=dim, vtype=GRB.BINARY, name="y")

    # Set objective
    obj = (P@y)@y
    m.setObjective(obj)

    # Add constraint: a skill is covered
    for skill_no in req_skills:

        m.addConstr(sum(skills[i][skill_no]*y[i] for i in range(dim)) >= 1)


    m.optimize()

    if m.status == GRB.Status.OPTIMAL:
        value_opt = m.ObjVal
        team_opt = m.getAttr("X", m.getVars())

    end = time.time()

    time_QP = end-start
    return value_opt, team_opt, time_QP


