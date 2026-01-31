import pandas as pd
import os

## To do Motorstrom offset definieren

MOTORKONSTANTE = 0.08  # Nm / A

folders = [
    r'./SammlungMessdaten/SammlunghigherSamplingRatedekodiert/2026-01-20_19-30-34SpezSeg3_highSampling',
    r'./SammlungMessdaten/SammlunghigherSamplingRatedekodiert/2026-01-20_19-33-13MyPilger5_highSampling'
]

filename_current = "currentAnfangAbgeschnitten.csv"
filename_position = "positionAnfangAbgeschnitten.csv"

for folder in folders:
    path_curr = os.path.join(folder, filename_current)
    path_pos = os.path.join(folder, filename_position)

    current_df = pd.read_csv(path_curr)
    position_df = pd.read_csv(path_pos)
    current_df = current_df.sort_values("time_[s]")
    position_df = position_df.sort_values("time_[s]")

    merged_df = pd.merge_asof(
        current_df,
        position_df,
        on="time_[s]",
        direction="nearest",
        suffixes=("", "_pos_original")
    )
    merged_df["torque_[Nm]"] = (merged_df["current_[mA]"] / 1000) * MOTORKONSTANTE
    final_df = merged_df[["time_[s]", "position_[mm]", "torque_[Nm]"]]

    output_path = os.path.join(folder, "matched_position_torque.csv")
    final_df.to_csv(output_path, index=False)