import os
import pandas as pd
import matplotlib.pyplot as plt
from configurations.config import Config

# ----
# FUNKTIONEN ZUR GRAFISCHEN AUSGABE (VERLÄUFE VON POSITION & STROM)
# ----


# Funktion zur Erstellung der matplotlib Figures (für Position + Stromstärke) & automatisches speichern
def createandsaveMatplotlibFigures():
    ordner_liste = [d for d in os.listdir(Config.PATH_data_fertig) if
                    os.path.isdir(os.path.join(Config.PATH_data_fertig, d))]

    for ordner in ordner_liste:
        verzeichnis = os.path.join(Config.PATH_data_fertig, ordner)
        ordner_liste_2 = [d for d in os.listdir(verzeichnis) if
                          os.path.isdir(os.path.join(verzeichnis, d))]
        print("Verzeichnis" + verzeichnis)
        print('\n--- ' + ordner + ':')
        for ordner_2 in ordner_liste_2:
            verzeichnis_2 = os.path.join(verzeichnis, ordner_2)
            dateinamen = ['current_diagramm.png', 'position_diagramm.png']
            for dateiname in dateinamen:
                pfad_zur_datei = os.path.join(verzeichnis_2, dateiname)
                print('--- ' + ordner + '\t' + ordner_2 + ':')
                if not os.path.isfile(pfad_zur_datei):
                    # Zugriff auf Daten der Messung
                    with open(os.path.join(verzeichnis_2, 'used_parts.txt'), 'r') as file:
                        lines = file.readlines()
                        txt_name_motor_list = lines[2].split(' ', 1)
                        txt_name_getriebe_list = lines[3].split(' ', 1)
                        txt_time = lines[6]
                        txt_name_motor = txt_name_motor_list[1]
                        txt_name_getriebe = txt_name_getriebe_list[1]
                    create_plot_file(ordner, txt_name_getriebe, txt_name_motor, txt_time, verzeichnis_2)
                    print(f'\t.... Figures von {pfad_zur_datei} erfolgreich gespeichert.')
                else:
                    print(f'\t.... Figures von {pfad_zur_datei} existieren bereits.')

    print('\n--- Für alle neuen Ordner in "#fertig" wurden die Figures erfolgreich gespeichert.')


def create_plot_file(ordner, txt_name_getriebe, txt_name_motor, txt_time, verzeichnis_2):
    # Festlegen der Grenzen der x- und y-Achse
    if "servo" in ordner:
        y_min_curr = 0
        y_max_curr = 2000
    elif "schritt" in ordner:
        y_min_curr = 0
        y_max_curr = 1500
    else:
        y_min_curr = 0
        y_max_curr = 1500
        print('\t--- Fehler.')
    x_min = -20
    x_max = 20
    y_min_pos = -500
    y_max_pos = 500
    # Diagramm für Positionsverlauf erstellen
    verzeichnis_position = os.path.join(verzeichnis_2, 'position.csv')
    df_position = pd.read_csv(verzeichnis_position)
    # Linienplot erstellen
    x_position = df_position['time_[s]']
    y_position = df_position['position_[mm]']
    plt.figure(figsize=(10, 8))
    plt.plot(x_position, y_position, linestyle='-', color='blue',
             label=txt_name_motor + txt_name_getriebe)
    # Feste Grenzen für die X- und Y-Achse setzen
    plt.xlim(x_min, x_max)
    plt.ylim(y_min_pos, y_max_pos)
    plt.title('Position:', loc='left', fontsize=16)
    plt.title(txt_time, loc='right', fontsize=16)
    plt.xlabel('Zeit [s]', fontsize=16)
    plt.ylabel('Position [mm]', fontsize=16)
    plt.grid(True)
    plt.legend(loc='upper left', fontsize=16)
    plt.savefig(os.path.join(verzeichnis_2, 'position_diagramm.png'))
    print(f"{verzeichnis_2}/position_diagramm.png gespeichert")
    # plt.show()
    # Diagramm für Stromstärkenverlauf erstellen
    verzeichnis_current = os.path.join(verzeichnis_2, 'current.csv')
    df_current = pd.read_csv(verzeichnis_current)
    # Linienplot erstellen
    x_current = df_current['time_[s]']
    y_current = df_current['current_[mA]']
    plt.figure(figsize=(10, 8))
    plt.plot(x_current, y_current, linestyle='-', color='red', label=txt_name_motor + txt_name_getriebe)
    # Feste Grenzen für die X- und Y-Achse setzen
    plt.xlim(x_min, x_max)
    # plt.ylim(y_min_curr, y_max_curr)
    plt.title('Current:', loc='left', fontsize=16)
    plt.title(txt_time, loc='right', fontsize=16)
    plt.xlabel('Zeit [s]', fontsize=16)
    plt.ylabel('Current [mA]', fontsize=16)
    plt.grid(True)
    plt.legend(loc='upper left', fontsize=16)
    plt.savefig(os.path.join(verzeichnis_2, 'current_diagramm.png'))
    print(f"{verzeichnis_2}/current_diagramm.png gespeichert")
    # plt.show()
