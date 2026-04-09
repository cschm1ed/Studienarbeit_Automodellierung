
##
#
# Das selbe wie bei apso_xReal nur dass die zweite Schicht ein Modell mit nur 11 Parametern verwendet, da
# am Versuchsstand keine Spindel angebaut ist.
#

import numpy as np
import pandas
import os

from Ansatz_A_Problem_xReal_reducedModel import *
import pandas as pd

N_GEN = 40      #|
N_POP = 40      #|
ITERATIONS = 1  # -> Parameter für APSO
LOGGING = True # Wenn True LOGGING = True wird die historie aller Parameter in einer csv gespeichert
x_ref_path = os.path.join("Datenaufbereitung", "ModbusMessung","ModbusMessung","2026-02-28_11-30-31_doppelsinus_75s", "position_sim.csv")

## Reihenfolge in dictionary ist relevant damit c1 - c17 iteriert werden kann
## Werte als (lower_bound, upper_bound) Tupel

params_best_estimate_bounds = {
    "Staender-Masse"        : (1,    1e2),       ## [kg]
    "Riemen-Daempfung"      : (1e-5, 1),  ## [N*m/rad]
    "KGT-Daempfung"         : (1e-4, 1),  ## [N/(m*s)]
    "KGT-Steifigkeit"       : (1e3, 1e8),  ## [N/m]
    "KGT-Trägheitsmoment"   : (8e-7, 1),  ## [kg*m²]
    "Reibung-viskos"        : (1e-4, 1),  ## [N*m/(rad*s)]
    "Riemen-Steifigkeit"    : (1e1, 1e8),  ## [N*m/rad]
    "Getriebe-Uebersetzung" : (1, 2),  ## [-]
    "Getriebe-Wirkungsgrad" : (0.9, 0.999),  ## [-]
    "Leitspindel-Steigung"  : (0.001, 0.005),  ## [m]
    "Motor-Trägheitsmoment" : (8e-6, 1e-2),  ## [kg*m²]
}

def main():
    #--------Speicherort der Simulink-Modelle-----------
    eng = matlab.engine.start_matlab()
    path = r"./matlab_path"
    eng.addpath(path, nargout=0)
    eng.addpath(os.path.join(path, "m_files"), nargout=0)
    eng.addpath(os.path.join(path, "mat_files"), nargout=0)
    eng.addpath(os.path.join(path, "simulink_models"), nargout=0)

    #-----Problem Variables-----
    n_gen = N_GEN      # Anzahl der Generationen
    n_pop = N_POP      # Populationsgröße

    #------Durchführe der Optimierung und Speichern in csv-Datei---------
    #eng.eval("myCluster = parcluster('local');", nargout=0)
    #eng.eval(f"myCluster.NumWorkers = {NUM_WORKERS};", nargout=0)
    #eng.eval("saveProfile(myCluster);", nargout=0)

    eng.parpool()

    # Durchführen Versuch mit Dimensionsreduktion
    #-------- Definition des Suchraums Dimensionsreduziert ---------
    ## c1 - c7 wie in Matlab-Modell bzw. in Arbeit

    params_dim_red_upper_bounds = [
                    params_best_estimate_bounds["Staender-Masse"][1],
                    params_best_estimate_bounds["KGT-Trägheitsmoment"][1],
                    params_best_estimate_bounds["Reibung-viskos"][1],
                    params_best_estimate_bounds["Getriebe-Wirkungsgrad"][1],
                    params_best_estimate_bounds["Getriebe-Uebersetzung"][1],
                    params_best_estimate_bounds["Leitspindel-Steigung"][1],
                    params_best_estimate_bounds["Motor-Trägheitsmoment"][1]
                    ]

    params_dim_red_lower_bounds = [
                    params_best_estimate_bounds["Staender-Masse"][0],
                    params_best_estimate_bounds["KGT-Trägheitsmoment"][0],
                    params_best_estimate_bounds["Reibung-viskos"][0],
                    params_best_estimate_bounds["Getriebe-Wirkungsgrad"][0],
                    params_best_estimate_bounds["Getriebe-Uebersetzung"][0],
                    params_best_estimate_bounds["Leitspindel-Steigung"][0],
                    params_best_estimate_bounds["Motor-Trägheitsmoment"][0]
                    ]


    x_ref = read_x_real_ref(x_ref_path)
    new_referenceDrive(FALL_7_VARS, params_dim_red_lower_bounds, params_dim_red_upper_bounds, eng, n_gen, n_pop, x_ref)
    df_apso_DimRed = pd.read_csv("./apso_finalerAnsatz_A40_Fall_1.csv")
    df_apso_DimRed = df_apso_DimRed.drop(df_apso_DimRed.loc[:, 'beste Fitness':'Fitnessverlauf{}'.format(n_gen)].columns,
                                         axis=1)
    df_apso_DimRed.loc['mean'] = df_apso_DimRed.mean()

    # Durchführen volles Modell
    #-------- Definition des Suchraums volles Modell ----------
    # Berechnung der Massen

    deviation_preopt_lower = 0.8
    deviation_preopt_upper = 1.2
    new_estimates_bounds = {
        "Staender-Masse": (params_best_estimate_bounds["Staender-Masse"][0],
                           params_best_estimate_bounds["Staender-Masse"][1]),
        "Riemen-Daempfung": (params_best_estimate_bounds["Riemen-Daempfung"][0],
                             params_best_estimate_bounds["Riemen-Daempfung"][1]),
        "KGT-Daempfung": (params_best_estimate_bounds["KGT-Daempfung"][0],
                          params_best_estimate_bounds["KGT-Daempfung"][1]),
        "KGT-Steifigkeit": (params_best_estimate_bounds["KGT-Steifigkeit"][0],
                            params_best_estimate_bounds["KGT-Steifigkeit"][1]),
        "KGT-Trägheitsmoment": (df_apso_DimRed['KGT-Trägheitsmoment'].loc['mean'].copy() * deviation_preopt_lower,
                                df_apso_DimRed['KGT-Trägheitsmoment'].loc['mean'].copy() * deviation_preopt_upper),
        "Reibung-viskos": (df_apso_DimRed['Reibung-viskos'].loc['mean'].copy() * deviation_preopt_lower,
                           df_apso_DimRed['Reibung-viskos'].loc['mean'].copy() * deviation_preopt_upper),
        "Riemen-Steifigkeit": (params_best_estimate_bounds["Riemen-Steifigkeit"][0],
                               params_best_estimate_bounds["Riemen-Steifigkeit"][1]),  ## [N*m/rad]
        "Getriebe-Uebersetzung": (df_apso_DimRed['Getriebe-Uebersetzung'].loc['mean'].copy() * deviation_preopt_lower,
                                  df_apso_DimRed['Getriebe-Uebersetzung'].loc['mean'].copy() * deviation_preopt_upper),
        "Getriebe-Wirkungsgrad": (df_apso_DimRed['Getriebe-Wirkungsgrad'].loc['mean'].copy() * deviation_preopt_lower,
                                  df_apso_DimRed['Getriebe-Wirkungsgrad'].loc['mean'].copy() * deviation_preopt_upper),
        "Leitspindel-Steigung": (df_apso_DimRed['Leitspindel-Steigung'].loc['mean'].copy() * deviation_preopt_lower,
                                 df_apso_DimRed['Leitspindel-Steigung'].loc['mean'].copy() * deviation_preopt_upper),
        "Motor-Trägheitsmoment": (df_apso_DimRed['Motor-Trägheitsmoment'].loc['mean'].copy() * deviation_preopt_lower,
                                  df_apso_DimRed['Motor-Trägheitsmoment'].loc['mean'].copy() * deviation_preopt_upper)
    }
    if new_estimates_bounds["Getriebe-Wirkungsgrad"][1] > 1:
        new_estimates_bounds["Getriebe-Wirkungsgrad"] = (0.99, 1)

    lower_bounds = [bounds[0] for bounds in new_estimates_bounds.values()]
    upper_bounds = [bounds[1] for bounds in new_estimates_bounds.values()]


    with open("myLog", "w") as mylogfile:
        mylogfile.write("new lower bounds:" + str(lower_bounds))
        mylogfile.write("new upper bounds:" + str(upper_bounds))
    x_ref = read_x_real_ref(x_ref_path)

    n_gen = N_GEN
    n_pop = round(N_POP)

    new_referenceDrive(FALL_11_VARS, lower_bounds, upper_bounds, eng, n_gen, n_pop, x_ref)
    eng.quit()


def new_referenceDrive(case, x_l, x_u, eng, n_gen, n_pop, x_ref_array):
    #---------Berechnung von xSimRef-----------------
    with open("apso_finalerAnsatz_A40_Fall_{}.csv".format(case), "w", newline="") as file:
        writer = csv.writer(file, delimiter=",")
        if case == FALL_7_VARS:
            titel = list(PARAM_NAMES_7) + ["beste Fitness", "Zeit"]
        elif case == FALL_11_VARS:
            titel = list(PARAM_NAMES_11) + ["beste Fitness", "Zeit"]
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
    elif case == FALL_11_VARS:
        MyProblem.static_n_var = 11

def read_x_real_ref(filename_case):
    ref_data  = pd.read_csv(filename_case, names=["time_s", "position_mm"])
    ref_data = ref_data["position_mm"].to_numpy(dtype=float)
    print(f"Daten aus: {filename_case} eingelesen.")
    return ref_data

if __name__=='__main__':
    main()

