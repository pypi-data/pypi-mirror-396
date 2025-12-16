'''
Description:

En este archivo se econtraran diferentes modelos genéticos, de manera que se puedan utilizar en el proyecto
de manera sencilla y rápida.

Se agregarán más modelos conforme se vayan necesitando.
'''

import numpy as np
import pandas as pd

# Import the algorithms to be used
from .algorithms.alg_bin import cl_alg_stn_bin
from .algorithms.alg_quantum import cl_alg_quantum
from .algorithms.alg_eda import cl_alg_eda


class GEN():
    def __init__(self, funtion= None, population=None, cant_genes = 8, num_cycles= 100, selection_percent = 0.5, 
                 crossing = 0.5, mutation_percent = 0.3, i_min = None, i_max = None, optimum = "max", 
                 num_qubits = 16, num_variables = 1, select_mode='ranking', datos=None, possibility_selection=0.5,
                 metric="mse", model="polynomial"):
        self.funtion = funtion
        self.population = population
        self.cant_genes = cant_genes
        self.num_qubits = num_qubits
        self.num_ciclos = num_cycles
        self.selection_percent = selection_percent
        self.crossing = crossing
        self.mutation_percent = mutation_percent
        self.i_min = i_min
        self.i_max = i_max
        self.optimum = optimum 
        self.num_variables = num_variables
        self.select_mode = select_mode
        self.datos = datos
        self.possibility_selection = possibility_selection
        self.metric = metric
        self.model = model

    def alg_stn_bin(self):
        algoritmo = cl_alg_stn_bin(
            self.funtion,
            self.population,
            self.cant_genes,
            self.num_ciclos,
            self.selection_percent,
            self.crossing,
            self.mutation_percent,
            self.i_min,
            self.i_max,
            self.optimum,
            self.select_mode,
            self.num_variables
        )
        return algoritmo.run()

    def alg_quantum(self):
        algoritmo = cl_alg_quantum(
            self.funtion,
            self.population,
            self.num_qubits,
            self.num_ciclos,
            self.mutation_percent,
            self.i_min,
            self.i_max,
            self.optimum
        )
        return algoritmo.run()
    

    def alg_eda(self):
        algoritmo = cl_alg_eda(
            self.datos,
            self.population,
            self.num_variables,
            self.num_ciclos,
            self.i_min,
            self.i_max,
            self.possibility_selection,
            self.metric,
            self.model
        )

        return algoritmo.run()


