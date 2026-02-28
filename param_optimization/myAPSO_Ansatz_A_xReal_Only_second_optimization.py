"""
@Name: apso_finalerAnsatz_A
@Autor: Yann Rutschke
@E-Mail: yann.rutschke@student.kit.edu
@Created: 31.08.2023
@Description: Use an apso which is parallelized over the population. The parameter vector is calculated in two time
              here: first the dimension reduction model is used. Then the results are used in the model with 17 para-
              meters. This program is using in both case reference drive spezSeg3.
"""
import numpy as np
import pandas
import os

from myAPSO_Ansatz_A_Problem_xReal import *
import pandas as pd

N_GEN = 40      #|
N_POP = 50      #|
ITERATIONS = 1  # -> Parameter für APSO
LOGGING = True # Wenn True LOGGING = True wird die historie aller Parameter in einer csv gespeichert
x_ref_path = os.path.join("Datenaufbereitung", "ModbusMessung","ModbusMessung","2026-02-21_14-46-32_doppelsinus_A1_40_T_10", "position_sim.csv")

preoptimized_7 = [.13457444933600754,8.143018143349469e-07,0.001345873633183951,0.8918265803447054,1.016659154604525,
                  0.0035792500512704306,9.178482939087618e-06,114.0764292488773]

deviation_upper = 1.2
deviation_lower = 0.8

params_best_estimate_bounds = {
    "Staender-Daempfung"     : (1e-4,    1e-1),      ## [N/(m*s)]
    "Staender-Steifigkeit"   : (1e2,     1e7),       ## [N/m]
    "Staender-Masse"         : (preoptimized_7[0] * deviation_lower,    preoptimized_7[0] * deviation_upper),       ## [kg]
    "Spindel-Daempfung"      : (1e-6,    5e-1),      ## [N/(m*s)]
    "Spindel-Steifigkeit"    : (1e3,     1e9),       ## [N/m]
    "Spindelgehaeuse-Masse"  : (1e-4,    1e3),       ## [kg]
    "Spindel-Masse"          : (1e-4,    500),       ## [kg]
    "KGT-Daempfung"          : (1e-4,    5e-1),      ## [N/(m*s)]
    "KGT-Steifigkeit"        : (1e3,     1e10),       ## [N/m]
    "KGT-Trägheitsmoment"    : (preoptimized_7[1] * deviation_lower,    preoptimized_7[1] * deviation_upper),      ## [kg*m²]
    "Reibung-viskos"         : (preoptimized_7[2] * deviation_lower,    preoptimized_7[2] *deviation_upper),      ## [N*m/(rad*s)]
    "Riemen-Daempfung"       : (1e-7,    1e-1),      ## [N*m/rad]
    "Riemen-Steifigkeit"     : (1e1,     1e9),       ## [N*m/rad]
    "Getriebe-Wirkungsgrad"  : (preoptimized_7[3] * deviation_lower,   preoptimized_7[3] * deviation_upper),     ## [-]
    "Getriebe-Uebersetzung"  : (preoptimized_7[4] * deviation_lower,    preoptimized_7[4] * deviation_upper),       ## [-]
    "Leitspindel-Steigung"   : (preoptimized_7[5] * deviation_lower,   preoptimized_7[5] * deviation_upper),     ## [m]
    "Motor-Trägheitsmoment"  : (preoptimized_7[6] * deviation_lower,   preoptimized_7[6] * deviation_upper),      ## [kg*m²]
}

def main():
    #--------Speicherort der Simulink-Modelle-----------
    eng = matlab.engine.start_matlab()
    path = r"./matlab_path"   # Pfad für xAchse_Sim_GR_GA_17V.slx
    eng.addpath(path, nargout=0)

    #-----Problem Variables-----
    n_gen = N_GEN      # Anzahl der Generationen
    n_pop = N_POP      # Populationsgröße

    #------Durchführe der Optimierung und Speichern in csv-Datei---------
    #eng.eval("myCluster = parcluster('local');", nargout=0)
    #eng.eval(f"myCluster.NumWorkers = {NUM_WORKERS};", nargout=0)
    #eng.eval("saveProfile(myCluster);", nargout=0)

    eng.parpool()

    if params_best_estimate_bounds["Getriebe-Wirkungsgrad"][1] > 1:
        params_best_estimate_bounds["Getriebe-Wirkungsgrad"] = (0.99, 1)

    lower_bounds = [bounds[0] for bounds in params_best_estimate_bounds.values()]
    upper_bounds = [bounds[1] for bounds in params_best_estimate_bounds.values()]


    with open("myLog", "w") as mylogfile:
        mylogfile.write("new lower bounds:" + str(lower_bounds))
        mylogfile.write("new upper bounds:" + str(upper_bounds))
    x_ref = read_x_real_ref(x_ref_path)

    n_gen = N_GEN
    n_pop = round(N_POP * 1.5)

    new_referenceDrive(FALL_17_VARS, lower_bounds, upper_bounds, eng, n_gen, n_pop, x_ref)
    eng.quit()


def new_referenceDrive(case, x_l, x_u, eng, n_gen, n_pop, x_ref_array):
    #---------Berechnung von xSimRef-----------------
    with open("apso_finalerAnsatz_A40_Fall_{}.csv".format(case), "w", newline="") as file:
        writer = csv.writer(file, delimiter=",")
        if case == FALL_7_VARS:
            titel = list(PARAM_NAMES_7) + ["beste Fitness", "Zeit"]
        elif case == FALL_17_VARS:
            titel = list(PARAM_NAMES_17) + ["beste Fitness", "Zeit"]
        for i in range(1, n_gen + 1):  # Fitnessverlauf für Dataframe
            titel.append("Fitnessverlauf{}".format(i))
        writer.writerow(titel)

        i = 0
        while i < ITERATIONS:
            problem_set_static_values(case, eng, n_pop, x_ref_array, x_l, x_u)
            problem = MyProblem()
            my_callback = ProgressCallback(current_iteration=i + 1,  ### Gibt status nach jeder generation aus und macht logging möglich
                                           total_iterations=ITERATIONS,
                                           total_gens=n_gen,
                                           case=case)
            res = minimize(problem=problem,
                           algorithm=PSO(pop_size=n_pop, adaptive=True),
                           termination=("n_gen", n_gen),
                           eliminate_duplicates=True,
                           verbose=True,
                           save_history=True,
                           callback=my_callback)
            print('res: ', res)
            print("Best solution found: \nX = %s\nF = %s" % (res.X, res.F))
            print("Time:", res.exec_time)
            val = [e.opt.get("F")[0] for e in res.history]
            data = np.append(res.X, res.F)
            data1 = np.append(data, res.exec_time)
            data2 = np.append(data1, val)
            writer.writerow(data2)
            i += 1

def problem_set_static_values(case, eng, n_pop, x_sim_ref, x_l, x_u):
    MyProblem.static_n_pop = n_pop
    MyProblem.static_case = case
    MyProblem.static_xSimRefArray = x_sim_ref
    MyProblem.static_xl = x_l
    MyProblem.static_xu = x_u
    MyProblem.engine = eng
    if case == FALL_7_VARS:
        MyProblem.static_n_var = 7
    elif case == FALL_17_VARS:
        MyProblem.static_n_var = 17

def read_x_real_ref(filename_case):
    ref_data  = pd.read_csv(filename_case, names=["time_s", "position_mm"])
    ref_data = ref_data["position_mm"].to_numpy(dtype=float)
    print(f"Daten aus: {filename_case} eingelesen.")
    return ref_data

if __name__=='__main__':
    main()

