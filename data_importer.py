import numpy as np
import pandas as pd
import ast


def read_data():
    dim = 1021

    dist = pd.read_csv("TFP-data-master/imdbSPdist3digits.txt", header=None, index_col=False)
    dist = dist.drop(dist.columns[dim], axis=1)

    P =  np.triu(dist, k=1)

    skills = pd.read_csv("TFP-data-master/imdbskills.txt", sep="\t", header=None, index_col=False)
    skills.fillna(0, inplace=True)
    skills = skills.astype(int)

    return P, skills


# TO DELETE
def read_small_data(dist, skills, small_dim = 50):

    small_dist = dist.iloc[:small_dim, :small_dim]
    small_P = np.triu(small_dist, k=1)
    small_skills = skills.iloc[:small_dim]

    vector = small_skills[5].values

    return small_P, vector


def get_req_skills(m, seed):
    req_skill_sets = pd.read_csv("TFP-data-master/imdb_instance_information.txt", sep="\t", index_col=False)
    row =  req_skill_sets.loc[(req_skill_sets['m'].eq(m)) & req_skill_sets['seed'].eq(f"seed={seed}")]
    req_skills  = row["skills"].values
    req_skills = ast.literal_eval(req_skills[0])
    print(req_skills)
    return req_skills