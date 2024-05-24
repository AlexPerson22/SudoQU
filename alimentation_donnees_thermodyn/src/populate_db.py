import pandas as pd
from src import DatabaseManager

# Database parameters
db_name = "cellule_doc"
db_user = "user_connection"
db_password = "thermodyn"
db_host = "localhost"

# Path to Excel file
extract_file_path = '/Users/edouardvieillard/Agap2/THERMODYN/data.xlsx'

db_manager = DatabaseManager(db_name, db_user, db_password, db_host)

# Read Excel file
df_excel = pd.read_excel(extract_file_path, header=0)
print("excel read")

# Rename columns to match those in the database
df_excel.rename(columns={'Clé': 'ID', 'Consultant': 'CONSULTANT', 'Numéro de projet': 'NUMERO_PROJET',
                         'Numéro de commande': 'NUMERO_COMMANDE', 'Numéro de Ligne': 'LIGNE', 'Release': 'RELEASE',
                         'Origine de la documentation': 'ORIGINE_DOC', 'Fournisseur': 'FOURNISSEUR',
                         'Date de réception matériel (format JJ/MM/AAAA)': 'DATE_RECEPTION_MATERIEL',
                         "Date d'obtention de la documentation (format JJ/MM/AAAA)": "DATE_OBTENTION_DOC",
                         'Date de fin de contrôle de la documentation (format JJ/MM/AAAA) - Automatique': 'HOROD_CONTROLE_VALIDE_SYSTEME',
                         'Date de fin de contrôle de la documentation (format JJ/MM/AAAA) - Cellule Doc': 'HOROD_CONTROLE_VALIDE_CELLULE_DOC',
                         'Date de relance fournisseur': 'HOROD_ATTENTE_RETOUR_FOURNISSEUR',
                         'Nature du contrôle': 'STATUT'}, inplace=True)

# Drop Horad colum
del df_excel['Horod']

# Drop duplicate and null values for the ID column
df_excel.dropna(subset=['ID'], inplace=True)
df_excel.drop_duplicates(subset=['ID'], keep='first', inplace=True)

# Normalization of the 'CONSULTANT' column
df_excel['CONSULTANT'] = (df_excel['CONSULTANT'].str.normalize('NFKD').str.encode('ascii', errors='ignore').
                          str.decode('utf-8').str.upper())

# df_excel['STATUT'] = df_excel['STATUT'].fillna("En cours")

# Put data into the PostgreSQL database
db_manager.dataframe_to_sql(df_excel, table_name='documents')

print("Données importées")
