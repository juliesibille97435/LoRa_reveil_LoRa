import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from glob import glob

SAVE_DIR = "save_data"
os.makedirs(SAVE_DIR, exist_ok=True)

def extract_power_level(file_path):
    basename = os.path.basename(file_path)
    match = re.search(r'_(\d+)dBm', basename)
    return int(match.group(1)) if match else None

def get_sample_interval(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            if line.lower().startswith("sample interval"):
                return float(line.strip().split(',')[1])
    raise ValueError(f"Sample interval not found in {file_path}")

def detect_large_drops(voltage, threshold=0.3):
    differences = np.diff(voltage)
    return np.where(differences < -threshold)[0]

def process_folder(folder_path, label):
    results = []
    file_paths = glob(os.path.join(folder_path, "*.csv"))
    print(file_paths)
    for file_path in file_paths:
        power_level = extract_power_level(file_path)
        sample_interval = get_sample_interval(file_path)
        with open(file_path, 'r') as f:
            for _ in range(3): next(f)
            data = pd.read_csv(f, names=["Reading #", "Reading"])
        data["Time (hour)"] = data["Reading #"] * sample_interval / 3600
        voltage = data["Reading"].astype(float).values

        drop_indices = detect_large_drops(voltage)
        nb_sequences = len(drop_indices)
        if nb_sequences < 1:
            print(f"Pas de chute détectée dans {file_path}")
            continue

        first_charge_time = data["Time (hour)"].iloc[drop_indices[0]]

        recharge_times = []
        for i in range(nb_sequences-1):
            drop = drop_indices[i]
            next_drop = drop_indices[i+1]
            segment = voltage[drop+1:next_drop]
            if len(segment) == 0: continue
            max_idx = np.argmax(segment)
            recharge_time = data["Time (hour)"].iloc[drop+1+max_idx] - data["Time (hour)"].iloc[drop]
            recharge_times.append(recharge_time * 60)  # minutes

        mean_recharge = np.mean(recharge_times) if recharge_times else np.nan
        std_recharge = np.std(recharge_times) if recharge_times else np.nan

        print(f"Fichier: {file_path}")
        print(f"  Puissance: {power_level} dBm")
        print(f"  Temps de première charge: {first_charge_time:.2f} h")
        print(f"  Temps de recharge moyen: {mean_recharge:.2f} min (écart-type: {std_recharge:.2f} min)")
        print(f"  Nombre de séquences: {nb_sequences}\n")

        results.append({
            "Puissance (dBm)": power_level,
            "Temps de charge (h)": first_charge_time,
            "Temps de recharge (min)": mean_recharge,
            "Ecart type (min)": std_recharge,
            "Nombre de séquences": nb_sequences
        })

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values("Puissance (dBm)")
    results_df.to_csv(f"{SAVE_DIR}/ChargeRechargeSummary_{label}.csv", index=False)

    print(f"\nTableau récapitulatif ({label}):")
    print(results_df)

    # Graphe 1 : Temps de première charge (h)
    plt.figure(figsize=(8,5))
    plt.plot(results_df["Puissance (dBm)"], results_df["Temps de charge (h)"], 's-', color='tab:orange')
    plt.xlabel("Puissance d'émission (dBm)")
    plt.ylabel("Temps de première charge (h)")
    plt.title(f"Temps de première charge vs puissance d'émission\n({label})")
    plt.grid()
    plt.savefig(f"{SAVE_DIR}/FirstCharge_vs_Power_{label}.png")
    plt.show()

    # Graphe 2 : Temps de recharge moyen (min) + barres d'erreur
    plt.figure(figsize=(8,5))
    plt.errorbar(
        results_df["Puissance (dBm)"],
        results_df["Temps de recharge (min)"],
        yerr=results_df["Ecart type (min)"],
        fmt='-o',
        color='tab:blue',
        ecolor='black',
        elinewidth=2,
        capsize=5
    )
    plt.xlabel("Puissance d'émission (dBm)")
    plt.ylabel("Temps de recharge moyen (min)")
    plt.title(f"Temps de recharge moyen vs puissance d'émission\n({label})")
    plt.grid()
    plt.savefig(f"{SAVE_DIR}/MeanRecharge_vs_Power_{label}.png")
    plt.show()

# Traite chaque dossier
process_folder("rectenna_unitaire", "Rectenna unitaire")
# process_folder("reseau_rectenna", "Réseau de rectenna")
