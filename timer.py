from data_importer import *
from simple_model import *
from branch_bound import *

from tqdm import tqdm
import pandas as pd

df = pd.DataFrame(columns=["m", "seed", "qno", "req_skills", "obj_value_QP", "obj_value_BB",
                           "team_QP", "team_BB", "QP_time", "BB_time"])

rows_list = []

set_m = [4,6,8,10,12,14,16,18,20]
max_seed = 10

complete_P, complete_skills = read_data()

def record_times(path):
    for m in [20]:       #set_m
        for s in tqdm(range(1, 1+1)):       #max_seed
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
            df.to_csv(path, index=False)


    print(rows_list)
    df = pd.DataFrame(rows_list)
    df = df.loc[:,["m", "seed", "qno", "req_skills", "obj_value_QP", "obj_value_BB",
                               "team_QP", "team_BB", "QP_time", "BB_time"] ]
    print(df)

    # export to csv
    df.to_csv(path, index=False)

def compute_means():
    df = pd.DataFrame()
    for m in set_m:
        df_m = pd.read_csv(f"results/results_m{m}.csv")
        df = pd.concat([df, df_m])
    df.reset_index(inplace=True, drop=True)
    df.rename(columns={"obj_value_QP": "obj_value_simple", "team_QP": "team_simple", "QP_time": "simple_time"}, inplace=True)
    print(df)
    df.to_csv("results/all_results.csv", index=False)

    df_mean = df.copy()
    df_mean.drop(["seed", "req_skills",  "obj_value_simple", "obj_value_BB",
                        "team_simple", "team_BB"], axis=1, inplace=True)
    df_count = df_mean.groupby(["m"]).count()
    df_mean = df_mean.groupby(["m"]).mean()
    df_mean.rename(columns={"qno": "mean_qno"}, inplace=True)
    df_mean["nb_instances_tested"] = df_count["qno"]
    df_mean = df_mean.round(2)
    print(df_mean)

    df_mean.to_csv("results/results_means.csv")

