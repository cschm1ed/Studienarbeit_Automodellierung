import os.path
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def daten_eigenschaften():
    eigenschaften_columns = ["Fahrt", "Abtastpunkte Strom", "Abtastpunkte Position", "Dauer Strom", "Dauer Position",
                             "Abtastpunkte pro Sek Strom", "Abtastpunkte pro sek Position"]
    eigenschaften_rows = []
    for folder in folders:
        folder = Path(folder)
        position = pd.read_csv(folder / filename_position)
        current = pd.read_csv(folder / filename_current)

        num_abtastpunkte_current = len(current)
        num_abtastpunkte_position = len(position)

        duration_current = current["time_[s]"].iloc[-1] - current["time_[s]"].iloc[0]
        duration_position = position["time_[s]"].iloc[-1] - position["time_[s]"].iloc[0]

        abtastpunkte_pro_sek_current = num_abtastpunkte_current / duration_current
        abtastpunkte_pro_sek_position = num_abtastpunkte_position / duration_position

        eigenschaften_rows.append({"Fahrt": folder.name,
                                   "Abtastpunkte Strom": num_abtastpunkte_current,
                                   "Abtastpunkte Position": num_abtastpunkte_position,
                                   "Dauer Strom": duration_current,
                                   "Dauer Position": duration_position,
                                   "Abtastpunkte pro sek Strom": abtastpunkte_pro_sek_current,
                                   "Abtastpunkte pro sek Position": abtastpunkte_pro_sek_position})
    eigenschaften_df = pd.DataFrame(eigenschaften_rows)
    if "Abgeschnitten" in filename_current:
        eigenschaften_df.to_csv("untersuchung_AnfangAbgeschnitten.csv")
    else:
        eigenschaften_df.to_csv("untersuchung.csv")


def daten_vor_startpunkt_loeschen():
    global index
    for folder in folders:
        folder = Path(folder)
        position = pd.read_csv(folder / filename_position)
        current = pd.read_csv(folder / filename_current)

        ## columns: 'time_[s]', 'current_[mA]' / 'position_[mm]'

        starttime = 0
        for index, row in position.iterrows():
            if abs(row["position_[mm]"]) > 0.015:
                starttime = row["time_[s]"]
                break

        current = current[current["time_[s]"] >= starttime]
        position = position[position["time_[s]"] >= starttime]
        position = position.reset_index(drop=True)
        current = current.reset_index(drop=True)

        fig, axs = plt.subplots(2, 1, figsize=(12, 8), layout="constrained")
        axs[0].plot(position["time_[s]"], position["position_[mm]"], color="blue")
        axs[0].set(xlabel="Time (s)", ylabel="Position (mm)", title="Position")
        axs[1].plot(current["time_[s]"], current["current_[mA]"], color="red")
        axs[1].set(xlabel="Time (s)", ylabel="Current (mA)", title="Current")
        axs[1].grid(True)
        axs[0].grid(True)
        plt.savefig(folder / "AnfangAbgeschnitten.png")

        current.to_csv(folder / "currentAnfangAbgeschnitten.csv", index=False)
        position.to_csv(folder / "positionAnfangAbgeschnitten.csv", index=False)



def daten_visualisieren():
    for folder in folders:
        folder = Path(folder)
        current = pd.read_csv(folder / filename_current)
        position = pd.read_csv(folder / filename_position)

        fig, axs = plt.subplots(2, 1, figsize=(10, 6), sharex=True, layout="constrained")
        fig.suptitle(folder.name)
        axs[0].plot(position["time_[s]"], position["position_[mm]"], color='b')
        axs[0].set(xlabel='Time [s]', ylabel='Position [mm]', title='Position')
        axs[1].plot(current["time_[s]"], current["current_[mA]"], color='r')
        axs[1].set(xlabel='Time [s]', ylabel='Current [mA]', title='Current')
        plt.savefig(folder / (folder.name + "_rohdaten.png"))


folders = [
    r'.\Motoroffset\2026-01-31_13-00-21_motoroffset_bestimmen',
    r'.\Motoroffset\2026-01-31_14-42-30',
    r'.\Motoroffset\2026-01-31_14-48-46',
    r'.\Motoroffset\2026-01-31_14-55-41',
    r'.\Motoroffset\2026-01-31_15-04-14'
]
#------------------Datenverarbeitung--------------------

filename_current = "current.csv"
filename_position = "position.csv"
daten_visualisieren()
daten_eigenschaften()
daten_vor_startpunkt_loeschen()
filename_current = "currentAnfangAbgeschnitten.csv"
filename_position = "positionAnfangAbgeschnitten.csv"
daten_eigenschaften()