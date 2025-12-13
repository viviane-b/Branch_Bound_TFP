import time

import numpy as np
from node import *
from solvers import *

"""
# example of network from the paper

dim = 5
P = [[0, 0.8, 0.9, 1.5, 1.3],
     [0, 0, 1.4, 0.9, 1.6],
     [0, 0, 0, 1.2, 0.7],
     [0, 0, 0, 0, 0.8],
     [0, 0, 0, 0, 0]]
skills = [[1, 0, 0],    # round
          [0, 1, 0],    # square
          [0, 0, 1],    # losange
          [0, 0, 1],
          [1, 0, 0]]
req_skills = [0,1,2]
"""

big_Number = 10000000
eps = 0.0001

# there are N candidates

def branch_bound(P:list[list[float]], skills:list[list[bool]], req_skills:list[int], dim:int) :
    P_symmetric = P + np.transpose(P)

    node_counter = 0
    queue = list[Node]

    ub = big_Number     # upper bound
    T = None        # incumbent solution

    # Create root node 0
    root = RootNode(l=node_counter, dim=dim, big_Number=big_Number)

    # create model
    solvers = Solvers(dim, P_symmetric, skills, req_skills)
    start = time.time()

    for n in range(dim):


        # update model for every n
        zeta_opt, value_opt = solvers.solve_subproblem_root(n)

        root.set_sub_value(value_opt, n)

        root.set_zeta(zeta_opt, n)

        # compute cost of the team
        opt_team = zeta_opt
        opt_team[n] = 1         # n is in the team of subproblem n
        team_cost = compute_team_cost(opt_team, P)

        # update UB and T if possible.
        if team_cost < ub:
            ub = team_cost
            T = opt_team


    # Solve the relaxed master problem
    y_opt, master_val_opt = solvers.solve_master(root.get_sub_values(), root.get_C1(), root.get_C2())

    # Update values at node
    root.set_y_star(y_opt)
    root.compute_z_values(dim)
    root.set_value(master_val_opt)
    lb = master_val_opt             # lower bound


    # Update UB and T if possible
    team_cost = compute_team_cost(y_opt, P)
    if team_cost < ub:
        ub = team_cost
        T = y_opt

    #  if LB<UB, then Q= {0}
    if lb < ub:
        queue = [root]


    while lb+eps < ub:
        # next node is the one in the queue that has the minimum value: best-first-search
        min_v = big_Number
        if len(queue) ==0:
            break
        curr_node = queue[0]
        for elem in queue:
            if elem.get_value() < min_v:
                curr_node = elem
                min_v = curr_node.get_value()
            elif elem.get_value() == min_v:     # if both nodes have the same value, we take the node with the smallest id
                if elem.get_l() < curr_node.get_l():
                    curr_node = elem
                    min_v = curr_node.get_value()

        queue.remove(curr_node)

        # {i,j}: BranchPair( node.y∗ , node.z∗)
        pair = branch_pair(curr_node.get_y_star(), curr_node.get_z_star(), dim)

        i = pair[0]
        j = pair[1]

        # Create child node l1
        node_counter += 1
        child1 = Node(node_counter, dim)

        child1.set_sub_values(curr_node.get_sub_values().copy())
        child1.set_zetas(curr_node.get_zetas().copy())
        child1.set_value(big_Number)

        new_C1 = curr_node.get_C1().copy()
        new_C1.append(pair)
        child1.set_C1(new_C1)      # pair should not be on the same team
        child1.set_C2(curr_node.get_C2().copy())


        if child1.get_zetas()[i][j] == 1:
            # Solve Pr_i
            zeta_opt, value_opt = solvers.solve_subproblem_node(i, child1.get_C1(), child1.get_C2())

            if zeta_opt is not None and value_opt is not None:
                child1.set_sub_value(value_opt, i)
                child1.set_zeta(zeta_opt, i)

                opt_team = zeta_opt
                opt_team[i] = 1  # i is in the team of subproblem i
                team_cost = compute_team_cost(opt_team, P)

                # update UB and T if possible.
                if team_cost < ub:
                    ub = team_cost
                    T = opt_team

            else:
                child1.set_sub_value(big_Number, i)

        if child1.get_zetas()[j][i] == 1:
            # Solve Pr_j
            zeta_opt, value_opt = solvers.solve_subproblem_node(j, child1.get_C1(), child1.get_C2())

            if zeta_opt is not None and value_opt is not None:
                child1.set_sub_value(value_opt, j)
                child1.set_zeta(zeta_opt, j)

                opt_team = zeta_opt
                opt_team[j] = 1  # j is in the team of subproblem j
                team_cost = compute_team_cost(opt_team,P)

                # update UB and T if possible.
                if team_cost < ub:
                    ub = team_cost
                    T = opt_team

            else:
                child1.set_sub_value(big_Number, j)

        # Solve relaxed master problem
        y_opt, master_val_opt = solvers.solve_master(child1.get_sub_values(), child1.get_C1(), child1.get_C2())

        if y_opt is not None and master_val_opt is not None:    # else prune by infeasibility
            child1.set_y_star(y_opt)
            child1.compute_z_values(dim)
            child1.set_value(master_val_opt)

            # Update UB and T if possible
            team_cost = compute_team_cost(y_opt, P)
            if team_cost < ub:
                ub = team_cost
                T = y_opt

            if child1.get_value() < ub:     # else prune by bound
                # Add this node to the queue to be branched again
                queue.append(child1)


        # Create node l2
        node_counter += 1
        child2 = Node(node_counter, dim)

        child2.set_sub_values(curr_node.get_sub_values().copy())
        child2.set_zetas(curr_node.get_zetas().copy())
        child2.set_value(big_Number)

        new_C2 = curr_node.get_C2().copy()
        new_C2.append(pair)
        child2.set_C1(curr_node.get_C1().copy())
        child2.set_C2(new_C2)           # i and j should be in the same team


        if child2.get_zetas()[i][j] == 0:
            # Solve Pr_i
            zeta_opt, value_opt = solvers.solve_subproblem_node(i, child2.get_C1(), child2.get_C2())

            if zeta_opt is not None and value_opt is not None:
                child2.set_sub_value(value_opt, i)
                child2.set_zeta(zeta_opt, i)

                opt_team = zeta_opt
                opt_team[i] = 1  # i is in the team of subproblem i
                team_cost = compute_team_cost(opt_team, P)

                # update UB and T if possible.
                if team_cost < ub:
                    ub = team_cost
                    T = opt_team

            else:
                child2.set_sub_value(big_Number, i)

        if child2.get_zetas()[j][i] == 0:
            # Solve Pr_j
            zeta_opt, value_opt = solvers.solve_subproblem_node(j, child2.get_C1(), child2.get_C2())

            if zeta_opt is not None and value_opt is not None:
                child2.set_sub_value(value_opt, j)
                child2.set_zeta(zeta_opt, j)

                opt_team = zeta_opt
                opt_team[j] = 1  # j is in the team of subproblem j
                team_cost = compute_team_cost(opt_team, P)

                # update UB and T if possible.
                if team_cost < ub:
                    ub = team_cost
                    T = opt_team

            else:
                child2.set_sub_value(big_Number, j)

        # Solve relaxed master problem
        y_opt, master_val_opt = solvers.solve_master(child2.get_sub_values(), child2.get_C1(), child2.get_C2())
        if y_opt is not None and master_val_opt is not None:    # else prune by infeasibility
            child2.set_y_star(y_opt)
            child2.compute_z_values(dim)
            child2.set_value(master_val_opt)

            # Update UB and T if possible
            team_cost = compute_team_cost(y_opt, P)
            if team_cost < ub:
                ub = team_cost
                T = y_opt

            if child2.get_value() < ub:     # else prune by bound
                # Add this node to the queue to be branched again
                queue.append(child2)


        # Compute lower bound
        min_v = big_Number
        for node in queue:
            if node.get_value() < min_v:
                min_v = node.get_value()
        lb = min_v

    end = time.time()
    run_time = end - start
    print(f"time branch_bound: {end - start}")
    return ub, T, run_time


def branch_pair(y:list[bool], z:list[list[bool]], dim:int) -> tuple[int,int]:
    pair = None
    for i in range (dim):
        if y[i]:
            for j in range (i+1, dim):
                if y[j] and not z[i][j] and not z[j][i]:        # type 1 pair
                    pair = (i, j)
#                    print("type 1 pair")
                    return pair

    if pair is None:
        for i in range(dim):
            if y[i]:
                for j in range (i+1, dim):
                    if y[j] and  z[i][j] != z[j][i]:            # type 2 pair
                        pair = (i,j)
                        print("type 2 pair")
                        return pair

    return pair


def compute_team_cost(x:list[bool], P:list[list[float]]) -> float:
    return float((P@np.array(x))@np.array(x))



