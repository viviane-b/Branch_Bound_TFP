# a
import numpy as np
from fontTools.misc.cython import returns
from gurobipy import Model, GRB
import pandas as pd
import scipy
from numpy.ma.core import shape


## Quadratic programming example
def test():

    # model
    m = Model("qp")

    # Create variables
    x = m.addVar(ub=1.0, name="x")
    y = m.addVar(ub=1.0, name="y")
    z = m.addVar(ub=1.0, name="z")

    # Set objective: x^2 + x*y + y^2 + y*z + z^2 + 2 x
    obj = x**2 + x * y + y**2 + y * z + z**2 + 2 * x
    m.setObjective(obj)

    # Add constraint: x + 2 y + 3 z >= 4
    m.addConstr(x + 2 * y + 3 * z >= 4, "c0")

    # Add constraint: x + y >= 1
    m.addConstr(x + y >= 1, "c1")

    m.optimize()

    for v in m.getVars():
        print(f"{v.VarName} {v.X:g}")

    print(f"Obj: {m.ObjVal:g}")

    x.VType = GRB.INTEGER
    y.VType = GRB.INTEGER
    z.VType = GRB.INTEGER

    m.optimize()

    for v in m.getVars():
        print(f"{v.VarName} {v.X:g}")

    print(f"Obj: {m.ObjVal:g}")


# Import data
dim = 1021
small_dim = 50

dist = pd.read_csv("TFP-data-master/imdbSPdist3digits.txt", header=None, index_col=False)
dist = dist.drop(dist.columns[dim], axis=1)
print(dist)

small_dist = dist.iloc[:small_dim, :small_dim]
print(small_dist)


P =  np.triu(dist, k=1)
small_P = np.triu(small_dist, k=1)
print(small_P)


skills = pd.read_csv("TFP-data-master/imdbskills.txt", sep="\t", header=None, index_col=False)
skills.fillna(0, inplace=True)
skills = skills.astype(int)
small_skills = skills.iloc[:small_dim]
print(small_skills)
print(skills[5].T)
print("data types")
vector = small_skills[5].values
print(vector.shape)

# N_size: size of set of candidates
# req_skills: set of skills required on the team
def first_model(N_size, req_skills):

    # model
    m = Model("first")

    # Create variables
    y = m.addMVar(shape=N_size, vtype=GRB.BINARY, name="y")
    print(y.shape)

    # Set objective
    obj = (small_P@y)@y
    m.setObjective(obj)

    # Add constraint: a skill is covered

    for skill_no in req_skills:

        m.addConstr(small_skills[skill_no].values @ y >= 1 )


    m.optimize()

    for v in m.getVars():
        print(f"{v.VarName} {v.X:g}")

    print(f"Obj: {m.ObjVal:g}")


first_model(small_dim, [3,4,5,6,11,12,19,20,23,26])