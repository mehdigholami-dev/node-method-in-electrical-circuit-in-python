import numpy as np

class Circuit:
    def __init__(self):
        self.nodes = ['0']
        self.resistors = []
        self.current_sources = []

    def add_node(self, node_name):
        if node_name not in self.nodes:
            self.nodes.append(node_name)

    def add_resistor(self, n1, n2, R):
        self.add_node(n1)
        self.add_node(n2)
        self.resistors.append((n1, n2, R))

    def add_current_source(self, node, I):
        self.add_node(node)
        self.current_sources.append((node, I))

    def build_y_matrix(self):
        main_nodes = []
        for n in self.nodes:
            if n != '0':
                main_nodes.append(n)

        N = len(main_nodes)
        node_index = {}
        for i in range(N):
            node_index[main_nodes[i]] = i

        Y = np.zeros((N, N))
        I_vec = np.zeros(N)

        for n1, n2, R in self.resistors:
            g = 1.0 / R
            if n1 != '0' and n2 != '0':
                i = node_index[n1]
                j = node_index[n2]
                Y[i, i] = Y[i, i] + g
                Y[j, j] = Y[j, j] + g
                Y[i, j] = Y[i, j] - g
                Y[j, i] = Y[j, i] - g
            elif n1 != '0':
                i = node_index[n1]
                Y[i, i] = Y[i, i] + g
            elif n2 != '0':
                j = node_index[n2]
                Y[j, j] = Y[j, j] + g

        for node, I in self.current_sources:
            if node != '0':
                i = node_index[node]
                I_vec[i] = I_vec[i] - I

        return Y, I_vec, node_index

    def solve_circuit(self):
        Y, I_vec, node_index = self.build_y_matrix()
        V_vals = np.linalg.solve(Y, I_vec)

        V_dict = {}
        for n in self.nodes:
            V_dict[n] = 0.0

        for node in node_index:
            idx = node_index[node]
            V_dict[node] = V_vals[idx]

        return V_dict

    def branch_currents(self, V_dict):
        currents = []
        for n1, n2, R in self.resistors:
            v1 = V_dict[n1]
            v2 = V_dict[n2]
            I = (v1 - v2) / R
            currents.append((n1, n2, I))
        return currents

    def validate_kcl(self, V_dict):
        for node in self.nodes:
            if node == '0':
                continue

            total_i = 0
            for n1, n2, I in self.branch_currents(V_dict):
                if n1 == node:
                    total_i = total_i + I
                if n2 == node:
                    total_i = total_i - I

            for n_src, I_src in self.current_sources:
                if n_src == node:
                    total_i = total_i - I_src

            print("Node", node, "KCL Sum:", total_i)


if __name__ == "__main__":
    c = Circuit()
    c.add_resistor('1', '0', 10)
    c.add_resistor('2', '0', 5)
    c.add_resistor('1', '2', 15)
    c.add_current_source('2', 2)

    volts = c.solve_circuit()

    print("Voltages:")
    for node in volts:
        print("V" + node, "=", round(volts[node], 3))

    print("\nCurrents:")
    currents = c.branch_currents(volts)
    for n1, n2, I in currents:
        print("I", n1, "to", n2, "=", round(I, 3))

    print("\nKCL Check:")
    c.validate_kcl(volts)
