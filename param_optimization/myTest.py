
import os
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog


folder = tk.filedialog.askdirectory(initialdir=os.getcwd())
if not folder:
    tk.messagebox.showinfo("Info", "--- Es wurde kein Pfad ausgewählt. ---")
    exit(0)

opt_results = []
param_histories = []
for i in [1, 2]:
    result_filename = f"apso_finalerAnsatz_A40_Fall_{i}.csv"
    try:
        opt_results.append(pd.read_csv(os.path.join(folder, result_filename)))
    except Exception as e:
        print(f"Beim lesen von {result_filename} ist ein Fehler aufgetreten")
        print(f"Error: {e}")
        exit(1)
    result_filename = f"parameter_historie_fall_{i}.csv"
    try:
        param_histories.append(pd.read_csv(os.path.join(folder, result_filename)))
    except Exception as e:
        print(f"Beim lesen von {result_filename} ist ein Fehler aufgetreten")
        print(f"Error: {e}")
        exit(1)

fitness = [[], []]
for i in [0, 1]:
    for column_name in opt_results[i].columns:
        if "Fitnessverlauf" in column_name:
            fitness[i].append(opt_results[i][column_name].iloc[0])


plt.plot(fitness[0], color="blue", label="Fitnessverlauf Fall 1")
plt.plot(fitness[1], color="red", label="Fitnessverlauf Fall 2")
plt.grid(True)
plt.show()




