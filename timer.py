from data_importer import *
from quadratic_programming import *
from branch_bound import *

from tqdm import tqdm
import pandas as pd

df = pd.DataFrame(columns=["m", "seed", "qno", "req_skills", "obj_value_QP", "obj_value_BB",
                           "team_QP", "team_BB", "QP_time", "BB_time"])

rows_list = []

set_m = [4,6,8,10,12,14,16,18,20]
max_seed = 10
path = "results/results_m20_1.csv"

complete_P, complete_skills = read_data()


for m in [20]:       #set_m
    for s in tqdm(range(1,max_seed+1)):       #max_seed
        row = {'m': m, 'seed': s}

        req_skills = get_req_skills(m, s)
        P, skills = preprocess_P(complete_P, complete_skills, req_skills)
        dim = len(P)
        print(dim)

        row["qno"] = dim
        row["req_skills"] = req_skills

        team = []
        obj_value, sol, time = first_model(P, skills, req_skills, dim)
        for i in range(dim):
            if sol[i] > 0:
                team.append(i)

        row["obj_value_QP"] = obj_value
        row["team_QP"] = team
        row["QP_time"] = time

        team = []
        obj_value, sol, time = branch_bound(P, skills, req_skills, dim)
        for i in range(dim):
            if sol[i] > 0:
                team.append(i)

        row["obj_value_BB"] = obj_value
        row["team_BB"] = team
        row["BB_time"] = time

        rows_list.append(row)


        df = pd.DataFrame(rows_list)
        df = df.loc[:, ["m", "seed", "qno", "req_skills", "obj_value_QP", "obj_value_BB",
                    "team_QP", "team_BB", "QP_time", "BB_time"]]
        df.to_csv(path)


print(rows_list)
df = pd.DataFrame(rows_list)
df = df.loc[:,["m", "seed", "qno", "req_skills", "obj_value_QP", "obj_value_BB",
                           "team_QP", "team_BB", "QP_time", "BB_time"] ]
print(df)

# export to csv

df.to_csv(path)


"""
req_skills = get_req_skills(4, 44)
P, skills = preprocess_P(complete_P, complete_skills, req_skills)
dim = len(P)
print(dim)
obj_value, sol, time = branch_bound(P, skills, req_skills, dim)
for i in range(dim):
            if sol[i] > 0:
                print(i)

"""