from pathlib import Path

# Project root = 2 levels up from this file
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Dataset folder
DATASET_DIR = PROJECT_ROOT / "dataset"

# Warehouses JSON file
WAREHOUSE_JSON_PATH = DATASET_DIR / "warehouses.json"
COURIER_STAFF_CSV_PATH = DATASET_DIR / "courier_staff.csv"
ROUTES_CSV_PATH = DATASET_DIR / "routes.csv"
SHIPMENTS_JSON_PATH = DATASET_DIR / "shipments.json"
COSTS_CSV_PATH = DATASET_DIR / "costs.csv"
SHIPMENT_TRACKING_CSV_PATH = DATASET_DIR / "shipment_tracking.csv"


##Sql queries
SEARCH_BY_SHIPMENT_ID = """
        SELECT s.*, c.name AS courier_name, c.vehicle_type
        FROM shipments s
        LEFT JOIN courier_staff c ON s.courier_id = c.courier_id
        WHERE s.shipment_id = %s;
    """
FILTER_SHIPMENTS = """
        SELECT s.*, c.name AS courier_name
        FROM shipments s
        LEFT JOIN courier_staff c ON s.courier_id = c.courier_id
        WHERE (%s IS NULL OR s.status = %s)
          AND (%s IS NULL OR s.origin = %s)
          AND (%s IS NULL OR s.destination = %s)
          AND (%s IS NULL OR s.order_date BETWEEN %s AND %s)
          AND (%s IS NULL OR s.courier_id = %s);
    """

TOTAL_SHIPMENTS = """
        SELECT count(s.shipment_id) FROM shipments s
    """

TOTAL_DELIVERED_SHIPMENTS = """
        SELECT count(s.shipment_id) FROM shipments s WHERE s.status='Delivered'
    """

TOTAL_CANCELLED_SHIPMENTS = """
        SELECT count(s.shipment_id) FROM shipments s WHERE s.status='Cancelled'
    """

AVERAGE_DELIVERY_TIME="""
        SELECT 
            COUNT(*) AS total_shipments,
            SUM(duration) AS total_duration_minutes,
            AVG(duration) AS avg_duration_minutes,
            CONCAT(
                FLOOR(AVG(duration) / 1440),
                ' days ',
                FLOOR(MOD(AVG(duration), 1440) / 60),
                ' hrs'
            ) AS avg_duration
        FROM (
            SELECT 
                st.shipment_id ,
                TIMESTAMPDIFF(
                    MINUTE,
                    MIN(`timestamp`),
                    MAX(`timestamp`)
                ) AS duration
            FROM shipment_tracking st 
            WHERE st.shipment_id IN (
                SELECT s.shipment_id
                FROM shipments s
                WHERE status = 'Delivered'
            )
		GROUP BY st.shipment_id
	) t;
    """

DISTINCT_ORIGINS = "SELECT DISTINCT origin FROM shipments WHERE origin IS NOT NULL ORDER BY origin"
DISTINCT_DESTINATIONS = "SELECT DISTINCT destination FROM shipments WHERE destination IS NOT NULL ORDER BY destination"
DISTINCT_COURIERS = """
        SELECT c.courier_id, c.name
        FROM courier_staff c
        ORDER BY c.name
    """

TOTAL_OPERATIONAL_COST_OF_SHIPMENTS = """
        select SUM(total_cost_1) from (
            SELECT
                tc.shipment_id,
                tc.total_cost_1
            FROM (
                SELECT
                    c.shipment_id,
                    SUM(
                        c.fuel_cost +
                        c.labor_cost +
                        c.misc_cost
                    ) AS total_cost_1
                FROM costs c
                GROUP BY c.shipment_id
            ) tc
        ) tcount;
        """