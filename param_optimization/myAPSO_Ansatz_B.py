"""
@Name: apso_finalerAnsatz_B
@Autor: Yann Rutschke
@E-Mail: yann.rutschke@student.kit.edu
@Created: 31.08.2023
@Description: Use an apso which is parallelized over the population. The parameter vector is calculated in two time
              here: first the dimension reduction model is used. Then the results are used in the model with 17 para-
              meters. This program is using two different reference drive (Seg12 and spezSeg3).
"""


from myAPSO_Ansatz_B_Problem import *
import csv
import pandas as pd
import os

CASE_7_PARAMS = 1
CASE_17_PARAMS = 2

def new_referenceDrive(case, x_lower_bounds, x_upper_bounds, eng, n_gen, n_pop, algorithm):
    """
            Write the csv data file for the examined case. Here two case are present 1 with the model with dimension .
            reduction and one with the model with 17 parameters.

                Parameters
                ----------
                case : int
                    Defines which model is used.
                    case = 1 : Model dimension reduction with Seg12
                    case = 2 : Model 17 parameter with spezSeg3
                x_lower_bounds : double list
                    Defines lower bound of the parameter vector
                x_upper_bounds : double list
                    Defines upper bound of the parameter vector

                Returns
                -------
                void : a csv file is written

                See Also
                --------
                Examples
                --------
                #>>> new_referenceDrive(2)
                """
    #---------Berechnung von xSimRef-----------------

    c = matlab.double(vector=[100000, 1500000000, 1000, 100000, 100000000, 500, 250, 100000, 200000000, 0.00029, 0.076,
                              1, 200000, 0.98, 55/24, 0.02, 0.00451])
    eng.assignin('base', 'c', c, nargout=0)

    # Für finalerAnsatz_A gibt es in der Realität keine Unterscheidung zwischen den Referenz-Modelle da die gleiche
    # Referenzfahrt verwendet werden. In finalerAnsatz_B wird dieser Abschnitt tatsächlich witig sein.

    if case == CASE_7_PARAMS:
        eng.assignin('base', 'start_position', matlab.double(-150), nargout=0)
        eng.sim("xAchse_Sim_Pilger1_17V.slx")

    elif case == CASE_17_PARAMS:
        eng.assignin('base', 'start_position', matlab.double(-150), nargout=0)
        eng.sim("xAchse_Sim_Pilger5_7V")

    xSimRef = np.array(eng.workspace['x_Sim'])
    xSimRefArray = xSimRef.reshape(1, xSimRef.size)

    with open("apso_Pilger_100proz_finalerAnsatz_B40_Fall_{}.csv".format(case), "w", newline="") as file:
        writer = csv.writer(file, delimiter=",")
        titel = ["Variable1", "Variable2", "Variable3", "Variable4", "Variable5", "Variable6", "Variable7",
                 "beste Fitness", "Zeit"]

        if case == 2:
            titel = ["Variable1", "Variable2", "Variable3", "Variable4", "Variable5", "Variable6", "Variable7",
                     "Variable8", "Variable9", "Variable10", "Variable11", "Variable12", "Variable13", "Variable14",
                     "Variable15", "Variable16", "Variable17", "beste Fitness", "Zeit"]

        for i in range(1, n_gen + 1):  # Fitnessverlauf für Dataframe
            titel.append("Fitnessverlauf{}".format(i))

        writer.writerow(titel)

        i = 0
        while i < 10:
            MyProblem.static_n_pop = n_pop
            MyProblem.static_case = case
            MyProblem.static_xSimRefArray = xSimRefArray
            MyProblem.static_x_lower_bounds = x_lower_bounds
            MyProblem.static_x_upper_bounds = x_upper_bounds

            if case == CASE_7_PARAMS:
                MyProblem.static_n_var = 7
            else:
                MyProblem.static_n_var = 17

            optimization_result = minimize(problem=MyProblem(eng),
                           algorithm=algorithm,
                           termination=("n_gen", n_gen),
                           eliminate_duplicates=True,
                           verbose=True,
                           save_history=True)
            print('optimization result: ', optimization_result)
            print("Best solution found: \nX = %s\nF = %s" % (optimization_result.X, optimization_result.F))
            print("Time:", optimization_result.exec_time)

            val = [e.opt.get("F")[0] for e in optimization_result.history]
            data = np.append(optimization_result.X, optimization_result.F)
            data1 = np.append(data, optimization_result.exec_time)
            data2 = np.append(data1, val)
            writer.writerow(data2)
            i += 1


def main():
    #--------Speicherort der Simulink-Modelle-----------

    eng = matlab.engine.start_matlab()
    path = os.getcwd()   # Pfad für xAchse_Sim_GR_GA_17V.slx
    eng.addpath(path, nargout=0)

    #-----Problem Variables-----
    n_gen = 40      # Anzahl der Generationen
    n_pop = 50      # Populationsgröße
    algorithm = PSO(pop_size=n_pop, adaptive=True)

    #------Durchführe der Optimierung und Speichern in csv-Datei---------

    eng.eval("cp = parcluster('local');", nargout=0)
    eng.eval("cp.NumWorkers = 16;", nargout=0) # Set to your core count
    eng.parpool(eng.workspace['cp'], nargout=0)

    # Durchführen Versuch mit Dimensionsreduktion
    x_lower_bound= [(950+475+238) * 0, 0.0002755 * 0, 0.0722 * 0, 0.931, 0 * 0.95 * 55 / 24, 0.019 * 0, 0.0042845 * 0] #-100% Abweichung nur W.Grad auf 0.931
    x_upper_bound = [(1050+525+262) * 2, 0.0003045 * 2, 0.0798 * 2, 1, 2 * 1.05 * 55 / 24, 0.021 * 2, 0.0047355 * 2] #+100% Abweichung nur W.Grad auf 1

    new_referenceDrive(CASE_7_PARAMS, x_lower_bound, x_upper_bound, eng, n_gen, n_pop, algorithm)

    df_apso_dim_red = pd.read_csv("apso_Pilger_100proz_finalerAnsatz_B40_Fall_1.csv")
    df_apso_dim_red = df_apso_dim_red.drop(df_apso_dim_red.loc[:, 'beste Fitness':'Fitnessverlauf{}'.format(n_gen)].columns,
                                         axis=1)
    df_apso_dim_red.loc['mean'] = df_apso_dim_red.mean()

    # Berechnung der Massen
    staender_Masse = (1000 / (1000 + 500 + 250)) * df_apso_dim_red['Variable1'].loc['mean'].copy()
    spindelgehaeuse_Masse = (500 / (1000 + 500 + 250)) * (df_apso_dim_red['Variable1'].loc['mean'].copy())
    spindel_Masse = (250 / (1000 + 500 + 250)) * (df_apso_dim_red['Variable1'].loc['mean'].copy())
    kgt_traegheitsmoment = df_apso_dim_red['Variable2'].loc['mean'].copy()
    leitspindel_viskReib = df_apso_dim_red['Variable3'].loc['mean'].copy()
    getriebe_wirkungsgrad = df_apso_dim_red['Variable4'].loc['mean'].copy()
    getriebe_uebersetzung = df_apso_dim_red['Variable5'].loc['mean'].copy()
    spindelsteigung = df_apso_dim_red['Variable6'].loc['mean'].copy()
    motor_traegheitsmoment = df_apso_dim_red['Variable7'].loc['mean'].copy()

    getriebe_wirkungsgrad_U = getriebe_wirkungsgrad + (getriebe_wirkungsgrad * 0.01)
    if getriebe_wirkungsgrad_U > 1:
        getriebe_wirkungsgrad_U = 1

    # Neue Parametervektoren, Parameter aus Dimensionsreduktion Abw. 2%, restliche Abweichung 10%
    x_lower_bound = [100000 * 0, 1500000000 * 0, (staender_Masse - (staender_Masse * 0.02)), 100000 * 0, 100000000 * 0,
           (spindelgehaeuse_Masse - (spindelgehaeuse_Masse * 0.02)), (spindel_Masse - (spindel_Masse * 0.02)), 100000 * 0, 200000000 * 0,
           (kgt_traegheitsmoment - (kgt_traegheitsmoment * 0.02)), (leitspindel_viskReib - (leitspindel_viskReib * 0.02)), 1 * 0,
           200000 * 0, (getriebe_wirkungsgrad - (getriebe_wirkungsgrad * 0.02)),
           (getriebe_uebersetzung - (getriebe_uebersetzung * 0.02)), (spindelsteigung - (spindelsteigung * 0.02)),
           (motor_traegheitsmoment - (motor_traegheitsmoment * 0.02))]

    x_upper_bound = [100000 * 2, 1500000000 * 2, (staender_Masse + (staender_Masse * 0.05)), 100000 * 2, 100000000 * 2,
           (spindelgehaeuse_Masse + (spindelgehaeuse_Masse * 0.02)), (spindel_Masse + (spindel_Masse * 0.02)), 100000 * 2, 200000000 * 2,
           (kgt_traegheitsmoment + (kgt_traegheitsmoment * 0.02)), (leitspindel_viskReib + (leitspindel_viskReib * 0.02)), 1 * 2,
           200000 * 2 ,getriebe_wirkungsgrad_U,
           (getriebe_uebersetzung + (getriebe_uebersetzung * 0.02)), (spindelsteigung + (spindelsteigung * 0.02)),
           (motor_traegheitsmoment + (motor_traegheitsmoment * 0.02))]

    new_referenceDrive(CASE_17_PARAMS, x_lower_bound, x_upper_bound, eng, n_gen, n_pop, algorithm)
    eng.quit()

main()