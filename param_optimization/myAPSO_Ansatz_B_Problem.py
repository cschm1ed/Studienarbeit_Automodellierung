
import matlab.engine
from pymoo.algorithms.soo.nonconvex.pso import PSO
from pymoo.optimize import minimize
import numpy as np
from pymoo.core.problem import Problem

CASE_7_PARAMS = 1
CASE_17_PARAMS = 2

class MyProblem(Problem):

    # statischen Variablen die für die parallele Ausführung und die Verwendung von verschiedenen Modelle benötigt werden.
    static_n_pop = 0
    static_case = 0
    static_xSimRefArray = 0
    static_n_var = 7
    static_x_lower_bounds = [(950 + 475 + 238) * 0, 0.0002755 * 0, 0.0722 * 0, 0.931, 0 * 0.95 * 55 / 24, 0.019 * 0, 0.0042845 * 0] #-100% Abweichung nur W.Grad auf 0.931
    static_x_upper_bounds = [(1050 + 525 + 262) * 2, 0.0003045 * 2, 0.0798 * 2, 1, 2 * 1.05 * 55 / 24, 0.021 * 2, 0.0047355 * 2] #+100% Abweichung nur W.Grad auf 1
    # static_n_var, static_x_lower_bounds und static_x_upper_bounds werden überschrieben.

    def __init__(self, eng, **kwargs):
        super().__init__(n_var=self.__class__.static_n_var,
                         n_obj=1,
                         xl=np.array(self.__class__.static_x_lower_bounds),
                         xu=np.array(self.__class__.static_x_upper_bounds),
                         var_type=float,
                         **kwargs)
        self.eng = eng

    def _evaluate(self, x, out, *args, **kwargs):
        # Hier ist x eine Matrix der größe (n_pop,17)
        x = x.tolist()      # numpy.array wird hier zu einer Liste einer List umgewandelt. Einträge sind Float.

        # Für jeden Fall gibt es ein anderes simulink_modell und eine andere Anzahl an Abtastpunkte.
        # Gleiches gilt mit der Startposition. Achtung: 'Stoptime' muss noch in den Modelle eingestellt werden
        # und ist gleich: stop Time = 0,002*(n_abtastpunkte-1)
        if self.__class__.static_case == CASE_7_PARAMS:
            n_abtastpunkte = 2671
            self.eng.assignin('base', 'start_position', matlab.double(-150), nargout=0)
            simulink_modell = 'xAchse_Sim_Pilger5_7V'

        elif self.__class__.static_case == CASE_17_PARAMS:
            n_abtastpunkte = 2051
            self.eng.assignin('base', 'start_position', matlab.double(-150), nargout=0)
            simulink_modell = 'xAchse_Sim_Pilger1_17V'

        # Parallele Version final
        # Erzeugen simulinkSimulationInputArray und durchfuehren der parallele Simulation

        matlab_matrix = matlab.double(x)
        self.eng.workspace['iN'] = self.eng.simulinkSimulationInputArray(matlab_matrix, self.__class__.static_n_pop, simulink_modell)
        self.eng.workspace['aut'] = self.eng.parsim(self.eng.workspace['iN'],
                                          'TransferBaseWorkspaceVariables', 'on')
        # This will print the actual reason the simulation failed
        error_msg = self.eng.eval("aut(1).ErrorMessage")
        if error_msg:
            print("\n--- SIMULATION ERROR ON WORKER 1 ---")
            print(error_msg)
            print("------------------------------------\n")
        # DEBUG: Check what the first simulation actually contains
        print("Available fields in simulation output:", self.eng.eval("fieldnames(aut(1))"))

        x_sim_s = np.empty((self.__class__.static_n_pop, n_abtastpunkte))

        for i in range(0, self.__class__.static_n_pop):
            # If 'x_Sim' is not in the list printed above, this line will crash
            x_sim = self.eng.getxSim(self.eng.workspace['aut'], i + 1)
            x_sim = np.squeeze(x_sim)
            x_sim_s[i] = x_sim - np.squeeze(self.__class__.static_xSimRefArray)

        out["F"] = np.sum(abs(x_sim_s), axis=1)