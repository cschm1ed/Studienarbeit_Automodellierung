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

N_GEN = 30      #|
N_POP = 50      #|
ITERATIONS = 1  # -> Parameter für APSO
LOGGING = True # Wenn True LOGGING = True wird die historie aller Parameter in einer csv gespeichert
x_ref_path = os.path.join("Datenaufbereitung", "SammlungDrehzUndVorschubKorrigiertDekodiert",
                              "2026-01-31_17-03-16doppelsinusF_5126_A1_5_f1_5_A2_2_f2_5_1", "position_sim.csv")

## Reihenfolge in dictionary ist relevant damit c1 - c17 iteriert werden kann
## Werte als (lower_bound, upper_bound) Tupel
params_best_estimate_bounds = {
    "Staender-Daempfung"     : (1e-3,    1e0),      ## [N/(m*s)]
    "Staender-Steifigkeit"   : (1e3,     1e6),      ## [N/m]
    "Staender-Masse"         : (0.01,    1.0),      ## [kg]
    "Spindel-Daempfung"      : (1e-3,    1e0),      ## [N/(m*s)]
    "Spindel-Steifigkeit"    : (1e4,     1e7),      ## [N/m]
    "Spindelgehaeuse-Masse"  : (0.005,   0.5),      ## [kg]
    "Spindel-Masse"          : (0.005,   0.5),      ## [kg]
    "KGT-Daempfung"          : (1e-3,    1e0),      ## [N/(m*s)]
    "KGT-Steifigkeit"        : (1e4,     1e7),      ## [N/m]
    "KGT-Trägheitsmoment"    : (1e-8,    1e-5),     ## [kg*m²]
    "Reibung-viskos"         : (1e-5,    1e-2),     ## [N*m/(rad*s)]
    "Riemen-Daempfung"       : (1e-4,    1e-1),     ## [N*m/rad]
    "Riemen-Steifigkeit"     : (1e2,     1e5),      ## [N*m/rad]
    "Getriebe-Wirkungsgrad"  : (0.90,    0.999),    ## [-]
    "Getriebe-Uebersetzung"  : (0.1,     10),       ## [-]
    "Leitspindel-Steigung"   : (0.002,   0.01),     ## [m]
    "Motor-Trägheitsmoment"  : (1e-7,    1e-4),     ## [kg*m²]
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

    # Durchführen Versuch mit Dimensionsreduktion
    #-------- Definition des Suchraums Dimensionsreduziert ---------
    ## c1 - c7 wie in Matlab-Modell bzw. in Arbeit
    deviation = 0.05
    params_dim_red_upper_bounds = [
                    params_best_estimate_bounds["Staender-Masse"][1] + params_best_estimate_bounds["Spindel-Masse"][1]
                        + params_best_estimate_bounds["Spindelgehaeuse-Masse"][1], ## Gesamtmasse
                    params_best_estimate_bounds["KGT-Trägheitsmoment"][1],
                    params_best_estimate_bounds["Reibung-viskos"][1],
                    params_best_estimate_bounds["Getriebe-Wirkungsgrad"][1],
                    params_best_estimate_bounds["Getriebe-Uebersetzung"][1],
                    params_best_estimate_bounds["Leitspindel-Steigung"][1],
                    params_best_estimate_bounds["Motor-Trägheitsmoment"][1]
                    ]

    params_dim_red_lower_bounds = [
                    params_best_estimate_bounds["Staender-Masse"][0] + params_best_estimate_bounds["Spindel-Masse"][0]
                        + params_best_estimate_bounds["Spindelgehaeuse-Masse"][0], ## Gesamtmasse
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

    deviation_preopt_lower = 0.9
    deviation_preopt_upper = 1.1
    new_estimates_bounds = {
        "Staender-Daempfung"     : (params_best_estimate_bounds["Staender-Daempfung"][0],
                                    params_best_estimate_bounds["Staender-Daempfung"][1]),      ## [N/(m*s)]
        "Staender-Steifigkeit"   : (params_best_estimate_bounds["Staender-Steifigkeit"][0],
                                    params_best_estimate_bounds["Staender-Steifigkeit"][1]),    ## [N/m]
        "Staender-Masse"         : (params_best_estimate_bounds["Staender-Masse"][0],
                                    params_best_estimate_bounds["Staender-Masse"][1]),          ## [kg]
        "Spindel-Daempfung"      : (params_best_estimate_bounds["Spindel-Daempfung"][0],
                                    params_best_estimate_bounds["Spindel-Daempfung"][1]),      ## [N/(m*s)]
        "Spindel-Steifigkeit"    : (params_best_estimate_bounds["Spindel-Steifigkeit"][0],
                                    params_best_estimate_bounds["Spindel-Steifigkeit"][1]),    ## [N/m]
        "Spindelgehaeuse-Masse"  : (params_best_estimate_bounds["Spindelgehaeuse-Masse"][0],
                                    params_best_estimate_bounds["Spindelgehaeuse-Masse"][1]),  ## [kg]
        "Spindel-Masse"          : (params_best_estimate_bounds["Spindel-Masse"][0],
                                    params_best_estimate_bounds["Spindel-Masse"][1]),          ## [kg]
        "KGT-Daempfung"          : (params_best_estimate_bounds["KGT-Daempfung"][0],
                                    params_best_estimate_bounds["KGT-Daempfung"][1]),          ## [N/(m*s)]
        "KGT-Steifigkeit"        : (params_best_estimate_bounds["KGT-Steifigkeit"][0],
                                    params_best_estimate_bounds["KGT-Steifigkeit"][1]),        ## [N/m]
        "KGT-Trägheitsmoment"    : (df_apso_DimRed['KGT-Trägheitsmoment'].loc['mean'].copy() * deviation_preopt_lower,
                                    df_apso_DimRed['KGT-Trägheitsmoment'].loc['mean'].copy() * deviation_preopt_upper),     ## [kg*m²]
        "Reibung-viskos"         : (df_apso_DimRed['Reibung-viskos'].loc['mean'].copy() * deviation_preopt_lower,
                                    df_apso_DimRed['Reibung-viskos'].loc['mean'].copy() * deviation_preopt_upper),          ## [N*m/(rad*s)]
        "Riemen-Daempfung"       : (params_best_estimate_bounds["Riemen-Daempfung"][0],
                                    params_best_estimate_bounds["Riemen-Daempfung"][1]),       ## [N*m/rad]
        "Riemen-Steifigkeit"     : (params_best_estimate_bounds["Riemen-Steifigkeit"][0],
                                    params_best_estimate_bounds["Riemen-Steifigkeit"][1]),     ## [N*m/rad]
        "Getriebe-Wirkungsgrad"  : (df_apso_DimRed['Getriebe-Wirkungsgrad'].loc['mean'].copy() * deviation_preopt_lower,
                                    df_apso_DimRed['Getriebe-Wirkungsgrad'].loc['mean'].copy() * deviation_preopt_upper),   ## [-]
        "Getriebe-Uebersetzung"  : (df_apso_DimRed['Getriebe-Uebersetzung'].loc['mean'].copy() * deviation_preopt_lower,
                                    df_apso_DimRed['Getriebe-Uebersetzung'].loc['mean'].copy() * deviation_preopt_upper),   ## [-]
        "Leitspindel-Steigung"   : (df_apso_DimRed['Leitspindel-Steigung'].loc['mean'].copy() * deviation_preopt_lower,
                                    df_apso_DimRed['Leitspindel-Steigung'].loc['mean'].copy() * deviation_preopt_upper),    ## [m]
        "Motor-Trägheitsmoment"  : (df_apso_DimRed['Motor-Trägheitsmoment'].loc['mean'].copy() * deviation_preopt_lower,
                                    df_apso_DimRed['Motor-Trägheitsmoment'].loc['mean'].copy() * deviation_preopt_upper)    ## [kg*m²]
    }
    if new_estimates_bounds["Getriebe-Wirkungsgrad"][1] > 1:
        new_estimates_bounds["Getriebe-Wirkungsgrad"] = (0.99, 1)

    lower_bounds = [bounds[0] for bounds in new_estimates_bounds.values()]
    upper_bounds = [bounds[1] for bounds in new_estimates_bounds.values()]


    with open("myLog", "w") as mylogfile:
        mylogfile.write("new lower bounds:" + str(lower_bounds))
        mylogfile.write("new upper bounds:" + str(upper_bounds))
    x_ref = read_x_real_ref(x_ref_path)
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
                           save_history=False,
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
