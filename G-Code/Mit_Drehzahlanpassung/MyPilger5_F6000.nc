; Pilger5
; Anfahren X200
; N80 G90     	 			#Wechsel zu absoluter Programmierung
; N85 G55					# ist ein G-Code, der oft für die Auswahl eines Werkzeuglängenoffsets verwendet wird.
; N95 G04 P10


; Pilger5
M09
G01 X900     F6000
G01 X950     F6000
G01 X750     F6000
G01 X1000    F6000


# G01 für Linearinterpolation
M08