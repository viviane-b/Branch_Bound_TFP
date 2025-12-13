from data_importer import *
from simple_model import *
from branch_bound import *


def main():
    set_m = [4, 6, 8, 10, 12, 14, 16, 18, 20]
    m = 0
    s = 0
    while m not in set_m:
        m_string = input('Number of required skills (in {4,6,8,10,12,14,16,18,20}): ')
        try:
            m = int(m_string)
        except ValueError:
            m = 0
    while s not in range (1, 101):
        s_string = input('Seed (1 to 100): ')
        try:
            s = int(s_string)
        except ValueError:
            s = 0

    complete_P, complete_skills = read_data()
    req_skills = get_req_skills(m, s)
    P, skills = preprocess_P(complete_P, complete_skills, req_skills)
    dim = len(P)
    print(f"Number of qualified candidates: {dim}")

    print(f"\nApplying Gurobi algorithm with m={m} and s={s}...")
    team_g = []
    obj_value_g, sol_g, time_g = first_model(P, skills, req_skills, dim)
    for i in range(dim):
        if sol_g[i] > 0:
            team_g.append(i)

    print(f"\nApplying Branch and Bound algorithm with m={m} and s={s}...")
    team_bb = []
    obj_value_bb, sol_bb, time_bb = branch_bound(P, skills, req_skills, dim)
    for i in range(dim):
        if sol_bb[i] > 0:
            team_bb.append(i)


    print(f"\n \n----------------------------")
    print("Gurobi model")
    print(f"Time taken: {time_g} s")
    print(f"Optimal team: {team_g}")
    print(f"Cost of optimal team: {obj_value_g}")

    print("\nBranch and bound")
    print(f"Time taken: {time_bb} s")
    print(f"Optimal team: {team_bb}")
    print(f"Cost of optimal team: {obj_value_bb}")





if __name__ == "__main__":
    main()