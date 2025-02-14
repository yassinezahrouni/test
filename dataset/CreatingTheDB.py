import pandas as pd
from pandas import ExcelWriter

# -------------------------------
# 1. Shipment and Route Tables
# -------------------------------

# RouteLocation: key locations
df_route_location = pd.DataFrame([
    {"location_id": 1, "city": "Shanghai", "state": "Shanghai", "country": "China", "region": "East Asia"},
    {"location_id": 2, "city": "Singapore", "state": "Singapore", "country": "Singapore", "region": "Southeast Asia"},
    {"location_id": 3, "city": "Port Said", "state": "Sinai", "country": "Egypt", "region": "Middle East"},
    {"location_id": 4, "city": "Hamburg", "state": "Hamburg", "country": "Germany", "region": "Central Europe"},
    {"location_id": 5, "city": "Munich", "state": "Bavaria", "country": "Germany", "region": "Central Europe"}
])

# LogisticsRoute: overall shipment route
df_logistics_route = pd.DataFrame([
    {"route_id": 101, "origin_location_id": 1, "destination_location_id": 5, "estimated_distance": 11000, "estimated_time": "480:00:00"}
])

# Route_Master: defines high-level segments
df_route_master = pd.DataFrame([
    {"route_master_id": 500, "route_code": "RT-CN-SP", "description": "Shanghai to Singapore via East & South China Sea", "active_status": True},
    {"route_master_id": 501, "route_code": "RT-SP-PS", "description": "Singapore to Port Said via Strait of Malacca and Indian Ocean", "active_status": True},
    {"route_master_id": 502, "route_code": "RT-SC", "description": "Transit through the Suez Canal", "active_status": True},
    {"route_master_id": 503, "route_code": "RT-PS-HAM", "description": "Port Said to Hamburg via North Sea", "active_status": True},
    {"route_master_id": 504, "route_code": "RT-HAM-MU", "description": "Hamburg to Munich via Highway A1", "active_status": True},
    {"route_master_id": 510, "route_code": "RT-SP-HK", "description": "Singapore to Hong Kong along the South China Sea", "active_status": True},
    {"route_master_id": 520, "route_code": "RT-IST-PS", "description": "Istanbul to Port Said via Aegean & Mediterranean Sea", "active_status": True},
    {"route_master_id": 530, "route_code": "RT-SYD-SP", "description": "Sydney to Singapore via Tasman and South China Sea", "active_status": True},
    {"route_master_id": 540, "route_code": "RT-CAS-ALG", "description": "Casablanca to Algeciras across the Atlantic", "active_status": True}
])

# Route: individual segments (one per itinerary segment)
df_route = pd.DataFrame([
    # For Part 1 (China origin)
    {"route_id": 101, "route_master_id": 500, "sequence_number": 1, "location_id": 1},
    {"route_id": 102, "route_master_id": 501, "sequence_number": 2, "location_id": 2},
    {"route_id": 103, "route_master_id": 502, "sequence_number": 3, "location_id": 3},
    {"route_id": 104, "route_master_id": 503, "sequence_number": 4, "location_id": 3},  # For example, stop at Port Said before heading to Hamburg
    {"route_id": 105, "route_master_id": 504, "sequence_number": 5, "location_id": 5},
    # For Part 2 (Singapore origin) – a different route from Singapore to Germany
    {"route_id": 201, "route_master_id": 510, "sequence_number": 1, "location_id": 2},
    {"route_id": 202, "route_master_id": 502, "sequence_number": 2, "location_id": 3},
    {"route_id": 203, "route_master_id": 503, "sequence_number": 3, "location_id": 3},
    {"route_id": 204, "route_master_id": 504, "sequence_number": 4, "location_id": 5},
    # For Part 3 (Turkey origin)
    {"route_id": 301, "route_master_id": 520, "sequence_number": 1, "location_id": 2},  # Istanbul assumed mapped to location_id=2 (Singapore not ideal but for sample)
    {"route_id": 302, "route_master_id": 502, "sequence_number": 2, "location_id": 3},
    {"route_id": 303, "route_master_id": 503, "sequence_number": 3, "location_id": 3},
    {"route_id": 304, "route_master_id": 504, "sequence_number": 4, "location_id": 5},
    {"route_id": 305, "route_master_id": 505, "sequence_number": 5, "location_id": 5},  # Additional local leg if needed
    # For Part 4 (Australia origin)
    {"route_id": 401, "route_master_id": 540, "sequence_number": 1, "location_id": 1},  # Use location_id=1 but label as Sydney for example; you can adjust if you add a Sydney location
    {"route_id": 402, "route_master_id": 501, "sequence_number": 2, "location_id": 2},
    {"route_id": 403, "route_master_id": 502, "sequence_number": 3, "location_id": 3},
    {"route_id": 404, "route_master_id": 503, "sequence_number": 4, "location_id": 3},
    {"route_id": 405, "route_master_id": 504, "sequence_number": 5, "location_id": 5},
    # For Part 5 (Morocco origin)
    {"route_id": 501, "route_master_id": 540, "sequence_number": 1, "location_id": 4},  # Here, Casablanca not in our sample; for demo, re-use location_id 4 (Hamburg) to mimic a different route
    {"route_id": 502, "route_master_id": 540, "sequence_number": 2, "location_id": 3},
    {"route_id": 503, "route_master_id": 504, "sequence_number": 3, "location_id": 5}
])

# Itinerary: linking shipment and route segments per part
# We will create separate itineraries for each part (simulate as if each part follows a distinct itinerary).
df_itinerary = pd.DataFrame([
    # Part 1 itinerary (from China)
    {"itinerary_id": 6001, "shipment_id": 5001, "route_id": 101, "scheduled_start_time": "2024-10-01T05:00:00Z", "scheduled_end_time": "2024-10-01T23:00:00Z"},
    {"itinerary_id": 6002, "shipment_id": 5001, "route_id": 102, "scheduled_start_time": "2024-10-01T23:30:00Z", "scheduled_end_time": "2024-10-03T20:00:00Z"},
    {"itinerary_id": 6003, "shipment_id": 5001, "route_id": 103, "scheduled_start_time": "2024-10-03T20:30:00Z", "scheduled_end_time": "2024-10-03T23:00:00Z"},
    {"itinerary_id": 6004, "shipment_id": 5001, "route_id": 104, "scheduled_start_time": "2024-10-04T00:00:00Z", "scheduled_end_time": "2024-10-07T10:00:00Z"},
    {"itinerary_id": 6005, "shipment_id": 5001, "route_id": 105, "scheduled_start_time": "2024-10-07T10:30:00Z", "scheduled_end_time": "2024-10-10T18:00:00Z"},
    # Part 2 itinerary (from Singapore)
    {"itinerary_id": 6101, "shipment_id": 5001, "route_id": 201, "scheduled_start_time": "2024-10-03T06:00:00Z", "scheduled_end_time": "2024-10-03T18:00:00Z"},
    {"itinerary_id": 6102, "shipment_id": 5001, "route_id": 202, "scheduled_start_time": "2024-10-03T19:00:00Z", "scheduled_end_time": "2024-10-05T12:00:00Z"},
    {"itinerary_id": 6103, "shipment_id": 5001, "route_id": 203, "scheduled_start_time": "2024-10-05T12:30:00Z", "scheduled_end_time": "2024-10-07T06:00:00Z"},
    {"itinerary_id": 6104, "shipment_id": 5001, "route_id": 204, "scheduled_start_time": "2024-10-07T06:30:00Z", "scheduled_end_time": "2024-10-09T18:00:00Z"},
    # Part 3 itinerary (from Turkey)
    {"itinerary_id": 6201, "shipment_id": 5001, "route_id": 301, "scheduled_start_time": "2024-10-04T05:00:00Z", "scheduled_end_time": "2024-10-04T23:00:00Z"},
    {"itinerary_id": 6202, "shipment_id": 5001, "route_id": 302, "scheduled_start_time": "2024-10-05T00:00:00Z", "scheduled_end_time": "2024-10-05T08:00:00Z"},
    {"itinerary_id": 6203, "shipment_id": 5001, "route_id": 303, "scheduled_start_time": "2024-10-05T08:30:00Z", "scheduled_end_time": "2024-10-07T12:00:00Z"},
    {"itinerary_id": 6204, "shipment_id": 5001, "route_id": 304, "scheduled_start_time": "2024-10-07T12:30:00Z", "scheduled_end_time": "2024-10-09T20:00:00Z"},
    {"itinerary_id": 6205, "shipment_id": 5001, "route_id": 305, "scheduled_start_time": "2024-10-09T20:30:00Z", "scheduled_end_time": "2024-10-09T22:00:00Z"},
    # Part 4 itinerary (from Australia)
    {"itinerary_id": 6301, "shipment_id": 5001, "route_id": 401, "scheduled_start_time": "2024-10-05T04:00:00Z", "scheduled_end_time": "2024-10-05T18:00:00Z"},
    {"itinerary_id": 6302, "shipment_id": 5001, "route_id": 402, "scheduled_start_time": "2024-10-05T19:00:00Z", "scheduled_end_time": "2024-10-06T12:00:00Z"},
    {"itinerary_id": 6303, "shipment_id": 5001, "route_id": 403, "scheduled_start_time": "2024-10-06T12:30:00Z", "scheduled_end_time": "2024-10-06T19:00:00Z"},
    {"itinerary_id": 6304, "shipment_id": 5001, "route_id": 404, "scheduled_start_time": "2024-10-06T19:30:00Z", "scheduled_end_time": "2024-10-09T10:00:00Z"},
    {"itinerary_id": 6305, "shipment_id": 5001, "route_id": 405, "scheduled_start_time": "2024-10-09T10:30:00Z", "scheduled_end_time": "2024-10-10T18:00:00Z"},
    # Part 5 itinerary (from Morocco)
    {"itinerary_id": 6401, "shipment_id": 5001, "route_id": 501, "scheduled_start_time": "2024-10-02T06:00:00Z", "scheduled_end_time": "2024-10-02T18:00:00Z"},
    {"itinerary_id": 6402, "shipment_id": 5001, "route_id": 502, "scheduled_start_time": "2024-10-02T19:00:00Z", "scheduled_end_time": "2024-10-03T12:00:00Z"},
    {"itinerary_id": 6403, "shipment_id": 5001, "route_id": 503, "scheduled_start_time": "2024-10-03T12:30:00Z", "scheduled_end_time": "2024-10-05T08:00:00Z"},
    {"itinerary_id": 6404, "shipment_id": 5001, "route_id": 504, "scheduled_start_time": "2024-10-05T08:30:00Z", "scheduled_end_time": "2024-10-07T18:00:00Z"},
    {"itinerary_id": 6405, "shipment_id": 5001, "route_id": 505, "scheduled_start_time": "2024-10-07T19:00:00Z", "scheduled_end_time": "2024-10-07T21:00:00Z"}
])

# ItineraryShipment: linking itinerary with shipment (if needed)
df_itinerary_shipment = pd.DataFrame([
    {"itinerary_shipment_id": 7001, "itinerary_id": 6001, "shipment_id": 5001},
    {"itinerary_shipment_id": 7002, "itinerary_id": 6002, "shipment_id": 5001},
    {"itinerary_shipment_id": 7003, "itinerary_id": 6003, "shipment_id": 5001},
    {"itinerary_shipment_id": 7004, "itinerary_id": 6004, "shipment_id": 5001},
    {"itinerary_shipment_id": 7005, "itinerary_id": 6005, "shipment_id": 5001},
    {"itinerary_shipment_id": 7101, "itinerary_id": 6101, "shipment_id": 5001},
    {"itinerary_shipment_id": 7102, "itinerary_id": 6102, "shipment_id": 5001},
    {"itinerary_shipment_id": 7103, "itinerary_id": 6103, "shipment_id": 5001},
    {"itinerary_shipment_id": 7104, "itinerary_id": 6104, "shipment_id": 5001},
    {"itinerary_shipment_id": 7201, "itinerary_id": 6201, "shipment_id": 5001},
    {"itinerary_shipment_id": 7202, "itinerary_id": 6202, "shipment_id": 5001},
    {"itinerary_shipment_id": 7203, "itinerary_id": 6203, "shipment_id": 5001},
    {"itinerary_shipment_id": 7204, "itinerary_id": 6204, "shipment_id": 5001},
    {"itinerary_shipment_id": 7205, "itinerary_id": 6205, "shipment_id": 5001},
    {"itinerary_shipment_id": 7301, "itinerary_id": 6301, "shipment_id": 5001},
    {"itinerary_shipment_id": 7302, "itinerary_id": 6302, "shipment_id": 5001},
    {"itinerary_shipment_id": 7303, "itinerary_id": 6303, "shipment_id": 5001},
    {"itinerary_shipment_id": 7304, "itinerary_id": 6304, "shipment_id": 5001},
    {"itinerary_shipment_id": 7305, "itinerary_id": 6305, "shipment_id": 5001},
    {"itinerary_shipment_id": 7401, "itinerary_id": 6401, "shipment_id": 5001},
    {"itinerary_shipment_id": 7402, "itinerary_id": 6402, "shipment_id": 5001},
    {"itinerary_shipment_id": 7403, "itinerary_id": 6403, "shipment_id": 5001},
    {"itinerary_shipment_id": 7404, "itinerary_id": 6404, "shipment_id": 5001},
    {"itinerary_shipment_id": 7405, "itinerary_id": 6405, "shipment_id": 5001}
])

# Shipment: main shipment details
df_shipment = pd.DataFrame([
    {"shipment_id": 5001, "shipment_number": "SHIP-20241001", "origin_location_id": 1, "destination_location_id": 5,
     "departure_date": "2024-10-01T06:00:00Z", "arrival_date": "2024-10-10T18:00:00Z", "status": "in transit"}
])

# RecordShipment: additional shipment details
df_record_shipment = pd.DataFrame([
    {"record_shipment_id": 8001, "shipment_id": 5001, "shipment_type": "ocean-road", "record_details": "Multi-segment route shipment."}
])

# ShipmentAlert: alerts for shipment
df_shipment_alert = pd.DataFrame([
    {"alert_id": 9001, "shipment_id": 5001, "alert_type": "delay", "alert_message": "Weather delay near Suez Canal.", "alert_date": "2024-10-07T08:00:00Z"}
])

# ShipmentDocument: documents for the shipment
df_shipment_document = pd.DataFrame([
    {"document_id": 10001, "shipment_id": 5001, "document_type": "Bill of Lading", "document_path": "https://docs.example.com/bill_lading_ship20241001.pdf", "upload_date": "2024-10-01T07:00:00Z"}
])

# ShipmentPlanning: planning details
df_shipment_planning = pd.DataFrame([
    {"planning_id": 11001, "shipment_id": 5001, "planned_route_id": 101, "planner_notes": "Confirmed ocean segment.", "planning_date": "2024-09-28T14:00:00Z"}
])

# ShipmentContainer: container info
df_shipment_container = pd.DataFrame([
    {"container_id": 12001, "shipment_id": 5001, "container_number": "CONT-20241001-A", "container_type": "40ft", "seal_number": "SEAL-2024A1"}
])

# LocationHoliday: holidays at locations
df_location_holiday = pd.DataFrame([
    {"holiday_id": 13001, "location_id": 1, "holiday_date": "2024-10-01", "description": "Local holiday at Shanghai Port"},
    {"holiday_id": 13002, "location_id": 5, "holiday_date": "2024-12-25", "description": "Christmas at Munich"}
])

# ShipmentSailingScheduleStop: maritime schedule stops
df_sailing_schedule_stop = pd.DataFrame([
    {"sailing_schedule_stop_id": 14001, "shipment_id": 5001, "port_location_id": 3, "arrival_date": "2024-10-07T09:00:00Z", "departure_date": "2024-10-07T16:00:00Z"}
])

# -------------------------------
# 2. Supplier Tables
# -------------------------------

# Suppliers
df_suppliers = pd.DataFrame([
    {"supplier_id": 1, "name": "DHL Global Forwarding", "contact_name": "Sandra Miller", "contact_title": "Regional Manager",
     "phone": "+49 30 1234567", "email": "sandra.miller@dhl.com", "website": "https://www.dhl.com", "status": "Active", "rating": 4.8, "notes": "Excellent for international shipments."}
])

# Supplier_Address
df_supplier_address = pd.DataFrame([
    {"address_id": 2101, "supplier_id": 1, "address_line1": "1000 International Way", "address_line2": "Suite 150", "city": "Frankfurt", "state": "Hesse", "postal_code": "60313", "country": "Germany"}
])

# Supplier_Contacts
df_supplier_contacts = pd.DataFrame([
    {"contact_id": 2201, "supplier_id": 1, "name": "David Kim", "title": "Customer Service Lead", "phone": "+49 30 1234568", "email": "david.kim@dhl.com"}
])

# Supplier_Certifications
df_supplier_certifications = pd.DataFrame([
    {"certification_id": 2301, "supplier_id": 1, "certification_name": "ISO 9001", "certification_body": "ISO", "issue_date": "2021-03-01", "expiry_date": "2024-03-01"}
])

# Supplier_Performance
df_supplier_performance = pd.DataFrame([
    {"performance_id": 2401, "supplier_id": 1, "evaluation_date": "2024-09-15", "score": 4.8, "comments": "On schedule and very reliable."}
])

# -------------------------------
# 3. Parts Tables
# -------------------------------

# Part_Categories
df_part_categories = pd.DataFrame([
    {"category_id": 1, "category_name": "Electrical", "description": "Components for electrical circuits and devices."},
    {"category_id": 2, "category_name": "Mechanical", "description": "Mechanical parts and assemblies."}
])

# Parts: five distinct parts with different origins
df_parts = pd.DataFrame([
    {"part_id": 1, "name": "Microcontroller ATmega328", "part_number": "ELEC-MCU-003", "description": "8-bit microcontroller used in Arduino boards", "category_id": 1, "unit_price": 2.50, "currency": "USD", "weight": 0.02, "dimensions": "3x3x0.8 cm", "color": "Green", "material": "Silicon", "status": "Active", "notes": "Origin: China"},
    {"part_id": 2, "name": "Solenoid Valve", "part_number": "MECH-SOL-010", "description": "Electrically controlled solenoid valve", "category_id": 2, "unit_price": 12.00, "currency": "USD", "weight": 0.3, "dimensions": "4x4x4 cm", "color": "Black", "material": "Brass", "status": "Active", "notes": "Origin: Singapore"},
    {"part_id": 3, "name": "Stepper Motor", "part_number": "MECH-STEP-012", "description": "High-torque stepper motor for precision control", "category_id": 2, "unit_price": 15.00, "currency": "USD", "weight": 0.4, "dimensions": "6x6x6 cm", "color": "Blue", "material": "Aluminum", "status": "Active", "notes": "Origin: Turkey"},
    {"part_id": 4, "name": "Printed Circuit Board", "part_number": "ELEC-PCB-018", "description": "Single-layer PCB for prototypes", "category_id": 1, "unit_price": 4.00, "currency": "USD", "weight": 0.05, "dimensions": "10x10x0.2 cm", "color": "Green", "material": "Fiberglass", "status": "Active", "notes": "Origin: Australia"},
    {"part_id": 5, "name": "Pneumatic Air Filter", "part_number": "PNEUM-AFILT-025", "description": "Air filter for pneumatic systems", "category_id": 2, "unit_price": 2.50, "currency": "USD", "weight": 0.1, "dimensions": "4x4x2 cm", "color": "White", "material": "Foam", "status": "Active", "notes": "Origin: Morocco"}
])

# Part_Suppliers: assigning each part to a supplier
df_part_suppliers = pd.DataFrame([
    {"part_supplier_id": 1, "part_id": 1, "supplier_id": 1, "lead_time_days": 5, "minimum_order_quantity": 100, "supply_status": "Active"},
    {"part_supplier_id": 2, "part_id": 2, "supplier_id": 1, "lead_time_days": 5, "minimum_order_quantity": 200, "supply_status": "Active"},
    {"part_supplier_id": 3, "part_id": 3, "supplier_id": 1, "lead_time_days": 7, "minimum_order_quantity": 50, "supply_status": "Active"},
    {"part_supplier_id": 4, "part_id": 4, "supplier_id": 1, "lead_time_days": 10, "minimum_order_quantity": 20, "supply_status": "Active"},
    {"part_supplier_id": 5, "part_id": 5, "supplier_id": 1, "lead_time_days": 8, "minimum_order_quantity": 10, "supply_status": "Active"}
])

# Part_Inventory: inventory details for each part
df_part_inventory = pd.DataFrame([
    {"inventory_id": 1, "part_id": 1, "quantity_on_hand": 1000, "reorder_level": 200, "location_id": 1},
    {"inventory_id": 2, "part_id": 2, "quantity_on_hand": 800, "reorder_level": 150, "location_id": 2},
    {"inventory_id": 3, "part_id": 3, "quantity_on_hand": 500, "reorder_level": 100, "location_id": 3},
    {"inventory_id": 4, "part_id": 4, "quantity_on_hand": 250, "reorder_level": 50, "location_id": 1},
    {"inventory_id": 5, "part_id": 5, "quantity_on_hand": 600, "reorder_level": 80, "location_id": 4}
])

# -------------------------------
# 4. Purchase Order Tables (Assumed)
# -------------------------------

# PurchaseOrder
df_purchase_order = pd.DataFrame([
    {"purchase_order_id": 1001, "shipment_id": 5001, "order_date": "2024-09-25T10:00:00Z", "status": "Confirmed"}
])

# PurchaseOrderLine: one line per part
df_purchase_order_line = pd.DataFrame([
    {"purchase_order_line_id": 101, "purchase_order_id": 1001, "part_id": 1, "quantity": 200, "unit_price": 2.50},
    {"purchase_order_line_id": 102, "purchase_order_id": 1001, "part_id": 2, "quantity": 50, "unit_price": 12.00},
    {"purchase_order_line_id": 103, "purchase_order_id": 1001, "part_id": 3, "quantity": 30, "unit_price": 15.00},
    {"purchase_order_line_id": 104, "purchase_order_id": 1001, "part_id": 4, "quantity": 100, "unit_price": 4.00},
    {"purchase_order_line_id": 105, "purchase_order_id": 1001, "part_id": 5, "quantity": 75, "unit_price": 2.50}
])

# -------------------------------
# Write to Excel File
# -------------------------------
with ExcelWriter("supply_chain_schema.xlsx") as writer:
    df_route_location.to_excel(writer, sheet_name="RouteLocation", index=False)
    df_logistics_route.to_excel(writer, sheet_name="LogisticsRoute", index=False)
    df_route_master.to_excel(writer, sheet_name="Route_Master", index=False)
    df_route.to_excel(writer, sheet_name="Route", index=False)
    df_itinerary.to_excel(writer, sheet_name="Itinerary", index=False)
    df_itinerary_shipment.to_excel(writer, sheet_name="ItineraryShipment", index=False)
    df_shipment.to_excel(writer, sheet_name="Shipment", index=False)
    df_record_shipment.to_excel(writer, sheet_name="RecordShipment", index=False)
    df_shipment_alert.to_excel(writer, sheet_name="ShipmentAlert", index=False)
    df_shipment_document.to_excel(writer, sheet_name="ShipmentDocument", index=False)
    df_shipment_planning.to_excel(writer, sheet_name="ShipmentPlanning", index=False)
    df_shipment_container.to_excel(writer, sheet_name="ShipmentContainer", index=False)
    df_location_holiday.to_excel(writer, sheet_name="LocationHoliday", index=False)
    df_sailing_schedule_stop.to_excel(writer, sheet_name="ShipmentSailingScheduleStop", index=False)
    df_suppliers.to_excel(writer, sheet_name="Suppliers", index=False)
    df_supplier_address.to_excel(writer, sheet_name="Supplier_Address", index=False)
    df_supplier_contacts.to_excel(writer, sheet_name="Supplier_Contacts", index=False)
    df_supplier_certifications.to_excel(writer, sheet_name="Supplier_Certifications", index=False)
    df_supplier_performance.to_excel(writer, sheet_name="Supplier_Performance", index=False)
    df_part_categories.to_excel(writer, sheet_name="Part_Categories", index=False)
    df_parts.to_excel(writer, sheet_name="Parts", index=False)
    df_part_suppliers.to_excel(writer, sheet_name="Part_Suppliers", index=False)
    df_part_inventory.to_excel(writer, sheet_name="Part_Inventory", index=False)
    df_purchase_order.to_excel(writer, sheet_name="PurchaseOrder", index=False)
    df_purchase_order_line.to_excel(writer, sheet_name="PurchaseOrderLine", index=False)

print("Excel file 'supply_chain_schema.xlsx' has been generated.")
