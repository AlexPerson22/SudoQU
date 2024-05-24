import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime
from Views.EditView import define_attributes


class AddView(ctk.CTkToplevel):
    def __init__(self, controller, view_name):
        super().__init__()
        self.entries = None
        self.controller = controller
        self.view_name = view_name
        self.title('Ajouter un nouveau document')

        # Initialise attributes and column mapping
        self.attributs, self.date_attributes, self.column_mapping = define_attributes()

        # Define which fields are mandatory
        self.required_fields = ["Numéro de projet", "Numéro de commande", "Ligne", "Release"]

        self.initialize_interface()

    def initialize_interface(self):
        """
        Initializes the user interface with dynamic form fields based on defined attributes. This method sets up the UI
        components dynamically based on the attributes specified for the instance of the class
        """

        # Dictionary to store references to the entry widgets
        self.entries = {}

        # List of possible status options for a status attribute
        statut_options = [
            "En cours",
            "En attente de retour interne",
            "Contrôle validé par la cellule doc",
            "Ligne Marine OPEN",
            "En attente d'inspection",
            "En attente de retour fournisseur",
            "Ligne Invalidable"
        ]

        # Loop through each attribute defined in `self.attributs`
        for i, attribut in enumerate(self.attributs):
            # Create a label for each attribute and place it in a grid
            ctk.CTkLabel(self, text=attribut).grid(row=i, column=0, sticky='e', padx=10, pady=5)

            # Conditional creation of entry widgets based on attribute type
            if attribut == "Statut":
                # Create a ComboBox for selecting status, pre-populate with options
                entry = ctk.CTkComboBox(self, values=statut_options, width=250)
                # Set the default value of the ComboBox
                entry.set("En cours")
            elif attribut in self.date_attributes:
                # Initialize the DateEntry without setting a date
                entry = DateEntry(self, date_pattern='dd/mm/yyyy')
                # Make sure the DateEntry is blank upon initialization
                entry.delete(0, 'end')
            else:
                # Create a standard entry widget for all other attributes
                entry = ctk.CTkEntry(self)

            # Place the entry widget in the grid
            entry.grid(row=i, column=1, sticky='ew', padx=10, pady=5)
            # Store the entry widget in the dictionary for later access
            self.entries[attribut] = entry

        # Configure column sizes for the grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)

        # Add buttons or other controls based on the number of attributes
        self.add_buttons(len(self.attributs))

    def add_buttons(self, count):
        """
        Adds control buttons to the user interface

        :param count: The number of attributes to determine the row position for the buttons
        """

        # Saving data entered in the form
        ctk.CTkButton(self, text="Ajouter", command=self.add_documentation).grid(row=count + 1, column=0, padx=10, pady=10)

        # Cancelling the operation and closing the form
        ctk.CTkButton(self, text="Annuler", command=self.destroy).grid(row=count + 1, column=1, padx=10, pady=10)

    def add_documentation(self):
        """
        Collects values from the form entries and adds a new record to the database after validating required fields
        """

        # Dictionary to store values entered by the user
        new_values = {}
        # Mapping of specific statuses to their corresponding timestamp columns in the database
        horodatage_map = {
            "Contrôle validé par la cellule doc": "HOROD_CONTROLE_VALIDE_CELLULE_DOC",
            "En attente de retour fournisseur": "HOROD_ATTENTE_RETOUR_FOURNISSEUR",
            "En attente de retour interne": "HOROD_ATTENTE_RETOUR_INTERNE",
            "Ligne Invalidable": "HOROD_LIGNE_INVALIDABLE"
        }
        # Boolean to check the validity of all required fields
        all_fields_valid = True
        # Error message for storing field validation errors
        error_message = ""

        # Browse each input attribute-widget pair in the self.entries dictionary
        for attribut, entry in self.entries.items():
            # Retrieves the name of the database column for the attribute
            db_column = self.column_mapping[attribut]

            # Retrieving the value according to widget type
            if isinstance(entry, DateEntry):
                # Date selected or None if empty
                value = entry.get_date() if entry.get() else None
            elif isinstance(entry, ctk.CTkComboBox):
                value = entry.get()
                if attribut == "Statut":
                    new_values[db_column] = value
                    # If the status corresponds to a key in timestamp_map, update the corresponding timestamp
                    if value in horodatage_map:
                        colonne_horodatage = horodatage_map[value]
                        new_values[colonne_horodatage] = datetime.now().date()
            else:
                value = entry.get() if entry.get() != '' else None

            new_values[db_column] = value

            # Check if the field is required and the value is None or empty
            if attribut in self.required_fields and (value is None or value == ''):
                all_fields_valid = False
                error_message += f"{attribut} est obligatoire\n"

        if all_fields_valid:
            # Only proceed to add data if all required fields are valid
            self.controller.add_data(new_values)
            self.controller.refresh_table(self.view_name)
            self.destroy()
        else:
            messagebox.showerror("Erreur de validation",
                                 "Certains champs obligatoires sont manquants ou incomplets :\n" + error_message)
            # Re-populate the form with the entered data for corrections
            self.repopulate_form(new_values)

    def repopulate_form(self, values):
        """
        Repopulates the form fields with previously entered data after validation failure

        :param values: Dictionary containing values to repopulate the form with, keyed by database column names
        """

        # Scrolls through each input widget associated with an attribute
        for attribut, entry in self.entries.items():
            # Name of the database column for the attribute
            db_column = self.column_mapping[attribut]
            # Retrieves the value to be repositioned in the form
            value = values.get(db_column)

            # Specific widget type management for data reconstitution
            if isinstance(entry, DateEntry):
                # If this is a date entry and a value is available, set it
                if value:
                    entry.set_date(value)
                else:
                    # Otherwise, delete the current contents of the entry
                    entry.delete(0, 'end')
            elif isinstance(entry, ctk.CTkComboBox):
                # For a ComboBox, define the value or leave blank if no value is provided
                entry.set(value if value is not None else "")
            else:
                # For text entries, delete the content first
                entry.delete(0, 'end')
                # If a value is available, put it back in the text entry
                if value is not None:
                    entry.insert(0, value)
