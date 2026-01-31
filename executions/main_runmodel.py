import time
from tqdm import tqdm
import functions.logicanalyzer as LogicAnalyzer
import functions.estlcam as Estlcam
import functions.general as General

# ----
# MAIN: STARTEN VON n-REFERENZFAHRTEN
# ----

# Abfahren von n Referenzfahrten, automatisiert hintereinander
# Hauptanzeige muss der Laptop sein (nicht der Bildschirm), da Estlcam über Position der Maus gesteigert wird

##############################################################
# EINGABEN:

# Anzahl der Referenzfahrten:
n = 1

# Dauer einer einzelnen Referenzfahrt (für die Datenaufnahme):
dauer = 150

# Benutzte Teile:
motor = 'Servomotor'
getriebe = 'Zahnriemen'
G_code_path = "../G-Code/Mit_Drehzahlanpassung/doppelsinusF8746_A1_5_f1_2_A2_2_F2_8.nc"

# Mailadresse:
mailadress = 'schmiedt.christi.a23@student.dhbw-karlsruhe.de'
EMAIL_ACTIVE = False
##############################################################
# g_code in Datei kopieren
ausgefuehrter_g_code_pfad = r"C:\Users\proki\Desktop\Referenzfahrt_1&5\WirdAusgeführt.nc"
with open(G_code_path, "r") as src, open(ausgefuehrter_g_code_pfad, "w") as dst:
    dst.write(src.read())

# Öffnen von Logic2 & Estlcam
prozess_Logic2 = LogicAnalyzer.startLogic2()
prozess_Estlcam = Estlcam.openEstlcam()
Estlcam.openReferenceRun()

# Mail beim Start senden
if EMAIL_ACTIVE:
    General.sendMail(recieveradress=mailadress, iteration=0, numberofdrives=n)



# durch Anzahl der Referenzfahrten iterieren
for i in range(1, n + 1):
    print("--- Start Referenzfahrt " + str(i) + "/" + str(n) + ":\t" + motor + " - " + getriebe)
    # Start der Datenaufnahme und der Referenzfahrt
    LogicAnalyzer.recordData_Logic2(dauer=dauer, motor=motor, getriebe=getriebe)
    print("\t.... Referenzfahrt " + str(i) + "/" + str(n) + " done")
    # Mail senden
    if i % 5 == 0 and i != n:
        if EMAIL_ACTIVE:
            General.sendMail(recieveradress=mailadress, iteration=i, numberofdrives=n)
        print('\n--- Pause: 90s')
        for j in tqdm(range(1, 91)):
            time.sleep(1)
        print('\n')
    # Mail senden nach Abschluss
    if i == n and EMAIL_ACTIVE:
        General.sendMail(recieveradress=mailadress, iteration=i, numberofdrives=n)
    # Pause zum Abkühlen von Motor & Spindel
    if n > 1:
        time.sleep(10)


print("\nReferenzfahrten (" + str(n) + ") erfolgreich abgeschlossen. ---")
# Schließen von Logic2 & Estlcam
prozess_Estlcam.terminate()
prozess_Logic2.terminate()
