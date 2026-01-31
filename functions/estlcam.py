import subprocess
import pyautogui
import time
import pygetwindow as gw
from pyautogui import click

from configurations.config import Config


# ----
# FUNKTIONEN ZUR STEUERUNG VON ESTLCAM
# ----


# ACHTUNG:
# evtl. müssen die Positionierbefehle (x & y) neu definiert werden
# Code ist auf einen 13 Zoll großen Laptop ausgelegt

MOUSE_MOVEMENT_DURATION = 0.5

# Funktion zum Öffnen von Estlcam & des CNC-Controller:
def openEstlcam():
    # Pfad der Estlcam.exe Datei
    exe_datei_pfad = Config.PATH_estlcam_exe
    # Die ausführbare Datei öffnen
    prozess = subprocess.Popen([exe_datei_pfad])
    # Starten der Mausbewegung:
    time.sleep(5)
    # Einstellung öffnen
    pyautogui.moveTo(440,80,MOUSE_MOVEMENT_DURATION)
    pyautogui.click(440, 80)
    # CNC Steuerung öffnen
    pyautogui.moveTo(440, 210, MOUSE_MOVEMENT_DURATION)
    pyautogui.click(440, 210)
    time.sleep(3)
    # Fenster in richtige Position verschieben
    ##########

    aktives_fenster = gw.getActiveWindow()
    aktives_fenster.moveTo(0, 0)

    ##############
    #
   # pyautogui.moveTo(260,270,3)
   # pyautogui.click(260, 270)
   # time.sleep(3)

    #############
    #Steuerung programmieren
    pyautogui.moveTo(438,805,MOUSE_MOVEMENT_DURATION)
    pyautogui.click(438, 805)
    time.sleep(7)
    # Fenster maximieren
    aktives_fenster = gw.getActiveWindow()
    aktives_fenster.maximize()
    print('Funktion "openEstlcam" abgeschlossen. ---')
    return prozess


# Funktion zum Laden der Referenzfahrt:
def openReferenceRun():
    time.sleep(3)
    aktives_fenster = gw.getActiveWindow()
    fenstertitel = aktives_fenster.title
    if fenstertitel == "Estlcam 11,245_A_64":
        time.sleep(2)
        pyautogui.moveTo(3100, 1000, MOUSE_MOVEMENT_DURATION)
        pyautogui.click(3100, 1000)
        time.sleep(19)
        pyautogui.moveTo(3135,148,MOUSE_MOVEMENT_DURATION)
        pyautogui.click(3135, 148)
        time.sleep(3)
       ### pyautogui.moveTo(497, 488, 2)
       ## pyautogui.click(497, 488)
       # time.sleep(3)
        # Fenster in richtige Position verschieben
       # aktives_fenster = gw.getActiveWindow()
       # aktives_fenster.moveTo(0, 0)
       # time.sleep(3)
        ### C3 CNC auswählen


        pyautogui.moveTo(487, 429, MOUSE_MOVEMENT_DURATION)
        pyautogui.doubleClick(487, 429)
        #max: 432:419
        #Pilger5: 454:375
        #Pilger1: 487:429
        #488
        time.sleep(12)

        pyautogui.moveTo(2008, 1119, MOUSE_MOVEMENT_DURATION)
        pyautogui.click(2008, 1119)
       # pyautogui.click(1160, 660)
       # time.sleep(3)
        print('Funktion "openReferenceRun" abgeschlossen. ---')
    else:
        print("Fehler: CNC-Controller nicht richtig geöffnet. ---")


# Funktion zum Starten der Referenzfahrt:
def startReferenceRun():
    time.sleep(1)
    # run drücken
    pyautogui.moveTo(2547, 1781, MOUSE_MOVEMENT_DURATION)
    pyautogui.click(2547, 1781)
