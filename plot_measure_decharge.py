import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Charger le fichier CSV
file_path = "data/decharge_20dBmTx_330mf.csv"
df = pd.read_csv(file_path, skiprows=3, names=["Index", "Voltage"])

# Convertir les valeurs de tension en float
df["Voltage"] = pd.to_numeric(df["Voltage"], errors="coerce")

# Supprimer les valeurs NaN éventuelles
df = df.dropna()

# Identifier l'indice où la tension chute brutalement
diff_voltage = np.diff(df["Voltage"])  # Calcul des variations de tension
chute_index = np.argmin(diff_voltage)  # Trouver l'indice où la chute est la plus forte

# Identifier l'indice où la tension atteint son minimum après la chute
min_voltage_index = df["Voltage"].idxmin()

# Calculer le temps de décharge (en ms, car chaque point est pris toutes les 1 ms)
temps_decharge_ms = (min_voltage_index - chute_index) * 1  # 1 ms par point

print(f"Temps de décharge du supercondensateur : {temps_decharge_ms} ms")

# Tracer la courbe de décharge
plt.figure(figsize=(10, 5))
plt.plot(df["Index"], df["Voltage"], label="Tension au borne du supercondensateur")
plt.axvline(chute_index, color='r', linestyle='--', label="Début de la chute")
plt.axvline(min_voltage_index, color='g', linestyle='--', label="Tension minimale")
plt.xlabel("Temps (ms)")
plt.ylabel("Tension (V)")
plt.legend()
plt.title("Courbe de décharge du supercondensateur")
plt.show()