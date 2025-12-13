class Node:

    value = float     # v'
    C1 = list[tuple[int]]
    C2 = list[tuple[int]]

    sub_values = list[float]       # v_n' for every n in N
    zetas = list[list[bool]]         # optimal ζn' for every n in N
    y_star = list[bool]             # optimal y for every n in N
    z_star = list[list[bool]]       # optimal z, dimension N by N


    def __init__(self, l:int, dim:int):
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


    def compute_z_values(self, dim:int):
        for i in range(dim):
            for j in range(dim):
                if i != j:
                    self.z_star[i][j] = self.y_star[j] * self.zetas[j][i]



class RootNode(Node):

    def __init__(self, l:int, dim:int, big_Number:int):
        super().__init__(l, dim)
        self.l = 0
        self.value = big_Number
        self.C1 = []
        self.C2 = []
