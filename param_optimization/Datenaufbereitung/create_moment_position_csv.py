import pandas as pd
import matplotlib.pyplot as plt

MOTORKONSTANTE = 0.08 # Nm / A

folders = [
    r'./SammlungMessdaten/Sammlung_dekodiert/2026-01-15_18-04-31_Pilger1',
    r'./SammlungMessdaten/Sammlung_dekodiert/2026-01-15_18-17-41_SpezSeg3',
    r'./SammlungMessdaten/Sammlung_dekodiert/2026-01-15_18-24-16_SpezSeg3_2',
    r'./SammlungMessdaten/Sammlung_dekodiert/2026-01-15_18-26-24_SpezSeg3Schneller',
    r'./SammlungMessdaten/Sammlung_dekodiert/2026-01-15_18-28-26_SpezSeg3Schneller_2',
    r'./SammlungMessdaten/Sammlung_dekodiert/2026-01-15_18-34-22_MyPilger1',
    r'./SammlungMessdaten/Sammlung_dekodiert/2026-01-15_18-36-02_MyPilger1_2',
    r'./SammlungMessdaten/Sammlung_dekodiert/2026-01-15_19-05-55_MyPilger5',
    r'./SammlungMessdaten/Sammlung_dekodiert/2026-01-15_19-10-16_MyPilger1_F2500',
]

filename_current = "currentAnfangAbgeschnitten.csv"
filename_position = "positionAnfangAbgeschnitten.csv"

for folder in folders:
    columns = ["position_[mm]", "torque_[nM]"]
    current_df = pd.read_csv(folder + "/" + filename_current)
    position_df = pd.read_csv(folder + "/" + filename_position)

    i = 0
    position_array = []
    torque_array = []
    time_position =
    for index, column in current_df.iterrows():
        torque = column["current_[mA]"] * MOTORKONSTANTE
        while i < len(position_df["time_[s]"]) - 1 and position_df["time_[s]"].iloc[i] < column["time_[s]"] :
            i += 1

        position = position_df["position_[mm]"].iloc[i]
        position_array.append(position)
        torque_array.append(torque)
    position_torque_df = pd.DataFrame({"time_torque_[s]": , "time_position_[s]": , "position_[mm]": position_array, "torque_[Nm]": torque_array})

    fig, axs = plt.subplots(2, 1)

    axs[0].plot(position_torque_df["position_[mm]"])
    axs[0].set(ylabel="Position [mm]", xlabel="Abtastpunkte", title="Position", color="blue")
    axs[0].grid(True)
    axs[1].plot(position_torque_df["torque_[Nm]"])
    axs[1].set(ylabel="Torque [mN]", xlabel="Abtastpunkte", title="Torque", color="orange")
    axs[1].grid(True)

    plt.savefig(folder + "/" + "torque_position" + ".png")









