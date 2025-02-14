-- Supplier table: stores supplier details.
CREATE TABLE Supplier (
    supplier_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    plant_address VARCHAR(255),
    local_port VARCHAR(255),
    port_address VARCHAR(255),
    origin VARCHAR(100)
);

-- Part table: each unique part produced by a supplier.
CREATE TABLE Part (
    part_id INT PRIMARY KEY,
    supplier_id INT NOT NULL,
    part_name VARCHAR(255) NOT NULL,
    quantity INT,                -- Default ordered quantity (could be a typical order size)
    unit_price DECIMAL(10,2),
    line_total DECIMAL(10,2),
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
);

-- PurchaseOrder table: one PO per supplier (or order period).
CREATE TABLE PurchaseOrder (
    purchase_order_id INT PRIMARY KEY,
    supplier_id INT NOT NULL,
    order_date DATETIME,
    status VARCHAR(50),
    remarks VARCHAR(255),
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
);

-- PurchaseOrderLine table: one line per part in the PO.
CREATE TABLE PurchaseOrderLine (
    purchase_order_line_id INT PRIMARY KEY,
    purchase_order_id INT NOT NULL,
    part_id INT NOT NULL,
    quantity INT,
    unit_price DECIMAL(10,2),
    line_total DECIMAL(10,2),
    FOREIGN KEY (purchase_order_id) REFERENCES PurchaseOrder(purchase_order_id),
    FOREIGN KEY (part_id) REFERENCES Part(part_id)
);

-- Delivery table: multiple deliveries can be scheduled for each purchase order line.
CREATE TABLE Delivery (
    delivery_id INT PRIMARY KEY,
    purchase_order_line_id INT NOT NULL,
    delivery_date DATETIME,
    delivered_quantity INT,
    status VARCHAR(50),
    remarks VARCHAR(255),
    FOREIGN KEY (purchase_order_line_id) REFERENCES PurchaseOrderLine(purchase_order_line_id)
);

-- Shipment table: overall shipment information, which may be linked to a purchase order.
CREATE TABLE Shipment (
    shipment_id INT PRIMARY KEY,
    shipment_number VARCHAR(50),
    origin_location VARCHAR(255),
    destination_location VARCHAR(255),
    departure_date DATETIME,
    arrival_date DATETIME,
    purchase_order_id INT,
    FOREIGN KEY (purchase_order_id) REFERENCES PurchaseOrder(purchase_order_id)
);

-- ItinerarySegment table: stores the route details (each row represents one segment of a shipment's journey).
CREATE TABLE ItinerarySegment (
    itinerary_segment_id INT PRIMARY KEY,
    shipment_id INT NOT NULL,
    sequence_number INT,  -- Order of this segment in the shipment
    route_code VARCHAR(50),
    segment_fromlocation VARCHAR(255),
    segment_fromaddress VARCHAR(255),
    segment_tolocation VARCHAR(255),
    segment_toaddress VARCHAR(255),
    -- Instead of separate via columns, we store a single string with via elements joined by a hyphen.
    segment_via VARCHAR(500),
    shipping_method VARCHAR(50),
    scheduled_start_time DATETIME,
    scheduled_end_time DATETIME,
    google_route_description TEXT,  -- e.g. a JSON string containing step-by-step instructions
    google_route_mainways TEXT,       -- e.g. a JSON array of major road identifiers
    FOREIGN KEY (shipment_id) REFERENCES Shipment(shipment_id)
);

SELECT 
    i.itinerary_segment_id AS Itinerary_ID,
    i.sequence_number AS Sequence_Number,
    i.route_code AS Route_Code,
    i.segment_fromlocation AS segment_FromLocation,
    i.segment_fromaddress AS segment_FromAddress,
    i.segment_tolocation AS segment_ToLocation,
    i.segment_toaddress AS segment_ToAddress,
    i.segment_via AS segment_via,
    i.shipping_method AS Shipping_Method,
    i.scheduled_start_time AS Scheduled_Start_Time,
    i.scheduled_end_time AS Scheduled_End_Time,
    p.part_name AS Part_Name,
    pol.quantity AS Quantity,
    pol.unit_price AS Unit_Price,
    pol.line_total AS Line_Total,
    i.google_route_description AS GoogleRouteDescription,
    i.google_route_mainways AS GoogleRouteMainWays
FROM ItinerarySegment i
JOIN Part p ON p.part_id = i.part_id
JOIN PurchaseOrderLine pol ON pol.part_id = i.part_id
-- Optionally, if you want to limit to a single shipment:
-- JOIN Shipment s ON s.shipment_id = i.shipment_id
WHERE i.shipment_id = 5001
ORDER BY i.itinerary_segment_id;
