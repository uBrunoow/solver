# Bibliotecas
from IPython.display import display, Markdown, Latex, Math
import numpy as np
import sympy

class SOLVER:
    def __init__(self,tableau):
        self.original_tableau = sympy.Matrix(tableau)
        self.current_tableau = self.original_tableau.copy()
        self.num_rows = self.original_tableau.shape[0]
        self.num_cols = self.original_tableau.shape[1]
        self.num_vars = self.num_cols - self.num_rows
        self.vars = { "X_"+str(i+1) : {"type": "NB" if i < self.num_vars else "B",
                                      "value": 0 if i < self.num_vars else tableau[i-self.num_vars+1][-1],
                                      "row": 0 if i<(self.num_cols-self.num_rows) else i-self.num_vars+1 }
                     for i in range(self.num_cols-1)}
        self.lpivo = -1
        self.cpivo = -1

    def isoptimum(self):
        if min(self.current_tableau[0,:]) < 0:
            return False
        else:
            return True

    def pivo(self):
        self.cpivo = np.argmin(self.current_tableau[0,:])
        menor = np.inf
        for lin in range(1,self.num_rows):
            if self.current_tableau[lin, self.cpivo] > 0:
                temp = self.current_tableau[lin, self.num_cols-1]/self.current_tableau[lin, self.cpivo]
                if temp < menor:
                    self.lpivo = lin
                    menor = temp


    def iteration(self):
        #Passo 01) Transformar o pivo em 1
        TC = self.current_tableau
        LP = self.lpivo
        CP = self.cpivo
        TC[LP,:] = TC[LP,:] / TC[LP,CP]
        #Passo 02) Para cada linha restante, zero os elementos da coluna do pivo fazendo a transformação L[i,:] = L[i,:] - L[i,CP]*L[LP,:]
        for i in range(self.num_rows):
            if i != self.lpivo:
                TC[i,:] = TC[i,:] - TC[i,CP] * TC[LP,:]
        self.update_dict()

    def update_dict(self):
        variables = list(self.vars.keys())
        pos = [self.vars[key]['row'] for key in self.vars.keys()]
        #Entra na base
        self.vars[variables[self.cpivo]]['type']="B"
        self.vars[variables[self.cpivo]]['value']=self.current_tableau[self.lpivo,-1]
        self.vars[variables[self.cpivo]]['row']=self.lpivo
        #Sai da base
        exit_var = variables[pos.index(self.lpivo)]
        self.vars[exit_var]['type'] = "NB"
        self.vars[exit_var]['value']=0
        self.vars[exit_var]['row'] = 0

    def solver(self):
        iter = 0
        step = r"$$\begin{matrix}"
        self.current_tableau = self.original_tableau.copy()
        while not self.isoptimum():
            step += r"\begin{matrix} " + self.latex_solution()[2:-2] + r"\ Tableau \"
            step += self.latex()[2:-2] + r"\ Pivo \"
            self.pivo()
            step += self.latex(pivo=True)[2:-2] + r"\end{matrix} &"
            self.iteration()
            iter+=1
        step += self.latex_solution()[2:-2] + r" \ Tableau \ Final \"
        step += self.latex()[2:-2]
        step += r"\end{matrix}$$"
        return step

    def latex_solution(self):
        base = []
        notbase = []
        for key,value in self.vars.items():
          base += [(key + "=" + str(value['value']))] if value['type'] == "B" else ""
          notbase += [(key + "=" + str(value['value']))] if value['type'] == "NB" else ""
        base = ",".join(base)
        notbase = ",".join(notbase)
        solution = r"$$\begin{matrix} Básicas & = & \{"
        solution += base + r"\}\ Não\ Básicas & = & \{"
        solution += notbase + r"\ Objetivo & = &"
        solution += str(self.current_tableau[0,-1]) + r"\end{matrix}$$"
        return solution

    def latex(self, leftlabel="", pivo = False):
        variables = list(self.vars.keys())
        pos = [self.vars[key]['row'] for key in self.vars.keys()]
        #Primeira Linha
        code = r"$$" + leftlabel +r"\left[ \left| \begin{matrix} Vars \ Z "
        for lin in range(self.num_rows-1):
            var = variables[pos.index(lin+1)]
            code+= r'\ \leftarrow ' + var if lin  + 1 == self.lpivo and pivo else r'\' + var
        code += r'\end{matrix} \right| '#\right] \]'
        code += r'\begin{matrix}'
        #Cabeçalho
        for j in range(self.num_cols-1):
            code += r'\downarrow' if j == self.cpivo and pivo else ''
            code+= ' ' + variables[j] + ' & '
        code += r' b \'
        for i in range(self.num_rows):
            for j in range(self.num_cols):
              if i == self.lpivo and j == self.cpivo and pivo:
                code += "\fbox{" + str(self.current_tableau[i,j]) + "}"
              else:
                code += str(self.current_tableau[i,j])
              code += r' & ' if j