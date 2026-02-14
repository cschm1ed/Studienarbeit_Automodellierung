
from pymoo.algorithms.soo.nonconvex.pso import PSO
from pymoo.optimize import minimize
import numpy as np
from pymoo.core.problem import Problem
from pymoo.core.callback import Callback
from myAPSO_Ansatz_A import LOGGING
import csv
import matlab.engine

FALL_7_VARS = 1
FALL_17_VARS = 2

PARAM_NAMES_7 = ["Gesamtmasse", "KGT-Trägheitsmoment", "Reibung-viskos",
                  "Getriebe-Wirkungsgrad", "Getriebe-Uebersetzung",
                  "Leitspindel-Steigung", "Motor-Trägheitsmoment"]

PARAM_NAMES_17 = ["Staender-Daempfung", "Staender-Steifigkeit", "Staender-Masse",
                   "Spindel-Daempfung", "Spindel-Steifigkeit", "Spindelgehaeuse-Masse",
                   "Spindel-Masse", "KGT-Daempfung", "KGT-Steifigkeit",
                   "KGT-Trägheitsmoment", "Reibung-viskos", "Riemen-Daempfung",
                   "Riemen-Steifigkeit", "Getriebe-Wirkungsgrad", "Getriebe-Uebersetzung",
                   "Leitspindel-Steigung", "Motor-Trägheitsmoment"]

class MyProblem(Problem):
    # statischen Variablen die für die parallele Ausführung und die Vervendung von verschiedene Modelle benötigt werden.
    static_n_pop = 0
    static_case = 0
    static_xSimRefArray = 0
    static_n_var = 7
    static_xl = []
    static_xu = []
    engine = None
    # static_n_var, static_xl und static_xu werden überschrieben.

    def __init__(self,  **kwargs):
        super().__init__(n_var =    self.__class__.static_n_var,
                         n_obj =    1,
                         xl =       np.array(self.__class__.static_xl),
                         xu =       np.array(self.__class__.static_xu),
                         var_type = float,
                                    **kwargs)

    def _evaluate(self, x_np, out, *args, **kwargs):
        # x_np is the numpy array, x is the list for MATLAB
        x = x_np.tolist()
        simulinkModell = ""
        if self.__class__.static_case == FALL_7_VARS:
            n_abtastpunkte = 3191
            MyProblem.engine.assignin('base', 'start_position', matlab.double(-200), nargout=0)
            simulinkModell = 'xAchse_Sim_GR_GA_nR_SpezSeg3_7V'
        elif self.__class__.static_case == FALL_17_VARS:
            n_abtastpunkte = 3191
            MyProblem.engine.assignin('base', 'start_position', matlab.double(-200), nargout=0)
            simulinkModell = 'xAchse_Sim_GR_GA_nR_SpezSeg3_17V'

        # Run Parallel Simulation
        matlab_matrix = matlab.double(x)
        MyProblem.engine.workspace['iN'] = MyProblem.engine.simulinkSimulationInputArray(matlab_matrix,
                                                                                         self.__class__.static_n_pop,
                                                                                         simulinkModell)
        MyProblem.engine.workspace['aut'] = MyProblem.engine.parsim(MyProblem.engine.workspace['iN'],
                                                                    'TransferBaseWorkspaceVariables', 'on')
        xSimS_fitness = np.zeros(self.__class__.static_n_pop)
        ref = np.squeeze(self.__class__.static_xSimRefArray)
        for i in range(0, self.__class__.static_n_pop):
            # Use getxSim helper (safest way to get data from the 'aut' workspace variable)
            try:
                xSim = MyProblem.engine.getxSim(MyProblem.engine.workspace['aut'], i + 1)
                xSim = np.squeeze(np.array(xSim))
                if xSim.shape == ref.shape:
                    xSimS_fitness[i] = np.sum(abs(xSim - ref))
                else:
                    raise ValueError("Shape Mismatch")
            except Exception:
                # DIAGNOSTICS: If getxSim fails or shape is wrong
                error_msg = MyProblem.engine.eval(f"aut({i + 1}).ErrorMessage")
                print(f"\n--- SIMULATION FAILED: Particle {i} ---")
                print(f"Reason: {error_msg if error_msg else 'Numerical Instability/Early Termination'}")
                print(f"Parameters: {x[i]}")
                xSimS_fitness[i] = 1e12  # Penalty value

        out["F"] = xSimS_fitness

## notify Wird während der optimierung nach jeder Generation aufgerufen
class ProgressCallback(Callback):
    def __init__(self, current_iteration, total_iterations, total_gens, case):
        super().__init__()
        self.current_iteration = current_iteration
        self.total_iterations = total_iterations
        self.total_gens = total_gens
        self.case = case

    def notify(self, algorithm):
        # algorithm.n_gen returns the number of generations completed so far
        print("---------------------------------------")
        print(f"GENERATION: {algorithm.n_gen}/{self.total_gens}; ITERATION: {self.current_iteration}/{self.total_iterations}, CASE: {self.case}")
        print("---------------------------------------")

        if LOGGING:
            current_x = algorithm.pop.get("X")
            n_particles = current_x.shape[0]
            gen_column = np.full((n_particles, 1), algorithm.n_gen)
            data_to_save = np.hstack((current_x, gen_column))
            mode = "w" if algorithm.n_gen == 1 else "a"
            with open(f"parameter_historie_fall_{self.case}.csv", mode, newline="") as f:
                csvWriter = csv.writer(f, delimiter=',')
                if algorithm.n_gen == 1:
                    if self.case == FALL_7_VARS:
                        header = PARAM_NAMES_7 + ["Generation"]
                    elif self.case == FALL_17_VARS:
                        header = PARAM_NAMES_17 + ["Generation"]
                    csvWriter.writerow(header)
                csvWriter.writerows(data_to_save)


