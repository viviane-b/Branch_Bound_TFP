import numpy as np
import pandas as pd
import ast


def read_data() -> (list[list[float]], list[list[bool]]):
    dim = 1021

    dist = pd.read_csv("TFP-data-master/imdbSPdist3digits.txt", header=None, index_col=False)
    dist = dist.drop(dist.columns[dim], axis=1)

    P =  np.triu(dist, k=1)
    P = P.tolist()


    skills = pd.read_csv("TFP-data-master/imdbskills.txt", sep="\t", header=None, index_col=False)
    skills.fillna(0, inplace=True)
    skills = skills.astype(int)
    skills = skills.to_numpy().tolist()

    return P, skills


# TO DELETE
def read_small_data(dist, skills, small_dim = 50):

    small_dist = dist.iloc[:small_dim, :small_dim]
    small_P = np.triu(small_dist, k=1)
    small_skills = skills.iloc[:small_dim]

    vector = small_skills[5].values

    return small_P, vector


def get_req_skills(m:int, seed:int) -> list:
    req_skill_sets = pd.read_csv("TFP-data-master/imdb_instance_information.txt", sep="\t", index_col=False)
    row =  req_skill_sets.loc[(req_skill_sets['m'].eq(m)) & req_skill_sets['seed'].eq(f"seed={seed}")]
    req_skills  = row["skills"].values
    req_skills = ast.literal_eval(req_skills[0])
    req_skills = list(req_skills)
    print(req_skills)
    return req_skills


def preprocess_P(P:list[list[float]], skills:[list[list[bool]]], req_skills:list[int]) -> (list[list[float]], list[list[bool]]):
    dim = len(P)
    processed_P = P.copy()
    processed_skills = skills.copy()
    candidates_to_delete = []
    for i in range(dim):
        valid_candidate = False
        for s in req_skills:
            if skills[i][s]:
                valid_candidate = True
                break
        if not valid_candidate:
            candidates_to_delete.append(i)

    processed_P = np.delete(processed_P, candidates_to_delete, axis=0)
    processed_P = np.delete(processed_P, candidates_to_delete, axis=1)
    processed_skills = np.delete(processed_skills, candidates_to_delete, axis=0)

    return processed_P, processed_skills

"""
NOTE: they didn't keep the original candidate number in the solution of the paper. I will do the same.
"""
# TODO: could be an improvement from the paper to keep track of the original candidate numbers!
# TODO: other improvement: test on unfeasible cases