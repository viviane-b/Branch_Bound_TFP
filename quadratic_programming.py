# a
from fontTools.misc.cython import returns
from gurobipy import Model, GRB
import pandas as pd



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
dist = pd.read_csv("TFP-data-master/imdbSPdist3digits.txt", header=None, index_col=False)
dist = dist.drop(dist.columns[1021], axis=1)
print(dist)