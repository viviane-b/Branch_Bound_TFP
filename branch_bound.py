import numpy as np
from data_importer import *
from gurobipy import Model, GRB

dim = 1021
P, skills = read_data()

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


big_Number = 10000000

P_symmetric = P + np.transpose(P)

req_skills = get_req_skills(4, 8)
# from example
req_skills = [0,1,2]

# there are N candidates

def branch_bound():
    node_counter = 0
    queue = list[Node]

    ub = big_Number     # upper bound
    T = None        # incumbent solution

    # Create root node 0
    root = RootNode(node_counter)

    for n in range(dim):
        zeta_opt, value_opt = solve_subproblem(n, root.get_C1(), root.get_C2())
        root.set_sub_value(value_opt, n)

        root.set_zeta(zeta_opt, n)

        # compute cost of the team
        opt_team = zeta_opt
        opt_team[n] = 1         # n is in the team of subproblem n
        team_cost = compute_team_cost(opt_team)

        # update UB and T if possible.
        if team_cost < ub:
            ub = team_cost
            T = opt_team


    # Solve the relaxed master problem
    y_opt, master_val_opt = solve_master_problem(root.get_sub_values(), root.get_C1(), root.get_C2())

    # Update values at node
    root.set_y_star(y_opt)
    root.compute_z_values()
    root.set_value(master_val_opt)
    lb = master_val_opt             # lower bound


    # Update UB and T if possible
    team_cost = compute_team_cost(y_opt)
    if team_cost < ub:
        ub = team_cost
        T = y_opt
    print(f"lb = {lb}, ub = {ub}")

    #  if LB<UB, then Q= {0}
    if lb < ub:
        queue = [root]


    while lb < ub:
        # next node is the one in the queue that has the minimum value: best-first-search
        min_v = big_Number
        if len(queue) ==0:
            # TODO: algo is over?
            break
        curr_node = queue[0]
        for elem in queue:      # TODO: optimize finding the min
            if elem.get_value() < min_v:
                curr_node = elem
                min_v = curr_node.get_value()
            elif elem.get_value() == min_v:     # if both nodes have the same value, we take the node with the smallest id
                if elem.get_l() < curr_node.get_l():
                    curr_node = elem
                    min_v = curr_node.get_value()

        queue.remove(curr_node)

        # {i,j}: BranchPair( node.y∗ , node.z∗)
        pair = branch_pair(curr_node.get_y_star(), curr_node.get_z_star())
        i = pair[0]
        j = pair[1]

        # Create child node l1
        node_counter += 1
        child1 = Node(node_counter)
        print(f"child 1 created, #{node_counter}, from parent node #{curr_node.get_l()}")

        child1.set_sub_values(curr_node.get_sub_values().copy())
        child1.set_zetas(curr_node.get_zetas().copy())
        child1.set_value(big_Number)

        new_C1 = curr_node.get_C1().copy()
        new_C1.append(pair)
        child1.set_C1(new_C1)      # pair should not be on the same team
        child1.set_C2(curr_node.get_C2().copy())
        print(f"CHILD 1 \n C1: {child1.get_C1()}")
        print(f"C2: {child1.get_C2()}")
        print(f"zetas: {child1.get_zetas()}")
        print(f"sub_values: {child1.get_sub_values()}")

        if child1.get_zetas()[i][j] == 1:
            # Solve Pr_i
            zeta_opt, value_opt = solve_subproblem(i, child1.get_C1(), child1.get_C2())

            if zeta_opt is not None and value_opt is not None:
                child1.set_sub_value(value_opt, i)
                child1.set_zeta(zeta_opt, i)

                opt_team = zeta_opt
                opt_team[i] = 1  # i is in the team of subproblem i
                team_cost = compute_team_cost(opt_team)

                # update UB and T if possible.
                if team_cost < ub:
                    ub = team_cost
                    T = opt_team
                print(f"lb = {lb}, ub = {ub}")

            else:
                child1.set_sub_value(big_Number, i)

        if child1.get_zetas()[j][i] == 1:
            # Solve Pr_j
            zeta_opt, value_opt = solve_subproblem(j, child1.get_C1(), child1.get_C2())

            if zeta_opt is not None and value_opt is not None:
                child1.set_sub_value(value_opt, j)
                child1.set_zeta(zeta_opt, j)

                opt_team = zeta_opt
                opt_team[j] = 1  # j is in the team of subproblem j
                team_cost = compute_team_cost(opt_team)

                # update UB and T if possible.
                if team_cost < ub:
                    ub = team_cost
                    T = opt_team
                print(f"lb = {lb}, ub = {ub}")

            else:
                child1.set_sub_value(big_Number, j)

        # Solve relaxed master problem
        y_opt, master_val_opt = solve_master_problem(child1.get_sub_values(), child1.get_C1(), child1.get_C2())
        if y_opt is not None and master_val_opt is not None:    # else prune by infeasibility
            child1.set_y_star(y_opt)
            child1.compute_z_values()
            child1.set_value(master_val_opt)

            # Update UB and T if possible
            team_cost = compute_team_cost(y_opt)
            if team_cost < ub:
                ub = team_cost
                T = y_opt
            print(f"lb = {lb}, ub = {ub}")

            if child1.get_value() < ub:     # else prune by bound
                # Add this node to the queue to be branched again
                queue.append(child1)

        print(f"node #{child1.get_l()} zetas = {child1.get_zetas()} \n")

        # Create node l2
        node_counter += 1
        child2 = Node(node_counter)
        print(f"child 2 created, #{node_counter}, from parent node #{curr_node.get_l()} ")

        child2.set_sub_values(curr_node.get_sub_values().copy())
        child2.set_zetas(curr_node.get_zetas().copy())
        child2.set_value(big_Number)

        new_C2 = curr_node.get_C2().copy()
        new_C2.append(pair)
        child2.set_C1(curr_node.get_C1().copy())
        print(f"child 2 C1 = {child2.get_C1()}")
        child2.set_C2(new_C2)           # i and j should be in the same team
        print(f"child 2 C2 = {child2.get_C2()}")

        if child2.get_zetas()[i][j] == 0:
            # Solve Pr_i
            zeta_opt, value_opt = solve_subproblem(i, child2.get_C1(), child2.get_C2())

            if zeta_opt is not None and value_opt is not None:
                child2.set_sub_value(value_opt, i)
                child2.set_zeta(zeta_opt, i)

                opt_team = zeta_opt
                opt_team[i] = 1  # i is in the team of subproblem i
                team_cost = compute_team_cost(opt_team)

                # update UB and T if possible.
                if team_cost < ub:
                    ub = team_cost
                    T = opt_team
                print(f"lb = {lb}, ub = {ub}")

            else:
                child2.set_sub_value(big_Number, i)

        if child2.get_zetas()[j][i] == 0:
            # Solve Pr_j
            zeta_opt, value_opt = solve_subproblem(j, child2.get_C1(), child2.get_C2())

            if zeta_opt is not None and value_opt is not None:
                child2.set_sub_value(value_opt, j)
                child2.set_zeta(zeta_opt, j)

                opt_team = zeta_opt
                opt_team[j] = 1  # j is in the team of subproblem j
                team_cost = compute_team_cost(opt_team)

                # update UB and T if possible.
                if team_cost < ub:
                    ub = team_cost
                    T = opt_team
                print(f"lb = {lb}, ub = {ub}")

            else:
                child2.set_sub_value(big_Number, j)

        # Solve relaxed master problem
        y_opt, master_val_opt = solve_master_problem(child2.get_sub_values(), child2.get_C1(), child2.get_C2())
        if y_opt is not None and master_val_opt is not None:    # else prune by infeasibility
            child2.set_y_star(y_opt)
            child2.compute_z_values()
            child2.set_value(master_val_opt)

            # Update UB and T if possible
            team_cost = compute_team_cost(y_opt)
            if team_cost < ub:
                ub = team_cost
                T = y_opt
            print(f"lb = {lb}, ub = {ub}")

            if child2.get_value() < ub:     # else prune by bound
                # Add this node to the queue to be branched again
                queue.append(child2)
        print(f"node #{child2.get_l()} zetas = {child2.get_zetas()} \n")

        # Compute lower bound
        min_v = big_Number
        for node in queue:
            if node.get_value() < min_v:
                min_v = node.get_value()
        lb = min_v

    return ub, T


def branch_pair(y:list[bool], z:list[list[bool]]) -> tuple[int]:
    pair = None
    for i in range (dim):
        if y[i]:
            for j in range (i+1, dim):
                if y[j] and not z[i][j] and not z[j][i]:        # type 1 pair
                    pair = [i, j]
                    print("type 1 pair")
                    return pair

    if pair is None:
        for i in range(dim):
            if y[i]:
                for j in range (i+1, dim):
                    if y[j] and  z[i][j] != z[j][i]:            # type 2 pair
                        pair = [i,j]
                        print("type 2 pair")
                        return pair
    print(f"pair = {pair}")
    return pair


def compute_team_cost(x:list[bool]):
    return (P@np.array(x))@np.array(x)


def solve_subproblem(n:int, C1:list[tuple[int]], C2:list[tuple[int]]):
    print("\n ---- solving subproblem n=", n)
    m = Model("subproblem")

    zeta = m.addMVar(shape=dim, name="zeta", vtype=GRB.BINARY)

    obj = sum(P_symmetric[i][n] * zeta[i] for i in range (0, n)) + sum(P_symmetric[i][n] * zeta[i] for i in range (n + 1, dim))
    m.setObjective(obj, GRB.MINIMIZE)

    # All skills should be covered
    for skill_no in req_skills:
        if skills[n][skill_no] == 0:    # candidate n does not possess the skill. Another member of the team has to have it
            m.addConstr(sum(skills[i][skill_no] * zeta[i] for i in range (0, n))
                        +sum(skills[i][skill_no] * zeta[i] for i in range (n+1, dim)) >= 1)

    for pair in C1:    # pair of candidates that should not be on the same team
        if n in pair:   # check only pairs that contain n       # TODO: maybe some optimization on the loop?
            i = pair[0] if pair[0] != n else pair[1]
            m.addConstr(zeta[i]==0)

    for pair in C2:    # pair of candidates that should be on the same team
        if n in pair:   # check only pairs that contain n
            i = pair[0] if pair[0] != n else pair[1]
            m.addConstr(zeta[i]==1)

    m.setParam('OutputFlag', 0)
    m.optimize()
    if m.status == GRB.OPTIMAL:
        zeta_opt = m.getAttr("X", m.getVars())
        value_opt = m.ObjVal


        print(f"zeta_opt = {zeta_opt}")
        print(f"value_opt = {value_opt})")
        return zeta_opt, value_opt

    elif m.status == GRB.INFEASIBLE:
        print("unfeasible")
        return None, None

    # TODO what if status is FEASIBLE  or other?


# v: values of the subproblems. Size N
def solve_master_problem(v:list[float], C1:list[tuple[int]], C2:list[tuple[int]]):
    print("\n ----- solving master problem")

    m = Model("master_problem")

    y = m.addMVar(shape=dim, name="y", vtype=GRB.BINARY)

    obj = sum(v[j]*y[j] for j in range (dim))/2
    m.setObjective(obj, GRB.MINIMIZE)

    # All skills should be covered
    for skill_no in req_skills:
        m.addConstr(sum(skills[j][skill_no]*y[j] for j in range(dim)) >= 1)

    for pair in C1:     # pair of candidates that should not be on the same team
        m.addConstr(y[pair[0]] + y[pair[1]] <= 1)

    for pair in C2:     # pair of candidates that should be on the same team
        m.addConstr(y[pair[0]] == 1)
        m.addConstr(y[pair[1]] == 1)

    m.setParam('OutputFlag', 0)
    m.optimize()

    if m.status == GRB.OPTIMAL:

        y_opt = m.getAttr("X", m.getVars())
        val_opt = m.ObjVal

        print(f"subproblem y_opt = {y_opt}")
        print(f"subproblem val_opt = {val_opt}")

        return y_opt, val_opt

    elif m.status == GRB.INFEASIBLE:
        print("unfeasible")
        return None, None


class Node:

    value = float     # v'
    C1 = list[tuple[int]]
    C2 = list[tuple[int]]

    sub_values = list[float]       # v_n' for every n in N
    zetas = list[list[bool]]         # optimal ζn' for every n in N
    y_star = list[bool]             # optimal y for every n in N
    z_star = list[list[bool]]       # optimal z, dimension N by N


    def __init__(self, l:int):
        self.l = l      #l: node number
        self.sub_values = [None for i in range(dim)]
        self.zetas = [[None for j in range(dim)] for i in range(dim)]
        self.z_star = [[None for j in range(dim)] for i in range(dim)]

    def get_l(self): return self.l
    def set_value(self, value:float): self.value = value

    def set_C1(self, C1: list[tuple[int]]): self.C1 = C1

    def set_C2(self, C2: list[tuple[int]]): self.C2 = C2

    def set_sub_value(self, sub_value: float, index:int): self.sub_values[index] = sub_value

    def set_sub_values(self, sub_values: list[float]): self.sub_values = sub_values

    def set_zeta(self, zeta: list[bool], index:int): self.zetas[index] = zeta

    def set_zetas(self, zetas: list[list[bool]]): self.zetas = zetas

    def get_value(self): return self.value

    def get_C1(self): return self.C1

    def get_C2(self): return self.C2

    def get_sub_values(self): return self.sub_values

    def get_zetas(self): return self.zetas

    def set_y_star(self, y_star: list[bool]): self.y_star = y_star

    def get_y_star(self): return self.y_star

    def get_z_star(self): return self.z_star


    def compute_z_values(self):
        #z = list[list[bool]]
        #z = [[None for j in range(dim)] for i in range(dim)]  # N*N matrix
        for i in range(dim):
            for j in range(dim):
                if i != j:
                    self.z_star[i][j] = self.y_star[j] * self.zetas[j][i]



class RootNode(Node):

    def __init__(self, l:int):
        super().__init__(l)
        self.l = 0
        self.value = big_Number
        self.C1 = []
        self.C2 = []



ub, T = branch_bound()
print(ub)
print(T)