import datetime
from tkinter import filedialog
import pandas as pd
from Model.Model import Session, Documents
from Model.ModelView import Thomas, Aurelie, Karen, Estelle, Elise, Elodie, Florent, Raphael, Null
from Views.EditView import EditView
from Views.MainView import MainView
from Views.AddView import AddView

views_dict = {
    "Tous les documents": Documents,
    "Aucun consultant affecté": Null,
    "THOMAS": Thomas,
    "AURELIE": Aurelie,
    "KAREN": Karen,
    "ESTELLE": Estelle,
    "ELISE": Elise,
    "ELODIE": Elodie,
    "FLORENT": Florent,
    "RAPHAEL": Raphael
}


class Controller:
    def __init__(self):
        self.edit_window = None
        self.add_window = None
        self.session = Session()
        self.window = MainView(views_dict.keys(), controller=self)
        self.items_id_map = {}
        self.initialize_data()

    def initialize_data(self):
        """
        This method retrieves data from all the documents in the database and displays them
        in a graphical table (window). Each document, except its ID, is displayed in the table.
        table, while the ID is used to maintain correspondence with the interface elements.
        """

        # Retrieve all records from the 'documents' table using the SQLAlchemy session
        data = self.session.query(Documents).all()

        # Extracts data from each document in preparation for insertion into the GUI
        # documents is a list of lists, where each sub-list contains the values of a document
        documents = [[getattr(p, col) for col in Documents.__table__.columns.keys()] for p in data]

        for document in documents:
            # Insertion of the project in the graphic table, omitting the ID from the displayed value
            item = self.window.table.insert('', 'end', values=document[1:])
            self.items_id_map[item] = document[0]

    def retrieve_project_id(self, item):
        """
        Retrieves a project ID from a GUI element reference

        :param item: The reference of the item for which the project ID is being searched

        :return: Returns the project ID associated with the given item. Returns None if the item is not found
        """

        # Use the dictionary's `get` method to return the ID associated with `item`
        # If `item` is not found in the dictionary, `get` will return None by default
        return self.items_id_map.get(item)

    def modify_data(self, doc_id, new_values):
        """
        Updates a project in the database with the values supplied in the dictionary

        :param doc_id: The identifier of the project to be updated, in string form
        :param new_values: A dictionary containing the names of the columns to be updated as keys,
                              and the new values for these columns as values
        """

        # Check parameter types to avoid type or format errors
        if not isinstance(str(doc_id), str) or not isinstance(new_values, dict):
            print("The `doc_id` and/or `new_values` parameters are invalid")
            return

        try:
            # Search for the Document object corresponding to the ID supplied
            document = self.session.query(Documents).filter_by(ID=str(doc_id)).first()
            if document:
                # document attributes updated with new dictionary values
                for key, value in new_values.items():
                    if hasattr(document, key):
                        setattr(document, key, value)
                    else:
                        print(f"Warning: The project has no '{key}' attribute")

                # Save changes to the database
                self.session.commit()
                print("The project has been successfully updated")
            else:
                print(f"Aucun projet trouvé avec l'ID {str(doc_id)}")
        except Exception as e:
            # Cancel changes in case of error
            self.session.rollback()
            print(f"Erreur lors de la mise à jour du projet : {e}")

    def add_data(self, new_values):
        """
        Adds a new project to the database using the values supplied in the dictionary, with a custom ID created by
        concatenating certain fields

        :param new_values: A dictionary containing the names of the columns as keys, and the values for these columns
        as values
        """

        # Checking the parameter type to avoid type or format errors
        if not isinstance(new_values, dict):
            print("Le paramètre `new_values` est invalide")
            return

        try:
            # Create a new instance of the Document object
            new_document = Documents()

            # Creation of personalised IDs from specific fields
            id_parts = []
            for field in ["NUMERO_COMMANDE", "LIGNE", "RELEASE", "NUMERO_PROJET"]:
                part = new_values.get(field, '')
                if part:  # Ensures that only non-empty fields are included
                    id_parts.append(str(part))

            custom_id = "".join(id_parts)
            if hasattr(new_document, 'ID'):
                new_document.ID = custom_id
            else:
                print("Avertissement : La classe Document n'a pas d'attribut 'ID'")

            # Assign values to the corresponding attributes in the document
            for key, value in new_values.items():
                if hasattr(new_document, key):
                    setattr(new_document, key, value)
                else:
                    print(f"Attention : La classe Document n'a pas d'attribut '{key}'")

            # Add the new instance to the session and save it in the database
            self.session.add(new_document)
            self.session.commit()
            print("Le nouveau projet a été ajouté avec succès, ID:", custom_id)
        except Exception as e:
            # Cancellation of changes in the event of an error
            self.session.rollback()
            print(f"Erreur lors de l'ajout du nouveau projet : {e}")

    def display_modification_form(self, doc_id, values, selected_view):
        """
        Displays a form window for modifying information on a specific document

        :param selected_view:
        :param doc_id: The identifier of the document to be modified, used to reference the specific document
        :param values: A dictionary containing the current values of the document's fields,
                    which will be used to pre-fill fields in the modification form
        """

        # Create a new instance of the edit_window,
        # The document identifier (`doc_id`) and the current values (`values`) to initialize the form fields.
        self.edit_window = EditView(self, doc_id, values, selected_view)

        # Activate modal mode for the editing window
        # This blocks interaction with the main window while the editing window is open
        self.edit_window.grab_set()

    def display_add_form(self, selected_view):
        """
        Displays a form window for adding a new document

        :param selected_view: The identifier of the view selected by the user, which determines the type of form to be
        displayed
        """

        # Create a new instance of the add window
        self.add_window = AddView(self, selected_view)

        # Activate modal mode for the adding window
        # This blocks interaction with the main window while the adding window is open
        self.add_window.grab_set()

    def refresh_table(self, view_name="Tous les documents", data=None):
        """
        Refreshes the data displayed in the user interface table. This method retrieves the latest data from the
        `documents` table in the database and updates the table display in the GUI interface

        :param view_name: Refresh the table with the view selected by the user
        :param data: This is the data to be searched for in the database
        """

        # Retrieves the view class corresponding to the given name
        view_class = views_dict[view_name]

        if data is None:
            # Query to obtain all entries in the `Documents` table in the database
            data = self.session.query(view_class).all()

        # Construction of a list of lists containing the field values for each document, ready for display
        documents = [[getattr(p, col) for col in view_class.__table__.columns.keys()] for p in data]

        # Update data display in the main window
        self.window.display_data(documents)

    def search_bar(self, filter_value, view_name="Tous les documents"):
        """
        Filters documents in the database according to the value supplied, which can be an order number or a project
        number. The function then updates the display with the filtered results.

        :param view_name: View selected by the user so that searches are based on the current view
        :param filter_value: The value used to filter the documents, either an order number (if numeric) or a project
        number (if alphanumeric)
        """

        # Retrieves the view class corresponding to the given name
        view_class = views_dict[view_name]

        # Initialize the basic query on the document table
        query = self.session.query(view_class)

        # Determines the type of filtering value and adjusts the query accordingly
        if filter_value.isdigit():
            # If the filter value is numeric, it is considered an order number
            query = query.filter(view_class.NUMERO_COMMANDE == int(filter_value))
        elif any(char.isdigit() for char in filter_value):
            # If the value is alphanumeric, it is considered a project number
            query = query.filter(view_class.NUMERO_PROJET.contains(filter_value))
        else:
            # If the value contains spaces or specific characters, consider it a supplier name
            query = query.filter(view_class.FOURNISSEUR.contains(filter_value))

        # Execute query and retrieve filtered results
        filtered_results = query.all()

        # Update user interface with filtered data
        self.refresh_table(view_name, filtered_results)

    def get_statut_values(self):
        """
        Retrieves and returns all unique values for the 'STATUS' field in the 'Documents' table.
        None' values are replaced with the default 'En cours' value

        :return: A list of strings containing the unique values for 'STATUS'
        """

        # Obtain all possible values for 'STATUT'
        unique_values = self.session.query(Documents.STATUT).distinct().all()

        # Extract values from the list of tuples, replacing None with a default value
        return [value[0] if value[0] is not None else "En cours" for value in unique_values]

    def filter_by_statut(self, filter_value, view_name="Tous les documents"):
        """
        Filters the data in the 'Documents' table according to the 'STATUS' value specified.
        The function returns a list of matching records

        :param filter_value: The 'STATUS' value used to filter the data
        :param view_name: The table or view to be queried. The default is the 'Documents' table
        """

        # Retrieves the view class corresponding to the given name
        view_class = views_dict[view_name]

        #  Filter data based on 'STATUT' according to the value specified.
        filtered_data = self.session.query(view_class).filter_by(STATUT=filter_value).all()

        # Refreshes the table displayed in the user interface according to the selected view and filtered status data
        self.refresh_table(view_name, filtered_data)

    def filter_by_date(self, date_column=None, status_condition=None, reverse_sort=False, days_limit=None,
                       filter_empty_date=None, view_name="Tous les documents"):
        """
        Filters and sorts documents based on several criteria including date columns and status conditions

        :param date_column: The column in the database to filter by date, if applicable
        :param status_condition: A status condition to further filter documents
        :param reverse_sort: Whether to sort the results in descending order
        :param days_limit: If specified, filters out documents older or newer than these many days from today
        :param filter_empty_date: If specified, filters records where the date column specified is empty
        :param view_name: The view or table in the database to query
        """

        # Retrieves the view class corresponding to the given name
        view_class = views_dict[view_name]

        # Set the current date
        today = datetime.date.today()

        # Initializes the query on the view class
        query = self.session.query(view_class)

        # Applies a status filter if a condition is specified
        if status_condition:
            query = query.filter_by(STATUT=status_condition)

        # Applies a filter based on the limit in days, if specified
        if days_limit is not None:
            # Calculation of the target date based on the limit of days
            target_date = today - datetime.timedelta(days=days_limit)

            # Creates a date filter based on reverse sorting or not
            date_filter = getattr(view_class, date_column) <= target_date if not reverse_sort else (
                    getattr(view_class, date_column) >= target_date)
            query = query.filter(date_filter)

        # Filter to exclude records with an empty date, if specified
        if filter_empty_date:
            # Filters out records where the specified column is null
            query = query.filter(getattr(view_class, filter_empty_date).is_(None))

        # Sorting by date if a date_column is specified for sorting
        if date_column:
            query = query.order_by(
                getattr(view_class, date_column).desc() if reverse_sort else getattr(view_class, date_column))

        # Executes the query and retrieves the filtered results
        results = query.all()

        # Refreshes the table with the results obtained
        self.refresh_table(view_name, results)

    def extract_data(self, view_name):
        """
        Retrieves data from the database according to the selected view

        :param view_name: The name of the view from which to extract the data
        """

        # Retrieves the view class corresponding to the given name
        view_class = views_dict[view_name]

        # Query to obtain all entries in the selected view in the database
        data = self.session.query(view_class).all()

        # Construction of a list of lists containing the field values for each document, ready for display
        documents = [[getattr(p, col) for col in view_class.__table__.columns.keys()] for p in data]

        df = pd.DataFrame(documents)

        # Open the dialog box to save the file
        filename = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[("CSV files", '*.csv')],
            title="Sauvegarder en tant que"
        )

        # Checks whether the user has cancelled the operation
        if filename:
            # Export data in CSV format (UTF8)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"Les données ont été exportées avec succès dans le fichier {filename}")
        else:
            print("Export annulé.")

    def run(self):
        """
        Launches the application's main event loop. This method must be called for the user interface to become
        interactive and respond to user actions. It keeps the application running and waits for the user to interact
        with the interface
        """

        # Starts the window's main event loop
        self.window.mainloop()
