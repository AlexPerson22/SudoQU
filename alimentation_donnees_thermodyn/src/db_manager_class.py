import numpy as np
from sqlalchemy import create_engine, MetaData, Table, update
from sqlalchemy.orm import sessionmaker
import pandas as pd
pd.options.mode.copy_on_write = True
import os
from datetime import datetime
import logging
from src.lists_initialisation import (histo_perfo_column_to_delete, full_backlog_data_column_for_ID,
                                      navy_check_column_for_ID, full_backlog_data_column_to_delete,
                                      navy_check_column_to_delete, histo_perfo_column_for_ID)


class DatabaseManager:
    def __init__(self, dbname, user, password, host):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.conn_string = f"postgresql+psycopg://{user}:{password}@{host}/{dbname}"
        self.engine = create_engine(self.conn_string)
        self.metadata = MetaData()

        # Create a directory for log files if it doesn't already exist
        log_directory = "./logs"
        if not os.path.exists(log_directory):
            os.makedirs(f'{log_directory}/INFO')
            os.makedirs(f'{log_directory}/ERROR')

        # Current date for naming log files
        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Logger configuration
        self.logger = logging.getLogger('DataManager')
        self.logger.setLevel(logging.DEBUG)  # Niveau le plus bas capté par le logger

        # Logger configuration
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Log file for INFO
        info_file_handler = logging.FileHandler(f'{log_directory}/INFO/info_{current_date}.log')
        info_file_handler.setLevel(logging.INFO)
        info_file_handler.setFormatter(formatter)
        self.logger.addHandler(info_file_handler)

        # Log file for ERROR
        error_file_handler = logging.FileHandler(f'{log_directory}/ERROR/error_{current_date}.log')
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(formatter)
        self.logger.addHandler(error_file_handler)

    def dataframe_to_sql(self, dataframe, table_name):
        """
        Transfers data from a Pandas DataFrame to a specified PostgreSQL table

        :param dataframe: The DataFrame containing the data to be transferred
        :param table_name: Le nom de la table de la base de données PostgreSQL où les données doivent être transférées
        """

        try:
            # Attempts to transfer DataFrame data to the specified PostgreSQL table
            # 'index=False' indicates not to include the DataFrame index as a column in the table
            # 'if_exists='append'' adds the data to the table if it already exists, without deleting existing data
            dataframe.to_sql(table_name, self.engine, index=False, if_exists='append')

            self.logger.info(f"The data has been successfully transferred to the {table_name} table")
        except Exception as e:
            self.logger.error(f"An error occurred during data transfer: {e}")

    def select_from_table(self, table_name):
        """
        Selects rows from a specified PostgreSQL table and returns them as pandas DataFrame

        :param table_name: The name of the PostgreSQL table from which to select data

        :return: pandas.DataFrame: A DataFrame containing selected rows from the specified table
        """

        # Creates a `Table` instance for the specified table, using the database engine and metadata
        table = Table(table_name, self.metadata, autoload_with=self.engine)

        # Prepares an SQLAlchemy session to interact with the database
        session_maker = sessionmaker(bind=self.engine)
        session = session_maker()
        try:
            # Creates a selection query for the table specified via the session
            query = session.query(table)

            # Executes the query and converts the result into DataFrame pandas
            result = pd.read_sql(query.statement, self.engine)
            return result
        except Exception as e:
            self.logger.error(f"An error occurred during data selection: {e}")
        finally:
            # Closes the session to release resources
            session.close()
            self.logger.info("The data has been successfully retrieved and transformed into a Dataframe from the "
                             "database")

    def formatting_dataframe(self, df, df_type):
        """
        Formats a DataFrame according to the extraction source

        :param df: The DataFrame to be formatted
        :param df_type: The extraction type, which determines the specific formatting to be applied
        :return: pandas.DataFrame: DataFrame formatted and filtered according to the specified type
        """

        # Initialization of the final filtered dataframe
        df_filtered = pd.DataFrame()

        # Specific formatting according to extraction type
        match df_type:
            case "histo_perfo":
                # Drop useless columns
                df.drop(histo_perfo_column_to_delete, axis=1, inplace=True)
                # Delete null value for the PO_NUMBER column
                df.dropna(subset=histo_perfo_column_for_ID[0], inplace=True)
                # Create ID
                df['ID'] = (df[histo_perfo_column_for_ID[0]].astype(int).astype(str) +
                            df[histo_perfo_column_for_ID[1]].astype(int).astype(str) +
                            df[histo_perfo_column_for_ID[2]].astype(str) +
                            df[histo_perfo_column_for_ID[3]].astype(str))

                # Rename columns
                df.rename(columns={'PO_NUMBER': 'NUMERO_COMMANDE', 'PO_LINE_NUMBER': 'LIGNE',
                                   'RELEASE_NUMBER': 'RELEASE', 'PO_JOB': 'NUMERO_PROJET',
                                   'CURR_PO_SUPPLIER': 'FOURNISSEUR', 'PO_LINE_DESCRIPTION': 'DESCRIPTION',
                                   'FIRST_MAT_DELIVERY_DATE': 'DATE_RECEPTION_MATERIEL',
                                   'FIRST_ISP': 'DATE_OBTENTION_DOC'}, inplace=True)

                df['LAST_EDM_MANAGEMENT_DATE'] = pd.to_datetime(df['LAST_EDM_MANAGEMENT_DATE'])
                date_limite = pd.Timestamp.now() - pd.Timedelta(days=14)

                # Apply a filter to select specific lines based on 'CURRENT_STATUS' and 'LAST_EDM_MANAGEMENT_DATE'
                df_current_status_filter = df[df['CURRENT_STATUS'].isin(['In Approval']) | df['CURRENT_STATUS'].isna()]

                df_approved_filter = df[df['CURRENT_STATUS'].isin(['APPROVED'])]
                df_on_approved_filter_with_date = df_approved_filter[
                    df_approved_filter['LAST_EDM_MANAGEMENT_DATE'] >= date_limite]

                # Concatenation of the two filtered dataframes
                df_filtered = pd.concat([df_current_status_filter, df_on_approved_filter_with_date], ignore_index=True)

                # Add new column with today's date for lines where CURRENT_STATUS is 'APPROVED'
                current_date = pd.Timestamp.now().normalize().strftime('%Y-%m-%d')
                df_filtered['HOROD_CONTROLE_VALIDE_SYSTEME'] = np.where(df_filtered['CURRENT_STATUS'] == 'APPROVED',
                                                                        current_date, None)

                # Drop final useless columns
                df_filtered.drop(['CURRENT_STATUS', 'LAST_EDM_MANAGEMENT_DATE'],
                                 axis=1, inplace=True)

            case "full_backlog_data":
                # Drop useless columns
                df.drop(full_backlog_data_column_to_delete, axis=1, inplace=True)
                # Delete null value for the PO column
                df.dropna(subset=full_backlog_data_column_for_ID[0], inplace=True)
                # Create ID
                df['ID'] = (df[full_backlog_data_column_for_ID[0]].astype(int).astype(str) +
                            df[full_backlog_data_column_for_ID[1]].astype(int).astype(str) +
                            df[full_backlog_data_column_for_ID[2]].astype(str) +
                            df[full_backlog_data_column_for_ID[3]].astype(str))

                # Rename columns
                df.rename(columns={'PO': 'NUMERO_COMMANDE', 'LINE': 'LIGNE',
                                   'PROJECT_NUM': 'NUMERO_PROJET', 'VENDOR_NAME': 'FOURNISSEUR',
                                   'ACTUAL_MAT_DELIVERY_DATE': 'DATE_RECEPTION_MATERIEL'}, inplace=True)

                # Application of a filter based on 'DATE_RECEPTION_MATERIEL'
                df_filtered_reception_materiel = df[df['DATE_RECEPTION_MATERIEL'].notna()]

                # Retrieves data from the database
                df_db = self.select_from_table("documents")

                # Filter the dataframes based on the ID column
                unique_rows = df_filtered_reception_materiel[~df_filtered_reception_materiel['ID'].isin(df_db['ID'])]

                # Add the current date to the 'HOROD_ATTENTE_DOC' column for the filtered rows
                current_date = pd.Timestamp.now().normalize().strftime('%Y-%m-%d')
                unique_rows['HOROD_ATTENTE_DOC'] = current_date

                # Identify common lines (present in both DataFrames)
                common_rows = df_filtered_reception_materiel[df_filtered_reception_materiel['ID'].isin(df_db['ID'])]

                # Concatenate unique_rows and common_rows
                df_filtered = pd.concat([unique_rows, common_rows], ignore_index=True)

            case "navy_check":
                # Drop useless columns
                df.drop(navy_check_column_to_delete, axis=1, inplace=True)
                # Delete null value for the PO column
                df.dropna(subset=navy_check_column_for_ID[0], inplace=True)
                # Create ID
                df['ID'] = (df[navy_check_column_for_ID[0]].astype(int).astype(str) +
                            df[navy_check_column_for_ID[1]].astype(int).astype(str) +
                            df[navy_check_column_for_ID[2]].astype(str) +
                            df[navy_check_column_for_ID[3]].astype(str))

                df['MAX_RECEIVING_DATE'] = pd.to_datetime(df['MAX_RECEIVING_DATE'], format='%d/%m/%Y')
                df['MAX_RECEIVING_DATE'] = df['MAX_RECEIVING_DATE'].dt.strftime('%Y-%m-%d')

                # Rename columns
                df.rename(columns={'PO': 'NUMERO_COMMANDE', 'LINE_NUM': 'LIGNE', 'RELEASE_NUM': 'RELEASE',
                                   'DIST_PROJECT': 'NUMERO_PROJET', 'CURR_VENDOR_NAME': 'FOURNISSEUR',
                                   'MAX_RECEIVING_DATE': 'DATE_RECEPTION_MATERIEL'}, inplace=True)

                # Application of filters based on 'FIRST_PO_APPROVED_DATE' and 'PO_REL_LINE_FIRST_APPRO_DATE'
                df_filtered = df[df['FIRST_PO_APPROVED_DATE'].notna() & df['PO_REL_LINE_FIRST_APPRO_DATE'].notna()]

                # Drop final useless columns
                df_filtered.drop(['FIRST_PO_APPROVED_DATE', 'PO_REL_LINE_FIRST_APPRO_DATE'], axis=1,
                                 inplace=True)

        # Delete duplicate IDs, keeping the first occurrence
        df_filtered.drop_duplicates(subset=['ID'], keep='first', inplace=True)

        return df_filtered

    def concatenated_dataframes(self, df_excel, table_name):
        """
        Merges a DataFrame from Excel with data from a database table, then saves the result in this database table

        :param df_excel: The DataFrame loaded from an Excel file
        :param table_name: The name of the database table with which to merge the data and where to save the result
        """

        # Selects data from the specified table in the database and stores it in df_result
        df_result = self.select_from_table(table_name)

        # Concatenate the two DataFrames df_excel and df_result
        # Filter rows, keeping only those with an 'ID' not present in df_result
        df_concatenated = pd.concat([df_excel, df_result])[
            ~pd.concat([df_excel, df_result])['ID'].isin(df_result['ID'])]

        # Date conversion to avoid type issues
        df_concatenated['DATE_RECEPTION_MATERIEL'] = pd.to_datetime(df_concatenated['DATE_RECEPTION_MATERIEL'])
        df_concatenated['DATE_OBTENTION_DOC'] = pd.to_datetime(df_concatenated['HOROD_CONTROLE_VALIDE_SYSTEME'])
        df_concatenated['HOROD_CONTROLE_VALIDE_SYSTEME'] = pd.to_datetime(
            df_concatenated['HOROD_CONTROLE_VALIDE_SYSTEME'])
        df_concatenated['HOROD_CONTROLE_VALIDE_CELLULE_DOC'] = pd.to_datetime(
            df_concatenated['HOROD_CONTROLE_VALIDE_CELLULE_DOC'])
        df_concatenated['HOROD_ATTENTE_RETOUR_FOURNISSEUR'] = pd.to_datetime(
            df_concatenated['HOROD_ATTENTE_RETOUR_FOURNISSEUR'])
        df_concatenated['HOROD_ATTENTE_DOC'] = pd.to_datetime(df_concatenated['HOROD_ATTENTE_DOC'])
        df_concatenated['HOROD_ATTENTE_RETOUR_INTERNE'] = pd.to_datetime(
            df_concatenated['HOROD_ATTENTE_RETOUR_INTERNE'])
        df_concatenated['HOROD_LIGNE_INVALIDABLE'] = pd.to_datetime(df_concatenated['HOROD_LIGNE_INVALIDABLE'])

        self.logger.info("The two dataframes have been concatenated")

        # Saves the merged DataFrame in the specified database table
        self.dataframe_to_sql(df_concatenated, table_name)

    def update_database_from_dataframe(self, dataframe, table_name):
        """
        Update existing rows in a PostgreSQL table from a pandas DataFrame

        :param dataframe: The DataFrame containing the data to be used for updating
        :param table_name: The name of the table in the database to be updated
        """

        # Creates a `Table` instance for the specified table, using the database engine and metadata
        table = Table(table_name, self.metadata, autoload_with=self.engine)

        # Prepares an SQLAlchemy session to interact with the database
        session_maker = sessionmaker(bind=self.engine)
        session = session_maker()
        try:
            # Iteration on each line of the DataFrame to update line by line
            for index, row in dataframe.iterrows():
                # Replaces NaN or NaT values with None to avoid errors when inserting into the database
                clean_row = row.where(pd.notnull(row), None)

                # Build the SQL update statement for the current row
                # This statement checks the row ID in the table and updates the corresponding columns
                stmt = (
                    update(table).
                    where(table.c.ID == clean_row['ID']).
                    values({column: clean_row[column] for column in dataframe.columns if column in table.c})
                )
                # Execute the update instruction for the current line
                session.execute(stmt)

            # Applies all changes made in this session to the database
            session.commit()
            self.logger.info(f"The existing data has been successfully updated in the {table_name} table")
        except Exception as e:
            # In the event of an error, cancels all modifications made during this session
            session.rollback()
            self.logger.error(f"An error occurred while updating the data: {e}")
        finally:
            # Closes the session to release resources
            session.close()
