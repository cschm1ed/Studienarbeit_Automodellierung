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

N_GEN = 80#|
N_POP = 50      #|
ITERATIONS = 1  # -> Parameter für APSO
LOGGING = True# Wenn True LOGGING = True wird die historie aller Parameter in einer csv gespeichert

## Reihenfolge in dictionary ist relevant damit c1 - c17 iteriert werden kann
params_best_estimate_lower_bound = {
    "Staender-Daempfung"     : 0,      ## [N/(m*s)]
    "Staender-Steifigkeit"   : 0,  ## [N/m]
    "Staender-Masse"         : 0,        ## [kg]
    "Spindel-Daempfung"      : 0,      ## [N/(m*s)]
    "Spindel-Steifigkeit"    : 0,   ## [N/m]
    "Spindelgehaeuse-Masse"  : 0,         ## [kg]
    "Spindel-Masse"          : 0,         ## [kg]
    "KGT-Daempfung"          : 0,      ## [N/(m*s)]
    "KGT-Steifigkeit"        : 0,   ## [N/m]
    "KGT-Trägheitsmoment"    : 0,     ## [kg*m²]
    "Reibung-viskos"         : 0,       ## [N*m/(rad*s)]
    "Riemen-Daempfung"       : 0,           ## [N*m/rad]
    "Riemen-Steifigkeit"     : 0,      ## [N*m/rad]
    "Getriebe-Wirkungsgrad"  : 0,        ## [-]
    "Getriebe-Uebersetzung"  : 0,     ## [-]
    "Leitspundel-Steigung"   : 0,        ## [m]
    "Motor-Trägheitsmoment"  : 0      ## [kg*m²]
}

params_best_estimate_upper_bound = {
    "Staender-Daempfung": 10e6,  ## [N/(m*s)]
    "Staender-Steifigkeit": 10e10,  ## [N/m]
    "Staender-Masse": 10e4,  ## [kg]
    "Spindel-Daempfung": 10e8,  ## [N/(m*s)]
    "Spindel-Steifigkeit": 10e10,  ## [N/m]
    "Spindelgehaeuse-Masse": 10e3,  ## [kg]
    "Spindel-Masse": 10e3,  ## [kg]
    "KGT-Daempfung": 10e8,  ## [N/(m*s)]
    "KGT-Steifigkeit": 10e10,  ## [N/m]
    "KGT-Trägheitsmoment": 10e2,  ## [kg*m²]
    "Reibung-viskos": 10e2,  ## [N*m/(rad*s)]
    "Riemen-Daempfung": 1,  ## [N*m/rad]
    "Riemen-Steifigkeit": 10e10,  ## [N*m/rad]
    "Getriebe-Wirkungsgrad": 1,  ## [-]
    "Getriebe-Uebersetzung": 10e3,  ## [-]
    "Leitspundel-Steigung": 0.1,  ## [m]
    "Motor-Trägheitsmoment": 10e1  ## [kg*m²]
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
                    params_best_estimate_upper_bound["Staender-Masse"] + params_best_estimate_upper_bound["Spindel-Masse"]
                        + params_best_estimate_upper_bound["Spindelgehaeuse-Masse"], ## Gesamtmasse
                    params_best_estimate_upper_bound["KGT-Trägheitsmoment"],
                    params_best_estimate_upper_bound["Reibung-viskos"],
                    params_best_estimate_upper_bound["Getriebe-Wirkungsgrad"],
                    params_best_estimate_upper_bound["Getriebe-Uebersetzung"],
                    params_best_estimate_upper_bound["Leitspundel-Steigung"],
                    params_best_estimate_upper_bound["Motor-Trägheitsmoment"]
                    ]

    params_dim_red_lower_bounds = [
                    params_best_estimate_lower_bound["Staender-Masse"] + params_best_estimate_lower_bound["Spindel-Masse"]
                        + params_best_estimate_lower_bound["Spindelgehaeuse-Masse"], ## Gesamtmasse
                    params_best_estimate_lower_bound["KGT-Trägheitsmoment"],
                    params_best_estimate_lower_bound["Reibung-viskos"],
                    params_best_estimate_lower_bound["Getriebe-Wirkungsgrad"],
                    params_best_estimate_lower_bound["Getriebe-Uebersetzung"],
                    params_best_estimate_lower_bound["Leitspundel-Steigung"],
                    params_best_estimate_lower_bound["Motor-Trägheitsmoment"]
                    ]

    x_ref_path = os.path.join("Datenaufbereitung", "SammlungDrehzUndVorschubKorrigiertDekodiert",
                              "2026-01-31_16-44-26_MyPilger5_1_F6000", "position_sim.csv")
    x_ref = read_x_real_ref(x_ref_path)
    new_referenceDrive(FALL_7_VARS, params_dim_red_lower_bounds, params_dim_red_upper_bounds, eng, n_gen, n_pop, x_ref)
    df_apso_DimRed = pd.read_csv("./apso_finalerAnsatz_A40_Fall_1.csv")
    df_apso_DimRed = df_apso_DimRed.drop(df_apso_DimRed.loc[:, 'beste Fitness':'Fitnessverlauf{}'.format(n_gen)].columns,
                                         axis=1)
    df_apso_DimRed.loc['mean'] = df_apso_DimRed.mean()

    # Durchführen volles Modell
    #-------- Definition des Suchraums volles Modell ----------
    # Berechnung der Massen

    deviation_preoptimized = 1.1
    new_estimates_upper_bounds = {
        "Staender-Daempfung"     : params_best_estimate_upper_bound["Staender-Daempfung"],      ## [N/(m*s)]
        "Staender-Steifigkeit"   : params_best_estimate_upper_bound["Staender-Steifigkeit"],  ## [N/m]
        "Staender-Masse"         : params_best_estimate_upper_bound["Staender-Masse"],        ## [kg]
        "Spindel-Daempfung"      : params_best_estimate_upper_bound["Spindel-Daempfung"],      ## [N/(m*s)]
        "Spindel-Steifigkeit"    : params_best_estimate_upper_bound["Spindel-Steifigkeit"],   ## [N/m]
        "Spindelgehaeuse-Masse"  : params_best_estimate_upper_bound["Spindelgehaeuse-Masse"],     ## [kg]
        "Spindel-Masse"          : params_best_estimate_upper_bound["Spindel-Masse"],         ## [kg]
        "KGT-Daempfung"          : params_best_estimate_upper_bound["KGT-Daempfung"],      ## [N/(m*s)]
        "KGT-Steifigkeit"        : params_best_estimate_upper_bound["KGT-Steifigkeit"],   ## [N/m]
        "KGT-Trägheitsmoment"    : df_apso_DimRed['Variable2'].loc['mean'].copy() * deviation_preoptimized,     ## [kg*m²]
        "Reibung-viskos"         : df_apso_DimRed['Variable3'].loc['mean'].copy() * deviation_preoptimized,     ## [N*m/(rad*s)]
        "Riemen-Daempfung"       : params_best_estimate_upper_bound["Riemen-Daempfung"],           ## [N*m/rad]
        "Riemen-Steifigkeit"     : params_best_estimate_upper_bound["Riemen-Steifigkeit"],      ## [N*m/rad]
        "Getriebe-Wirkungsgrad"  : df_apso_DimRed['Variable4'].loc['mean'].copy() * deviation_preoptimized,     ## [-]
        "Getriebe-Uebersetzung"  : df_apso_DimRed['Variable5'].loc['mean'].copy() * deviation_preoptimized,     ## [-]
        "Leitspundel-Steigung"   : df_apso_DimRed['Variable6'].loc['mean'].copy() * deviation_preoptimized,     ## [m]
        "Motor-Trägheitsmoment"  : df_apso_DimRed['Variable7'].loc['mean'].copy() * deviation_preoptimized     ## [kg*m²]
    }

    deviation_preoptimized = 0.9
    new_estimates_lower_bounds = {
        "Staender-Daempfung"     : params_best_estimate_lower_bound["Staender-Daempfung"],      ## [N/(m*s)]
        "Staender-Steifigkeit"   : params_best_estimate_lower_bound["Staender-Steifigkeit"],  ## [N/m]
        "Staender-Masse"         : params_best_estimate_lower_bound["Staender-Masse"],        ## [kg]
        "Spindel-Daempfung"      : params_best_estimate_lower_bound["Spindel-Daempfung"],      ## [N/(m*s)]
        "Spindel-Steifigkeit"    : params_best_estimate_lower_bound["Spindel-Steifigkeit"],   ## [N/m]
        "Spindelgehaeuse-Masse"  : params_best_estimate_lower_bound["Spindelgehaeuse-Masse"],     ## [kg]
        "Spindel-Masse"          : params_best_estimate_lower_bound["Spindel-Masse"],         ## [kg]
        "KGT-Daempfung"          : params_best_estimate_lower_bound["KGT-Daempfung"],      ## [N/(m*s)]
        "KGT-Steifigkeit"        : params_best_estimate_lower_bound["KGT-Steifigkeit"],   ## [N/m]
        "KGT-Trägheitsmoment"    : df_apso_DimRed['Variable2'].loc['mean'].copy() * deviation_preoptimized,     ## [kg*m²]
        "Reibung-viskos"         : df_apso_DimRed['Variable3'].loc['mean'].copy() * deviation_preoptimized,     ## [N*m/(rad*s)]
        "Riemen-Daempfung"       : params_best_estimate_lower_bound["Riemen-Daempfung"],           ## [N*m/rad]
        "Riemen-Steifigkeit"     : params_best_estimate_lower_bound["Riemen-Steifigkeit"],      ## [N*m/rad]
        "Getriebe-Wirkungsgrad"  : df_apso_DimRed['Variable4'].loc['mean'].copy() * deviation_preoptimized,     ## [-]
        "Getriebe-Uebersetzung"  : df_apso_DimRed['Variable5'].loc['mean'].copy() * deviation_preoptimized,     ## [-]
        "Leitspundel-Steigung"   : df_apso_DimRed['Variable6'].loc['mean'].copy() * deviation_preoptimized,     ## [m]
        "Motor-Trägheitsmoment"  : df_apso_DimRed['Variable7'].loc['mean'].copy() * deviation_preoptimized     ## [kg*m²]
    }

    lower_bounds = [value for value in new_estimates_lower_bounds.values()]
    upper_bounds = [value for value in new_estimates_upper_bounds.values()]


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
            titel = [f"Variable{i}" for i in range(1, 7 + 1)] + ["beste Fitness", "Zeit"]
        elif case == FALL_17_VARS:
            titel = [f"Variable{i}" for i in range(1, 17 + 1)] + ["beste Fitness", "Zeit"]
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
