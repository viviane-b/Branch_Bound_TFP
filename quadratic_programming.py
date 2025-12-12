from gurobipy import Model, GRB
import time

# dim = 1021
# P, skills = read_data()
# print(skills)
#
#
# req_skills = get_req_skills(4, 4)
# P, skills = preprocess_P(P, skills, req_skills)
# print(P)
# print(len(P), len(P[0]))
# print(skills)
# print(len(skills))
# dim = len(P)


# req_skills: set of skills required on the team
def first_model(P:list[list[float]], skills:list[list[bool]], req_skills:list[int], dim:int):
    start = time.time()

    # model
    m = Model("first")
    #m.setParam("Method", 2)
    #m.setParam("Cuts", 0)
    m.setParam("Presolve", 0)
    #m.setParam("Aggregate", 0)
    #m.setParam("Disconnected", 0)
    #m.setParam("Symmetry", 0)
    m.setParam("Heuristics", 0)

    # Create variables
    y = m.addMVar(shape=dim, vtype=GRB.BINARY, name="y")
    print(y.shape)

    # Set objective
    obj = (P@y)@y
    m.setObjective(obj)

    # Add constraint: a skill is covered

    for skill_no in req_skills:

       #  m.addConstr(skills[skill_no].values @ y >= 1 )
        m.addConstr(sum(skills[i][skill_no]*y[i] for i in range(dim)) >= 1)


    m.optimize()
    print(f"Runtime: {m.Runtime}")

    if m.status == GRB.Status.OPTIMAL:
        value_opt = m.ObjVal
        team_opt = m.getAttr("X", m.getVars())

    end = time.time()
    for v in m.getVars():
       if v.X >0:
           print(f"{v.VarName} {v.X:g}")

    print(f"Obj: {m.ObjVal:g}")

    time_QP = end-start
    return value_opt, team_opt, time_QP




# start = time.time()
# first_model(dim, req_skills)
# end = time.time()
# print(f"total time: {end - start}")

