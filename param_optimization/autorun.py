

import subprocess
import os
import shutil
from datetime import datetime


for i in range(5):
    # Execute another script and wait for completion
    subprocess.run(["python", "myAPSO_Ansatz_A_xReal.py"], check=True)

    # Create folder with timestamp
    folder_name = datetime.now().strftime(f"%Y-%m-%d_%H_%M_optimization_run_{i}")
    folder_name = os.path.join(os.getcwd(), "Datenaufbereitung", "ModbusMessung","ModbusMessung","2026-02-21_14-46-32_doppelsinus_A1_40_T_10", folder_name)
    os.makedirs(folder_name, exist_ok=True)

    # Move files to the new folder
    files_to_move = ["apso_finalerAnsatz_A40_Fall_1.csv", "apso_finalerAnsatz_A40_Fall_2.csv", "parameter_historie_fall_1.csv", "parameter_historie_fall_2.csv"]
    for f in files_to_move:
        if os.path.exists(f):
            shutil.move(f, os.path.join(folder_name, f))

    print(f"Files moved to {folder_name}")