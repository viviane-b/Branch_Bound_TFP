from gurobipy import Model, GRB
from data_importer import*


dim = 1021
P, skills = read_data()
print(skills)


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

        m.addConstr(skills[skill_no].values @ y >= 1 )


    m.optimize()

    for v in m.getVars():
       if v.X >0:
           print(f"{v.VarName} {v.X:g}")

    print(f"Obj: {m.ObjVal:g}")


first_model(dim, get_req_skills(4, 8))

print(skills.loc[[30]])

