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
from myAPSO_Ansatz_A_Problem import *
import pandas as pd

N_GEN = 50      #|
N_POP = 50      #|
ITERATIONS = 1  # -> Parameter für APSO
LOGGING = False # Wenn True LOGGING = True wird die historie aller Parameter in einer csv gespeichert

## Reihenfolge in dictionary ist relevant damit c1 - c17 iteriert werden kann
params_best_estimate = {
    "Staender-Daempfung"     : 100000,      ## [N/(m*s)]
    "Staender-Steifigkeit"   : 1500000000,  ## [N/m]
    "Staender-Masse"         : 1000,        ## [kg]
    "Spindel-Daempfung"      : 100000,      ## [N/(m*s)]
    "Spindel-Steifigkeit"    : 100000000,   ## [N/m]
    "Spindelgehaeuse-Masse"  : 500,         ## [kg]
    "Spindel-Masse"          : 250,         ## [kg]
    "KGT-Daempfung"          : 100000,      ## [N/(m*s)]
    "KGT-Steifigkeit"        : 200000000,   ## [N/m]
    "KGT-Trägheitsmoment"    : 0.00029,     ## [kg*m²]
    "Reibung-viskos"         : 0.076,       ## [N*m/(rad*s)]
    "Riemen-Daempfung"       : 1,           ## [N*m/rad]
    "Riemen-Steifigkeit"     : 200000,      ## [N*m/rad]
    "Getriebe-Wirkungsgrad"  : 0.98,        ## [-]
    "Getriebe-Uebersetzung"  : 55 / 24,     ## [-]
    "Leitspindel-Steigung"   : 0.02,        ## [m]
    "Motor-Trägheitsmoment"  : 0.00451      ## [kg*m²]
}

def main():
    c_vector = [param for param in params_best_estimate.values()]
    c = matlab.double(vector=c_vector)

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
    params_dim_red = [
                    params_best_estimate["Staender-Masse"] + params_best_estimate["Spindel-Masse"]
                        + params_best_estimate["Spindelgehaeuse-Masse"], ## Gesamtmasse
                    params_best_estimate["KGT-Trägheitsmoment"],
                    params_best_estimate["Reibung-viskos"],
                    params_best_estimate["Getriebe-Wirkungsgrad"],
                    params_best_estimate["Getriebe-Uebersetzung"],
                    params_best_estimate["Leitspindel-Steigung"],
                    params_best_estimate["Motor-Trägheitsmoment"]
                    ]
    x_lower_bounds = np.multiply(params_dim_red, 1 - deviation) #-5% Abweichungin csv-D
    x_upper_bounds = np.multiply(params_dim_red, 1 + deviation) #+5% Abweichung
    if x_upper_bounds[3] > 1: ## 3 == index Wirkungsgrad
        x_upper_bounds[3] = 1

    x_ref = create_x_sim_ref(FALL_7_VARS, eng, c)
    new_referenceDrive(FALL_7_VARS, x_lower_bounds, x_upper_bounds, eng, n_gen, n_pop, x_ref)

    df_apso_DimRed = pd.read_csv("./apso_finalerAnsatz_A40_Fall_1.csv")
    df_apso_DimRed = df_apso_DimRed.drop(df_apso_DimRed.loc[:, 'beste Fitness':'Fitnessverlauf{}'.format(n_gen)].columns,
                                         axis=1)
    df_apso_DimRed.loc['mean'] = df_apso_DimRed.mean()

    # Durchführen volles Modell
    #-------- Definition des Suchraums volles Modell ----------
    # Berechnung der Massen

    new_estimates = {
        "Staender-Daempfung"     : params_best_estimate["Staender-Daempfung"],      ## [N/(m*s)]
        "Staender-Steifigkeit"   : params_best_estimate["Staender-Steifigkeit"],  ## [N/m]
        "Staender-Masse"         : params_best_estimate["Staender-Masse"],        ## [kg]
        "Spindel-Daempfung"      : params_best_estimate["Spindel-Daempfung"],      ## [N/(m*s)]
        "Spindel-Steifigkeit"    : params_best_estimate["Spindel-Steifigkeit"],   ## [N/m]
        "Spindelgehaeuse-Masse"  : params_best_estimate["Spindelgehaeuse-Masse"],     ## [kg]
        "Spindel-Masse"          : params_best_estimate["Spindel-Masse"],         ## [kg]
        "KGT-Daempfung"          : params_best_estimate["KGT-Daempfung"],      ## [N/(m*s)]
        "KGT-Steifigkeit"        : params_best_estimate["KGT-Steifigkeit"],   ## [N/m]
        "KGT-Trägheitsmoment"    : df_apso_DimRed['KGT-Trägheitsmoment'].loc['mean'].copy(),     ## [kg*m²]
        "Reibung-viskos"         : df_apso_DimRed['Reibung-viskos'].loc['mean'].copy(),     ## [N*m/(rad*s)]
        "Riemen-Daempfung"       : params_best_estimate["Riemen-Daempfung"],           ## [N*m/rad]
        "Riemen-Steifigkeit"     : params_best_estimate["Riemen-Steifigkeit"],      ## [N*m/rad]
        "Getriebe-Wirkungsgrad"  : df_apso_DimRed['Getriebe-Wirkungsgrad'].loc['mean'].copy(),     ## [-]
        "Getriebe-Uebersetzung"  : df_apso_DimRed['Getriebe-Uebersetzung'].loc['mean'].copy(),     ## [-]
        "Leitspindel-Steigung"   : df_apso_DimRed['Leitspindel-Steigung'].loc['mean'].copy(),     ## [m]
        "Motor-Trägheitsmoment"  : df_apso_DimRed['Motor-Trägheitsmoment'].loc['mean'].copy()      ## [kg*m²]
    }
    new_estimates_optimized_names = ["KGT-Trägheitsmoment", "Reibung-viskos",
                                     "Getriebe-Wirkungsgrad", "Getriebe-Uebersetzung", "Leitspindel-Steigung",
                                     "Motor-Trägheitsmoment"]
    x_lower_bounds = []
    x_upper_bounds = []
    deviation_optimized_values = 0.01
    deviation_unoptimized_values = 0.05
    for key, value in new_estimates.items():
        if key in new_estimates_optimized_names:
            x_lower_bounds.append(value * (1 - deviation_optimized_values))
            if key == "Getriebe-Wirkungsgrad" and value * (1 + deviation_optimized_values) > 1:
                x_upper_bounds.append(1)
            else:
                x_upper_bounds.append(value * (1 + deviation_optimized_values))
        else:
            x_lower_bounds.append(value * (1 - deviation_unoptimized_values))
            x_upper_bounds.append(value * (1 + deviation_unoptimized_values))
    with open("myLog", "w") as mylogfile:
        mylogfile.write("new lower bounds:" + str(x_lower_bounds))
        mylogfile.write("new upper bounds:" + str(x_upper_bounds))
    x_ref = create_x_sim_ref(FALL_17_VARS, eng, c)
    new_referenceDrive(FALL_17_VARS, x_lower_bounds, x_upper_bounds, eng, n_gen, n_pop, x_ref)
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

def create_x_sim_ref(case, eng, c):
    eng.assignin('base', 'c', c, nargout=0)
    # Für finalerAnsatz_A gibt es in der Realität keine Unterscheidung zwischen den Referenz-Modelle da die gleiche
    # Referenzfahrt verwendet werden. In finalerAnsatz_B wird dieser Abschnitt tatsächlich witig sein.
    if case == FALL_7_VARS:
        eng.assignin('base', 'start_position', matlab.double(-200), nargout=0)
        eng.sim("xAchse_Sim_GR_GA_nR_SpezSeg3_17V")
    elif case == FALL_17_VARS:
        eng.assignin('base', 'start_position', matlab.double(-200), nargout=0)
        eng.sim("xAchse_Sim_GR_GA_nR_SpezSeg3_17V")
    xSimRef = np.array(eng.workspace['x_Sim'])
    xSimRefArray = xSimRef.reshape(1, xSimRef.size)
    return xSimRefArray

if __name__=='__main__':
    main()
