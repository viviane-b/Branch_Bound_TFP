from gurobipy import Model, GRB
from data_importer import*
import time

dim = 1021
P, skills = read_data()
print(skills)


req_skills = get_req_skills(10, 7)
P, skills = preprocess_P(P, skills, req_skills)
print(P)
print(len(P), len(P[0]))
print(skills)
print(len(skills))
dim = len(P)

# N_size: size of set of candidates
# req_skills: set of skills required on the team
def first_model(N_size, req_skills):

    # model
    m = Model("first")

    # Create variables
    y = m.addMVar(shape=N_size, vtype=GRB.BINARY, name="y")
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

    for v in m.getVars():
       if v.X >0:
           print(f"{v.VarName} {v.X:g}")

    print(f"Obj: {m.ObjVal:g}")




start = time.time()
first_model(dim, req_skills)
end = time.time()
print(f"total time: {end - start}")

