import unittest
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, String, Column, Integer, delete
from src import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.dbname = 'cellule_doc'
        self.user = 'user_connection'
        self.password = 'thermodyn'
        self.host = 'localhost'
        self.conn_string = f"postgresql+psycopg://{self.user}:{self.password}@{self.host}/{self.dbname}"

        # Initializing a DatabaseManager instance for tests
        self.db_manager = DatabaseManager(dbname=self.dbname, user=self.user, password=self.password, host=self.host)

        self.table_name = 'test'

        self.data = {'ID': ['43908910767110', '43908910741151'], 'CONSULTANT': ['Karen', 'Aurélie'],
                     'NUMERO_PROJET': ['SMP0390', '1PE0039'], 'NUMERO_COMMANDE': [439089107, 439089107],
                     'LIGNE': [67, 41], 'RELEASE': ['110', '151'], 'ORIGINE_DOC': ['ISP', 'Mail'],
                     'FOURNISSEUR': ['CORREGE 916115', 'H ZOBEL SAS'],
                     'DATE_RECEPTION_MATERIEL': ['2022-02-09', '2023-08-31'],
                     'DATE_OBTENTION_DOC': ['2021-02-11', '2023-07-15']}

        # Creating an SQLAlchemy engine for testing
        self.engine = create_engine(self.conn_string)
        self.metadata = MetaData()
        self.metadata.create_all(bind=self.engine)

    def tearDown(self):
        # Cleaning after tests
        with self.engine.connect() as connection:
            # Début d'une transaction
            with connection.begin() as transaction:
                try:
                    # Prépare et exécute la requête SQL pour supprimer tous les enregistrements de la table test
                    delete_query = sqlalchemy.text(f"DELETE FROM public.{self.table_name}")
                    connection.execute(delete_query)
                    # Validation de la transaction
                    transaction.commit()
                except Exception as e:
                    # En cas d'erreur, annulation de la transaction
                    transaction.rollback()
                    raise e
                finally:
                    transaction.close()

    def test_dataframe_to_sql(self):
        # Creating a DataFrame from the provided data
        df = pd.DataFrame(self.data)

        # Convert both date columns to datetime for df
        df['DATE_RECEPTION_MATERIEL'] = pd.to_datetime(df['DATE_RECEPTION_MATERIEL'])
        df['DATE_OBTENTION_DOC'] = pd.to_datetime(df['DATE_OBTENTION_DOC'])

        # Calling the 'dataframe_to_sql' method of the database manager to transfer DataFrame to SQL
        self.db_manager.dataframe_to_sql(df, self.table_name)

        # Checking if the data has been correctly added to the table
        result = self.db_manager.select_from_table(self.table_name)

        # Convert both date columns to datetime for result
        result['DATE_RECEPTION_MATERIEL'] = pd.to_datetime(result['DATE_RECEPTION_MATERIEL'])
        result['DATE_OBTENTION_DOC'] = pd.to_datetime(result['DATE_OBTENTION_DOC'])

        # Asserting if the number of rows is the same
        self.assertEqual(len(result), len(df))

        # Asserting if each column matches between result and the original DataFrame
        for col in df.columns:
            self.assertTrue(all(result[col] == df[col]), f"Column '{col}' is different")

    def test_select_from_table(self):
        # Creating a DataFrame from the provided data
        df = pd.DataFrame(self.data)

        # Convert both date columns to datetime for df
        df['DATE_RECEPTION_MATERIEL'] = pd.to_datetime(df['DATE_RECEPTION_MATERIEL'])
        df['DATE_OBTENTION_DOC'] = pd.to_datetime(df['DATE_OBTENTION_DOC'])

        # Adding data to the table for testing purposes
        df.to_sql(self.table_name, self.engine, index=False, if_exists='append')

        # Calling the 'select_from_table' method to retrieve data from the table
        result = self.db_manager.select_from_table(self.table_name)

        # Convert both date columns to datetime for result
        result['DATE_RECEPTION_MATERIEL'] = pd.to_datetime(result['DATE_RECEPTION_MATERIEL'])
        result['DATE_OBTENTION_DOC'] = pd.to_datetime(result['DATE_OBTENTION_DOC'])

        # Asserting if the number of rows is the same
        self.assertEqual(len(result), len(df))

        # Asserting if each column matches between result and the original DataFrame
        for col in df.columns:
            self.assertTrue(all(result[col] == df[col]), f"Column '{col}' is different")

    def test_concatenated_dataframes(self):
        # Sample data for DataFrame loaded from Excel
        df_excel_data = {'ID': ['43904538716391', '4390453872408'], 'CONSULTANT': ['Thomas', 'Estelle'],
                         'NUMERO_PROJET': ['1B60062', '-'], 'NUMERO_COMMANDE': [439080808, 439080815],
                         'LIGNE': [87, 34], 'RELEASE': ['456', '812'], 'ORIGINE_DOC': ['Mail', 'ISPO'],
                         'FOURNISSEUR': ['NUOVO PIGNONE SRL', 'CTA FRANCE SAS'],
                         'DATE_RECEPTION_MATERIEL': ['2025-07-23', '2020-09-30'],
                         'DATE_OBTENTION_DOC': ['2018-04-11', '2019-07-29']}
        df_excel = pd.DataFrame(df_excel_data)

        # Sample data for existing database table
        df_result = pd.DataFrame(self.data)

        # Reset index for both DataFrames
        df_excel.reset_index(drop=True, inplace=True)
        df_result.reset_index(drop=True, inplace=True)

        # Convert both date columns to datetime for df_excel and df_result
        df_excel['DATE_RECEPTION_MATERIEL'] = pd.to_datetime(df_excel['DATE_RECEPTION_MATERIEL'])
        df_excel['DATE_OBTENTION_DOC'] = pd.to_datetime(df_excel['DATE_OBTENTION_DOC'])

        df_result['DATE_RECEPTION_MATERIEL'] = pd.to_datetime(df_result['DATE_RECEPTION_MATERIEL'])
        df_result['DATE_OBTENTION_DOC'] = pd.to_datetime(df_result['DATE_OBTENTION_DOC'])

        # Create a sample table in memory database
        df_result.to_sql(self.table_name, self.engine, index=False, if_exists='append')

        # Call the method to be tested
        self.db_manager.concatenated_dataframes(df_excel, self.table_name)

        # Verify if the merged data is correctly saved in the database table
        df_merged = self.db_manager.select_from_table(self.table_name)
        df_merged['DATE_RECEPTION_MATERIEL'] = pd.to_datetime(df_merged['DATE_RECEPTION_MATERIEL'])
        df_merged['DATE_OBTENTION_DOC'] = pd.to_datetime(df_merged['DATE_OBTENTION_DOC'])

        expected_result = pd.concat([df_excel[~df_excel['ID'].isin(df_result['ID'])], df_result])
        expected_result['DATE_RECEPTION_MATERIEL'] = pd.to_datetime(expected_result['DATE_RECEPTION_MATERIEL'])
        expected_result['DATE_OBTENTION_DOC'] = pd.to_datetime(expected_result['DATE_OBTENTION_DOC'])

        pd.testing.assert_frame_equal(df_merged.sort_values('ID').reset_index(drop=True),
                                      expected_result.sort_values('ID').reset_index(drop=True))

    def test_update_database_from_dataframe(self):
        # Sample data for DataFrame loaded from Excel
        df_excel_data = {'ID': ['43904538716391', '43908910741151'], 'CONSULTANT': ['Thomas', 'Estelle'],
                         'NUMERO_PROJET': ['1B60062', '-'], 'NUMERO_COMMANDE': [439080808, 439080815],
                         'LIGNE': [87, 34], 'RELEASE': ['456', '812'], 'ORIGINE_DOC': ['Mail', 'ISPO'],
                         'FOURNISSEUR': ['NUOVO PIGNONE SRL', 'CTA FRANCE SAS'],
                         'DATE_RECEPTION_MATERIEL': ['2025-07-23', '2020-09-30'],
                         'DATE_OBTENTION_DOC': ['2018-04-11', '2019-07-29']}
        df_excel = pd.DataFrame(df_excel_data)

        # Sample data for existing database table
        df_result = pd.DataFrame(self.data)

        # Reset index for both DataFrames
        df_excel.reset_index(drop=True, inplace=True)
        df_result.reset_index(drop=True, inplace=True)

        # Convert both date columns to datetime for df_excel and df_result
        df_excel['DATE_RECEPTION_MATERIEL'] = pd.to_datetime(df_excel['DATE_RECEPTION_MATERIEL'])
        df_excel['DATE_OBTENTION_DOC'] = pd.to_datetime(df_excel['DATE_OBTENTION_DOC'])

        df_result['DATE_RECEPTION_MATERIEL'] = pd.to_datetime(df_result['DATE_RECEPTION_MATERIEL'])
        df_result['DATE_OBTENTION_DOC'] = pd.to_datetime(df_result['DATE_OBTENTION_DOC'])

        # Create a sample table in memory database
        df_result.to_sql(self.table_name, self.engine, index=False, if_exists='append')

        # Call the method to be tested
        self.db_manager.update_database_from_dataframe(df_excel, self.table_name)

        df_updated = self.db_manager.select_from_table(self.table_name)
        df_updated['DATE_RECEPTION_MATERIEL'] = pd.to_datetime(df_updated['DATE_RECEPTION_MATERIEL'])
        df_updated['DATE_OBTENTION_DOC'] = pd.to_datetime(df_updated['DATE_OBTENTION_DOC'])

        expected_result_data = {'ID': ['43908910767110', '43908910741151'], 'CONSULTANT': ['Karen', 'Estelle'],
                                'NUMERO_PROJET': ['SMP0390', '-'], 'NUMERO_COMMANDE': [439089107, 439080815],
                                'LIGNE': [67, 34], 'RELEASE': ['110', '812'], 'ORIGINE_DOC': ['ISP', 'ISPO'],
                                'FOURNISSEUR': ['CORREGE 916115', 'CTA FRANCE SAS'],
                                'DATE_RECEPTION_MATERIEL': ['2022-02-09', '2020-09-30'],
                                'DATE_OBTENTION_DOC': ['2021-02-11', '2019-07-29']}
        expected_result = pd.DataFrame(expected_result_data)
        expected_result['DATE_RECEPTION_MATERIEL'] = pd.to_datetime(expected_result['DATE_RECEPTION_MATERIEL'])
        expected_result['DATE_OBTENTION_DOC'] = pd.to_datetime(expected_result['DATE_OBTENTION_DOC'])

        pd.testing.assert_frame_equal(df_updated.sort_values('ID').reset_index(drop=True),
                                      expected_result.sort_values('ID').reset_index(drop=True))


if __name__ == '__main__':
    unittest.main()
