from datetime import datetime
import customtkinter as ctk
from tkcalendar import DateEntry


def define_attributes():
    attributs = [
        "Numéro de projet", "Numéro de commande", "Ligne", "Release", "Fournisseur", "Date de la réception matériel",
        "Date d'obtention de la doc", "Description", "Item code", "Statut", "Commentaires", "Consultant",
        "Origine de la doc",
    ]
    # Attributes to be treated as dates
    date_attributes = {
        "Date de la réception matériel", "Date d'obtention de la doc"
    }

    # Map the interface attribute names to the database column names
    column_mapping = {
        "Numéro de projet": "NUMERO_PROJET",
        "Numéro de commande": "NUMERO_COMMANDE",
        "Ligne": "LIGNE",
        "Release": "RELEASE",
        "Fournisseur": "FOURNISSEUR",
        "Date de la réception matériel": "DATE_RECEPTION_MATERIEL",
        "Date d'obtention de la doc": "DATE_OBTENTION_DOC",
        "Description": "DESCRIPTION",
        "Item code": "ITEM_CODE",
        "Statut": "STATUT",
        "Commentaires": "COMMENTAIRES",
        "Consultant": "CONSULTANT",
        "Origine de la doc": "ORIGINE_DOC",
    }

    return attributs, date_attributes, column_mapping


class EditView(ctk.CTkToplevel):
    def __init__(self, controller, id_projet, valeurs, view_name):
        super().__init__()
        self.entries = None
        self.view_name = view_name
        self.controller = controller
        self.id_projet = id_projet
        self.title('Modification document')

        # Initialise attributes and column mapping
        self.attributs, self.date_attributes, self.column_mapping = define_attributes()

        self.initialize_interface(valeurs)

    def initialize_interface(self, values):
        """
        Initializes the user interface with dynamic form fields based on provided attributes and values

        :param values: A list of values corresponding to the attributes defined in `define_attributes`
        """

        # Dictionary to hold the entry widgets associated with attributes
        self.entries = {}

        statut_options = [
            "En cours",  # for null value
            "En attente de retour interne",
            "Contrôle validé par la cellule doc",
            "Ligne Marine OPEN",
            "En attente d'inspection",
            "En attente de retour fournisseur",
            "Ligne Invalidable"
        ]

        # Loop over each attribute and its corresponding value
        for i, (attribut, valeur) in enumerate(zip(self.attributs, values)):
            # Create and place a label for each attribute
            ctk.CTkLabel(self, text=attribut).grid(row=i, column=0, sticky='e', padx=10, pady=5)
            if attribut == "Statut":
                entry = ctk.CTkComboBox(self, values=statut_options, width=250)
                # Management of null value
                entry.set(valeur if valeur is not None else "En cours")
            # Determine if this attribute should have a date entry
            elif attribut in self.date_attributes:
                # Specific date entry for date attributes
                entry = DateEntry(self, date_pattern='dd/mm/yyyy')
            else:
                # Regular text entry for other attributes
                entry = ctk.CTkEntry(self)

            # Configure the entry with the provided initial value
            self.configurer_entry(entry, valeur)
            entry.grid(row=i, column=1, sticky='ew', padx=10, pady=5)

            # Store the entry widget in the dictionary with its attribute as the key
            self.entries[attribut] = entry

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)

        # Add buttons (e.g., save, cancel) at the end of the form
        self.add_buttons(len(self.attributs))

    def configurer_entry(self, entry, valeur):
        """
        Configures an entry widget based on its type. If the widget is a DateEntry, it converts
        the string to a date and sets it. For regular entry widgets, it inserts the string value
        directly, assuming the value is valid and not a placeholder 'None'.

        :param entry: The entry widget to be configured. This could be either a DateEntry for dates
                      or a regular entry widget for text
        :param valeur: The string value to set in the entry widget. Expected to be either a date
                       string for DateEntry widgets or any text for regular entries
        """

        # Check if the entry widget is an instance of DateEntry
        if isinstance(entry, DateEntry):
            date_obj = self.convert_str_to_date(valeur)
            if date_obj:
                # Set the converted date in the DateEntry widget
                entry.set_date(date_obj)
            else:
                entry.delete(0, 'end')

        elif isinstance(entry, ctk.CTkComboBox):
            if valeur == "Contrôle validé par le système":
                # Disable the CTkComboBox and set the value
                entry.set(valeur)
                entry.configure(state='disabled')
            else:
                # Enable the CTkComboBox, set the value, and ensure it is editable
                entry.configure(state='normal')
                # Use 'set' for comboboxes if value is not None, otherwise select "None"
                entry.set(valeur if valeur is not None else "En cours")

        elif valeur and valeur != 'None':
            entry.insert(0, valeur)

    def add_buttons(self, count):
        """
        Adds control buttons to the interface. This includes a "Save" button to commit changes
        and a "Cancel" button to close the form without saving changes

        :param count: The number of rows already used in the grid layout, used to determine where to place the buttons
        """

        # Add a "Save" button that calls the `save_modification` method when clicked
        (ctk.CTkButton(self, text="Sauvegarder", command=self.save_modification).
         grid(row=count + 1, column=0, padx=10, pady=10))

        # Add a "Cancel" button that calls the `destroy` method when clicked, which closes the current window
        (ctk.CTkButton(self, text="Annuler", command=self.destroy).
         grid(row=count + 1, column=1, padx=10, pady=10))

    def save_modification(self):
        """
        Collects modified values from the form entries and updates the corresponding record in the database.
        After updating, it refreshes the table display and closes the modification form
        """

        # Dictionary to store new values fetched from the form entries
        new_values = {}
        horodatage_map = {
            "Contrôle validé par la cellule doc": "HOROD_CONTROLE_VALIDE_CELLULE_DOC",
            "En attente de retour fournisseur": "HOROD_ATTENTE_RETOUR_FOURNISSEUR",
            "En attente de retour interne": "HOROD_ATTENTE_RETOUR_INTERNE",
            "Ligne Invalidable": "HOROD_LIGNE_INVALIDABLE"
        }

        for attribut, entry in self.entries.items():
            db_column = self.column_mapping[attribut]
            # Check if the entry widget is specifically for date input
            if isinstance(entry, DateEntry):
                # If it's a DateEntry widget, fetch the date as a datetime.date object
                new_values[db_column] = entry.get_date() if entry.get() else None

            elif isinstance(entry, ctk.CTkComboBox) and attribut == "Statut":
                # Get the status value from the drop-down list
                statut = entry.get()
                new_values[db_column] = statut

                # If the status corresponds to a key in timestamp_map, update the corresponding timestamp
                if statut in horodatage_map:
                    colonne_horodatage = horodatage_map[statut]
                    new_values[colonne_horodatage] = datetime.now().date()

            else:
                # For other types of entry widgets, fetch the text value
                new_values[db_column] = entry.get() if entry.get() != '' else None

        # Call the controller method to update the document data in the database using the collected new values
        self.controller.modify_data(self.id_projet, new_values)

        # Refresh the table in the main GUI to reflect the updated data
        self.controller.refresh_table(self.view_name)

        # Close the current modification window
        self.destroy()

    @staticmethod
    def convert_str_to_date(value, date_format="%Y-%m-%d"):
        """
        Converts a string in the format 'YYYY-MM-DD' to a datetime.date object

        :param date_format: Desired date format
        :param value: The string to be converted to a date
        :return: datetime.date: The corresponding date object if conversion is successful; None otherwise
        """

        # Check if the input is None or explicitly the string 'None'
        if value is not None and value != 'None':
            try:
                # Attempt to convert the string to a date object
                return datetime.strptime(value, date_format).date()
            except ValueError as e:
                # Handle the case where the date format is incorrect
                print(f"Erreur lors de la conversion de la date: {e}")
                return None
        else:
            # Return None if the input is None or 'None'
            return None
