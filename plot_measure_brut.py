import matplotlib.pyplot as plt
import pandas as pd

# Fonction pour lire un fichier CSV et extraire l'intervalle d'échantillonnage
def read_csv(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        # Trouver la ligne où apparaît "Sample interval"
        for line in lines:
            if line.startswith("Sample interval:"):
                # Le sample interval est après la virgule
                sample_interval = float(line.strip().split(',')[1])
                print(sample_interval)
                break
        else:
            raise ValueError("Sample interval not found in file!")
    
    data = pd.read_csv(file_path, skiprows=2)
    # Calcul du temps en heure selon l'intervalle extrait automatiquement
    data["Time (hour)"] = data["Reading #"] * sample_interval / 3600
    # Voltage
    data["Voltage (V)"] = data["Reading"]
    return data

# Chemins des fichiers CSV
file_paths = [
    # "LpL_SF12/reseau_14dBm_330m_255cm_placo.csv",
    "LpL_SF8/reseau_20dBm_330m_255cm_placo.csv"
    # "LpL_SF12/reseau_16dBm_330m_255cm_placo.csv",
    # "LpL_SF12/reseau_18dBm_330m_255cm_placo.csv",
    # "LpL_SF12/reseau_20dBm_330m_255cm_placo.csv"
]

# Liste pour stocker toutes les données
all_data = []

# Lire les données et générer un graphique pour chaque fichier
for file_path in file_paths:
    data = read_csv(file_path)
    all_data.append((file_path, data))  # Stocker les données pour le graphe combiné

# Créer un graphique combiné avec toutes les courbes
plt.figure(figsize=(12, 6))
for file_path, data in all_data:
    file_name = file_path.split("/")[-1]
    plt.plot(data["Time (hour)"], data["Voltage (V)"], label=file_name)

plt.title("Combined: Time vs Voltage for All Files")
plt.xlabel("Time (hour)")
plt.ylabel("Voltage (V)")
plt.grid(True)
plt.legend()
plt.show()
