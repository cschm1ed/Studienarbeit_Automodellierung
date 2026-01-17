import os
import platform

class Config:

    ##########
    # Lokaler Pfad:
    if platform.system() == "Windows":
        BASE_PATH = r'C:\Users\proki\Desktop\Oktober25_DHBW\Neuer Ordner'
    else:
        BASE_PATH = rf'{os.environ["HOME"]}/Documents/Studienarbeit/Studienarbeit_Code'
    # Google Colab Pfad:
    #BASE_PATH = r'/content/drive/MyDrive/Colab/Masterarbeit_Schubert'
    ##########


    # Strings für Pfade

    STR_raw_data = r'raw_data_sorted'
    STR_data_alt = r'#alt'
    STR_data_fertig = r'#fertig'
    STR_data_machine_learning = r'#machine_learning'

    STR_servo_raeder = r"#_servo_zahnräder"
    STR_servo_riemen = r"#_servo_zahnriemen"
    STR_schritt_raeder = r"#_schritt_zahnräder"
    STR_schritt_riemen = r"#_schritt_zahnriemen"

    STR_KNN = r'KNN'
    STR_RF  = r'RF'
    STR_Testdaten = r'Testdaten'
    STR_Trainingsdaten = r'Trainingsdaten'


    # Zusammensetzung der Pfade
    PATH_estlcam_exe =r'C:\Users\proki\Downloads\MA MS\MA MS\Orga MA MS\05 Sonstige Dokumente\Estlcam11\Estlcam.exe'
    PATH_logic2_exe = r'C:\Program Files\Logic\Logic.exe'

    PATH_raw_data = os.path.join(BASE_PATH, STR_raw_data)
    PATH_data_alt = os.path.join(PATH_raw_data, STR_data_alt)
    PATH_data_fertig = os.path.join(PATH_raw_data, STR_data_fertig)
    PATH_data_machine_learning = os.path.join(PATH_raw_data, STR_data_machine_learning)

    PATH_servo_raeder = os.path.join(PATH_data_fertig, STR_servo_raeder)
    PATH_servo_riemen = os.path.join(PATH_data_fertig, STR_servo_riemen)
    PATH_schritt_raeder = os.path.join(PATH_data_fertig, STR_schritt_raeder)
    PATH_schritt_riemen = os.path.join(PATH_data_fertig, STR_schritt_riemen)

    PATH_KNN = os.path.join(PATH_data_machine_learning, STR_KNN)
    PATH_RF = os.path.join(PATH_data_machine_learning, STR_RF)
    PATH_Testdaten = os.path.join(PATH_data_machine_learning, STR_Testdaten)
    PATH_Trainingsdaten = os.path.join(PATH_data_machine_learning, STR_Trainingsdaten)











