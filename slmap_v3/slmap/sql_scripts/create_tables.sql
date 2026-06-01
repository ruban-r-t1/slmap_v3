
## This script performs the following actions:
#- Drops existing tables (if they already exist)
#- Creates new tables with the defined schema


DROP TABLE IF EXISTS shipment_tracking, shipments, courier_staff,routes,warehouses,costs;


# create courier_staff table
CREATE TABLE courier_staff (
    courier_id   VARCHAR(50) PRIMARY KEY COMMENT 'Unique identifier for courier employee',
    name         VARCHAR(150) NOT NULL COMMENT 'Full name of courier',
    rating       DECIMAL(3,1) COMMENT 'Courier performance rating (1–5 scale)',
    vehicle_type VARCHAR(50) COMMENT 'Type of delivery vehicle used (Bike, Van, Truck, Car)'
);


#create table shipments
CREATE TABLE shipments (
    shipment_id   VARCHAR(50) PRIMARY KEY COMMENT 'Unique identifier for each shipment/order',
    order_date    DATE NOT NULL COMMENT 'Date when the shipment order was created',
    origin        VARCHAR(100) NOT NULL COMMENT 'City/location where shipment starts',
    destination   VARCHAR(100) NOT NULL COMMENT 'Delivery city/location',
    weight        DECIMAL(10,2) NOT NULL COMMENT 'Weight of the shipment in kg',
    courier_id    VARCHAR(50) COMMENT 'Courier responsible for delivery (FK to courier_staff)',
    status        VARCHAR(50) NOT NULL COMMENT 'Current shipment status (Delivered, In Transit, Cancelled, etc.)',
    delivery_date DATE NULL COMMENT 'Date when shipment was delivered (NULL if not delivered yet)',
    CONSTRAINT fk_courier FOREIGN KEY (courier_id) REFERENCES courier_staff(courier_id)
);

#create table shipment_tracking
CREATE TABLE shipment_tracking (
    tracking_id  INT PRIMARY KEY COMMENT 'Unique identifier for tracking event',
    shipment_id  VARCHAR(50) NOT NULL COMMENT 'Shipment linked to this event (FK to shipments)',
    status       VARCHAR(50) NOT NULL COMMENT 'Status update at this stage (Picked Up, In Transit, Delivered, etc.)',
    timestamp    DATETIME NOT NULL COMMENT 'Date & time when this tracking event occurred',
    CONSTRAINT fk_shipment FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id)
);

#create table routes
CREATE TABLE routes (
    route_id VARCHAR(50) PRIMARY KEY,       -- Unique identifier for transport route
    origin VARCHAR(100),                    -- Starting city/location of route
    destination VARCHAR(100),               -- Ending city/location of route
    distance_km DECIMAL(10,2),              -- Distance between origin and destination in kilometers
    avg_time_hours DECIMAL(5,2)             -- Average travel time expected for this route
);

#create table warehouses
CREATE TABLE warehouses (
    warehouse_id VARCHAR(50) PRIMARY KEY,   -- Unique identifier for warehouse
    city VARCHAR(100),                      -- City where warehouse is located
    state VARCHAR(50),                      -- State or region of warehouse
    capacity INT                            -- Maximum shipment capacity warehouse can handle
);

#create table costs
CREATE TABLE costs (
    shipment_id VARCHAR(50) PRIMARY KEY,    -- Shipment linked to cost record (FK to shipments)
    fuel_cost DECIMAL(15,2),                -- Fuel cost incurred for shipment delivery
    labor_cost DECIMAL(15,2),               -- Courier labor cost for shipment
    misc_cost DECIMAL(15,2),                -- Additional operational costs (handling, packaging, etc.)
    CONSTRAINT fk_costs_shipment
        FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id)
);