from tkinter import ttk
import customtkinter as ctk


class MainView(ctk.CTk):
    def __init__(self, view_names, controller=None):
        super().__init__()
        self.title('SudoQU')
        self.controller = controller
        self.geometry('1200x600')

        # External frame
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(side=ctk.TOP, fill='x')

        # Add a button to add a document
        self.add_button = ctk.CTkButton(top_frame, text="Ajouter un document", command=self.add_form,
                                        fg_color="#18B281", hover_color="#10725F")
        self.add_button.pack(side=ctk.LEFT, pady=10, padx=10)

        # Combobox for database views
        self.views_combobox = ctk.CTkComboBox(top_frame, command=self.on_view_selected, width=200)
        self.views_combobox.configure(values=list(view_names))
        if view_names:
            self.views_combobox.set(list(view_names)[0])
        self.views_combobox.pack(side=ctk.LEFT, padx=20)

        # Prio doc button
        self.prio_doc_button = ctk.CTkButton(top_frame, text="Priorité documentation",
                                             command=lambda: self.apply_prio_filter("prio_doc"),
                                             fg_color="#ff7c70", hover_color="#c94139")  # pastel red
        self.prio_doc_button.pack(side=ctk.LEFT, padx=50)

        # Prio relance button
        self.prio_relance_button = ctk.CTkButton(top_frame, text="Priorité relance",
                                                 command=lambda: self.apply_prio_filter("prio_relance"),
                                                 fg_color="#cbcd69", hover_color="#8c902e")  # pastel yellow
        self.prio_relance_button.pack(side=ctk.LEFT)

        # Search button
        self.search_button = ctk.CTkButton(top_frame, text="Rechercher", command=self.view_search_bar,
                                           fg_color="#18B281", hover_color="#10725F")  # pastel green
        self.search_button.pack(side=ctk.RIGHT, padx=10, pady=10)

        # Search bar
        self.filter_field = ctk.CTkEntry(top_frame)
        self.filter_field.pack(side=ctk.RIGHT)

        # Container for table and scrollbars
        table_conteneur = ctk.CTkFrame(self)
        table_conteneur.pack(expand=True, fill=ctk.BOTH)

        # Treeview table configuration
        columns_name = (
            "Numéro de projet", "Numéro de commande", "Ligne", "Release", "Fournisseur",
            "Date de la réception matériel", "Date d'obtention de la doc", "Description", "Item code", "Statut",
            "Commentaires", "Consultant", "Origine de la doc", "Date du contrôle validé par le système",
            "Date du contrôle validé par la cellule doc", "Date de l'attente de retour fournisseur",
            "Date de l'attente de la documentation", "Date de l'attente de retour interne", "Ligne invalidable",
            )

        self.table = ttk.Treeview(table_conteneur, columns=columns_name, show='headings')

        for col in columns_name:
            self.table.heading(col, text=col, anchor="center")
            self.table.column(col, width=225, anchor="center")

        # Creating and positioning the horizontal scrollbar
        scrollbar_horizontal = ctk.CTkScrollbar(table_conteneur, orientation="horizontal")
        scrollbar_horizontal.pack(side="bottom", fill="x")
        self.table.configure(xscrollcommand=scrollbar_horizontal.set)  # Link the scrollbar with the table view
        scrollbar_horizontal.configure(command=self.table.xview)  # Associate horizontal view

        # Creating and positioning the vertical scrollbar
        scrollbar_vertical = ctk.CTkScrollbar(table_conteneur, orientation="vertical")
        scrollbar_vertical.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=scrollbar_vertical.set)  # Link the scrollbar with the table view
        scrollbar_vertical.configure(command=self.table.yview)  # Associate vertical view

        self.table.pack(expand=True, fill='both')

        # Bind double-click on a table item to the on_item_selection method
        self.table.bind("<Double-1>", self.on_item_selection)

        # Panel for filtering controls
        control_panel = ctk.CTkFrame(self)
        control_panel.pack(side=ctk.TOP, fill=ctk.X)

        # Combobox for filtering
        self.filter_combobox = ctk.CTkComboBox(control_panel, values=self.controller.get_statut_values(), width=250)
        self.filter_combobox.pack(side=ctk.LEFT, padx=10, pady=10)

        # Button to apply the filter
        self.filter_status_button = ctk.CTkButton(control_panel, text="Statut", command=self.apply_status_filter,
                                                  fg_color="#18B281", hover_color="#10725F")  # pastel green
        self.filter_status_button.pack(side=ctk.LEFT, padx=10)

        # Data extraction button
        self.extract_data_button = ctk.CTkButton(control_panel, text="Extraire les données", command=self.export_data,
                                                 fg_color="#4A90E2", hover_color="#357ABD")  # pastel blue
        self.extract_data_button.pack(side=ctk.RIGHT, padx=10, pady=10)

    def export_data(self):
        """
        Extracts data from the database and displays it
        """

        # Retrieves the value selected in the 'filter_combobox' drop-down menu
        selected_view = self.views_combobox.get()

        # Calls the export_data method of the controller, passing the selected view name
        self.controller.extract_data(view_name=selected_view)

    def apply_prio_filter(self, prio_button):
        """
        Applies a priority filter based on the button clicked. The filter criteria are set depending on the button type

        :param prio_button: Identifier for the button that was clicked, determining the filter criteria
        """

        # Checks which priority button was pressed and applies a corresponding filter
        if prio_button == 'prio_doc':
            # Filters data by 'DATE_OBTENTION_DOC' within the last 7 days for documents in progress
            self.controller.filter_by_date(date_column="DATE_OBTENTION_DOC", status_condition="En cours",
                                           reverse_sort=False, days_limit=7, view_name=self.views_combobox.get())

        elif prio_button == 'prio_relance':
            # Filters data where 'DATE_OBTENTION_DOC' is empty and order by 'DATE_RECEPTION_MATERIEL'
            self.controller.filter_by_date(date_column="DATE_RECEPTION_MATERIEL",
                                           filter_empty_date="DATE_OBTENTION_DOC",
                                           status_condition="En attente de la documentation", reverse_sort=False,
                                           view_name=self.views_combobox.get())

    def apply_status_filter(self):
        """
        Filter data by status and selected view, then refresh the user interface
        """

        # Retrieves the value selected in the 'filter_combobox' drop-down menu
        filter_value = self.filter_combobox.get()

        # Retrieves the view currently selected in the 'views_combobox' drop-down menu
        selected_view = self.views_combobox.get()

        # Recovers data filtered by status
        self.controller.filter_by_statut(filter_value, selected_view)

    def on_item_selection(self, event):
        """
        Handles item selection in a table. Retrieves the selected item's project ID and data,
        then opens a modification form with these details

        :param event: The event object that triggered this method, containing details like which item was selected
        """

        # Get the first selected item assuming single selection mode
        selected_item = self.table.selection()[0]

        # Retrieves the view currently selected in the 'views_combobox' drop-down menu
        selected_view = self.views_combobox.get()

        # Retrieve the project ID associated with the selected item
        id_projet = self.controller.retrieve_project_id(selected_item)

        # Fetch the values associated with the selected item in the table
        values = list(self.table.item(selected_item, 'values'))
        desired_values = values[:13]

        # Open the modification form with the retrieved ID and values
        self.controller.display_modification_form(id_projet, desired_values, selected_view)

    def add_form(self):
        """
        Handles displaying a form for adding new records based on the selected view from a dropdown menu
        """

        # Retrieves the view currently selected in the 'views_combobox' drop-down menu
        selected_view = self.views_combobox.get()

        # Calls a controller method to display the add form corresponding to the selected view
        self.controller.display_add_form(selected_view)

    def on_view_selected(self, event=None):
        """
        This method is called when the user selects a view from the 'views_combobox' drop-down menu.
        It is used to refresh the contents of the table according to the view selected

        :param event: Optional parameter which can be used to receive details of the event which triggered this method
        """

        # Retrieves the view currently selected in the 'views_combobox' drop-down menu
        selected_view = self.views_combobox.get()

        # Refreshes the table displayed in the user interface according to the view selected
        self.controller.refresh_table(selected_view)

    def view_search_bar(self):
        """
        Fetches the user input from the search bar and passes it to the controller's search function when the user
        submits a search query by clicking on the search button
        """

        # Retrieve the value entered the search bar
        filter_value = self.filter_field.get()
        get_views = self.views_combobox.get()

        # Pass the retrieved value to the search_bar method of the controller
        self.controller.search_bar(filter_value, get_views)

    def display_data(self, data):
        """
        Clears the current data in the table and updates it with new data.

        :param data: A list of tuples or lists where each item contains the fields to be displayed in the table.
        """

        # Remove all existing entries from the table
        # This prevents duplication and ensures that the table reflects the current data state
        for i in self.table.get_children():
            self.table.delete(i)  # Delete old data

        # Insert new data into the table
        for row_data in data:
            # Insertion of the project in the graphic table, omitting the ID from the displayed value
            item = self.table.insert('', 'end', values=row_data[1:])
            self.controller.items_id_map[item] = row_data[0]
