import pandas as pd
import time
import os
from src import DatabaseManager
pd.options.mode.copy_on_write = True

# Database parameters
db_name = "cellule_doc"
db_user = "user_connection"
db_password = "thermodyn"
db_host = "localhost"

start_time = time.time()

# Specify the path to the directory containing the files to be checked
folders_path = {
    'Histo': '/Users/edouardvieillard/Agap2/THERMODYN/Extracts/',
    'Backlog': '/Users/edouardvieillard/Agap2/THERMODYN/Extracts/',
    'Navy': '/Users/edouardvieillard/Agap2/THERMODYN/Extracts/',
}

# Initialiser la liste pour suivre les chemins complets des fichiers les plus récents
most_recent_files = []

# Parcourir chaque dossier et chaque clé
for key, folder in folders_path.items():
    most_recent_file = None
    most_recent_time = None

    # Assurer que le dossier existe et contient des fichiers
    if os.path.exists(folder):
        for nom_fichier in os.listdir(folder):
            if key in nom_fichier:  # Vérifier si la clé est dans le nom du fichier
                file_path = os.path.join(folder, nom_fichier)
                modification_time = os.path.getmtime(file_path)

                if most_recent_file is None or modification_time > most_recent_time:
                    most_recent_file = file_path
                    most_recent_time = modification_time

    # Ajouter le chemin du fichier le plus récent à la liste
    if most_recent_file:
        most_recent_files.append(most_recent_file)


# Create a DatabaseManager instance
db_manager = DatabaseManager(db_name, db_user, db_password, db_host)
table_name = "documents"

file_type = ['histo_perfo', 'full_backlog_data', 'navy_check']

for i in range(len(most_recent_files)):

    extraction_file_path = most_recent_files[i]

    df_excel = pd.read_excel(extraction_file_path, header=0)
    db_manager.logger.info(f"Loading file {most_recent_files[i]}")

    df_formatted = db_manager.formatting_dataframe(df_excel, file_type[i])
    db_manager.logger.info(f"The {most_recent_files[i]} file formatted")

    db_manager.concatenated_dataframes(df_formatted, table_name)

    db_manager.update_database_from_dataframe(df_formatted, table_name)

end_time = time.time()

# Timer
execution_time = end_time - start_time
db_manager.logger.info(f"Temps d'exécution: {execution_time} secondes")
