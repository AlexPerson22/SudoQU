# Histo Perfo file #

histo_perfo_column_to_delete = ['CURR_PO_SUPPLIER_CODE', 'EDM_TABLE_JOB', 'REQUIREMENT_CODE', 'LAST_ISP', 'NB_ENTRY',
                                'INFO_IN', 'FIRST_EDM_MANAGEMENT_DATE', 'NB_OUT', 'INFO_OUT', 'PO_SHIPMENT_NUMBER']

histo_perfo_column_for_ID = ['PO_NUMBER', 'PO_LINE_NUMBER', 'RELEASE_NUMBER', 'PO_JOB']

# Full Backlog Data file #

full_backlog_data_column_to_delete = ['TRACKING_TYPE', 'QP', 'QCP_CODE_EXPECTED', 'QCP_DESCRIPTION', 'ISP_COMMENTS',
                                      'ITEM', 'PO_LINE_DESCRIPTION', 'SITU_RETARD', 'PO_STATUS', 'ACT_ISP',
                                      'PROMISED_MATERIAL_DATE', 'ISP_DOC_STATUS', 'SHIPMENT_CLOSURE_STATUS', 'SHIPMENT']

full_backlog_data_column_for_ID = ['PO', 'LINE', 'RELEASE', 'PROJECT_NUM']

# Navy Check file #

navy_check_column_to_delete = ['PO_CURRENT_BUYER', 'PO_CURRENT_SPA_SFM', 'PO_CREATION_DATE', 'CURRENT_PO_REVISION_NUM',
                               'PO_LAST_CONTRACTUAL_REV_NUM', 'PO_LAST_CONTRACTUAL_DATE', 'PO_CANCELLED', 'TYPE',
                               'RELEASE_CURRENT_BUYER', 'PO_LAST_COMMENTS', 'RELEASE_CANCELLED',
                               'PO_REL_LINE_FIRST_REVISION', 'CURR_VENDOR_CODE', 'PO_LINE_CLOSURE_STATUS', 'RCP',
                               'LINE_CANCELLED', 'ITEM_CODE', 'LINE_DESCRIPTION', 'CURR_CONTRACTUAL_DATE',
                               'CURR_PROMISED_DATE', 'MIN_ARRIVAL_DATE', 'MAX_ARRIVAL_DATE', 'MIN_RECEIVING_DATE',
                               'SHIP_CANCELLED', 'INFO_NIMA', 'SHIP_QUANTITY', 'SHIP_UNIT_MEAS_LOOKUP_CODE',
                               'SHIP_QUANTITY_RECEIVED', 'SHIP_QUANTITY_ACCEPTED', 'SHIP_QUANTITY_REJECTED',
                               'SHIP_QUANTITY_BILLED', 'SHIP_QUANTITY_CANCELLED', 'DISTRIBUTION_NUM',
                               'PROJ_QUANTITY_ORDERED', 'PROJ_QUANTITY_DELIVERED', 'PROJ_QUANTITY_CANCELLED',
                               'PROJ_QUANTITY_BILLED', 'KEY', 'KEY2', 'CURRENT_PO_APPROVAL_STATUS',
                               'SHIP_CLOSURE_STATUS', 'SHIPMENT_NUM']

navy_check_column_for_ID = ['PO', 'LINE_NUM', 'RELEASE_NUM', 'DIST_PROJECT']
