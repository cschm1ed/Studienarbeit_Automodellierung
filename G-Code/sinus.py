## Code zum Erstellen einer Referenzfahrt mit doppelter Sinus-Trajektorie

import numpy as np

# --- Parameter ---
A1, f1 = 5.0, 1.0
A2, f2 = 2.0, 5.0
dt = 0.01
T  = 5.0

# optional: Offset, damit du nicht um 0 herum fährst (falls du das nicht willst)
x_offset = 500  # mm

# optional: Begrenzung Nachkommastellen für CNC
decimals = 3

# --- Trajektorie ---
t = np.arange(0.0, T + 0.5*dt, dt)
x = (A1*np.sin(2*np.pi*f1*t) + A2*np.sin(2*np.pi*f2*t)) + x_offset

# --- Geschwindigkeit -> Vorschubabschätzung ---
v = np.gradient(x, dt)           # mm/s
F_required = np.max(np.abs(v)) * 50.0  # mm/min

# Sicherheitsfaktor (z.B. 10% Reserve)
F_set = 1.1 * F_required

print(f"Empfohlener G-Code Vorschub F ~ {F_set:.1f} mm/min")

# --- G-Code schreiben ---
outfile = "doppelsinus.nc"
with open(outfile, "w", encoding="utf-8") as f:
    f.write("\n")

    # optional: Start anfahren
    f.write(f"G1 X{round(x[0], decimals):.{decimals}f}\n")



    f.write("M09\n")

    # Trajektorie
    for xi in x[1:]:
        f.write(f"G1 X{round(xi, decimals):.{decimals}f} F{round(F_set)}\n")

    f.write("M08\n")

print(f"G-Code gespeichert: {outfile}")