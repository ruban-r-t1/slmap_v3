# Shipment Logistics Management Analytics Platform

A Streamlit + MySQL dashboard for shipment search, operational KPI tracking, and logistics analytics. The project loads shipment-related datasets into MySQL and provides an interactive dashboard for filtering shipments, monitoring business performance, and reviewing analytical insights across delivery, courier, cost, cancellation, and warehouse dimensions.

## Project Objectives

- **Centralize logistics data**: Store shipments, courier staff, routes, shipment tracking, warehouse, and cost data in MySQL.
- **Enable shipment search and filtering**: Search by `shipment_id` and filter shipments by status, origin, destination, date range, and courier.
- **Track business KPIs**: Monitor total shipments, delivered percentage, cancelled percentage, average delivery time, and total operational cost.
- **Build analytical views**: Provide delivery, courier, cost, cancellation, and warehouse insights through Streamlit visualizations.
- **Support near real-time dashboard usage**: Use Streamlit caching with refresh controls to keep dashboard responses fast while allowing updated DB reads.

## Tech Stack

- **Python**
- **Streamlit** for dashboard UI
- **MySQL** for data storage
- **mysql-connector-python** for database connectivity
- **Pandas** for tabular data handling
- **Matplotlib** for pie/scatter visualizations

## Project Structure

```text
slmap/
├── dataset/                         # Source datasets
├── resources/
│   └── db.properties                # MySQL connection configuration
├── sql_scripts/                     # SQL scripts, if any
├── src/
│   ├── app.py                       # Main Streamlit dashboard
│   ├── app1.py                      # Earlier KPI demo app
│   └── main/
│       ├── mysql_connector.py       # MySQL connection helper
│       ├── repositories/            # DB table creation, inserts, queries
│       ├── services/                # Service layer used by Streamlit
│       └── utils/
│           └── constants.py         # Dataset paths and SQL constants
└── README.md
```

## Prerequisites

Before running the project, ensure you have:

- **Python 3.10+** installed
- **MySQL Server** installed and running
- A MySQL database created for the project
- Project dependencies installed

## Setup Instructions

### 1. Clone or open the project

Open the project folder:

```powershell
cd e:\guvi_projects\slmap
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install streamlit pandas mysql-connector-python matplotlib
```

If you already have a `requirements.txt`, you can install from it instead:

```powershell
pip install -r requirements.txt
```

### 4. Configure MySQL connection

Update `resources/db.properties` with your MySQL credentials:

```properties
[mysql]
host=localhost
user=your_mysql_user
password=your_mysql_password
database=your_database_name
```

The dashboard reads this file through `src/main/mysql_connector.py`.

### 5. Prepare the database tables

The repository layer contains table creation and insert methods for:

- `warehouses`
- `courier_staff`
- `routes`
- `shipments`
- `shipment_tracking`
- `costs`

Run your existing data-loading script or test setup that recreates and populates these tables from the files inside `dataset/`.

Expected source files include:

- `dataset/warehouses.json`
- `dataset/courier_staff.csv`
- `dataset/routes.csv`
- `dataset/shipments.json`
- `dataset/shipment_tracking.csv`
- `dataset/costs.csv`

### 6. Run the Streamlit dashboard

From the project root:

```powershell
streamlit run src\app.py
```

Streamlit will open the dashboard in your browser, usually at:

```text
http://localhost:8501
```

## Dashboard Features

### Shipment Search & Filtering

The left side of the dashboard focuses on operational search.

You can:

- **Search by shipment ID**
- **Filter by status**:
  - Delivered
  - Cancelled
  - In Transit
- **Filter by origin**
- **Filter by destination**
- **Filter by order date range**
- **Filter by courier**
- **Download filtered results as CSV**

### Business Analytics

The right side of the dashboard displays KPI cards and analytical views.

#### KPI Summary

- **Total shipments**
- **Delivered percentage**
- **Cancelled percentage**
- **Delivered shipment count**
- **Cancelled shipment count**
- **Shipment status distribution pie chart**
- **Average delivery time**
- **Total operational cost**

#### 1. Delivery Performance Insights

- **Average delivery time per route**
- **Most delayed routes**
- **Delivery time vs distance comparison**

Delayed routes are calculated by comparing actual shipment duration from tracking timestamps against route expected average time.

#### 2. Courier Performance

- **Shipments handled per courier**
- **On-time delivery percentage**
- **Average courier rating comparison**

#### 3. Cost Analytics

- **Total cost per shipment**
- **Cost per route**
- **Fuel vs labor vs miscellaneous percentage contribution**
- **High-cost shipments**

#### 4. Cancellation Analysis

- **Cancellation rate by origin**
- **Cancellation rate by courier**
- **Time-to-cancellation analysis**

#### 5. Warehouse Insights

- **Warehouse capacity comparison**
- **High-traffic warehouse cities**

High-traffic warehouse cities are estimated by counting shipments where the warehouse city appears as either shipment origin or destination.

## Demo Walkthrough

Use the following flow when presenting the project:

### Step 1: Open the dashboard

Run:

```powershell
streamlit run src\app.py
```

Explain that the app connects to MySQL using `resources/db.properties` and retrieves live data through the repository/service layers.

### Step 2: Shipment search

On the left panel:

1. Enter a valid `shipment_id`.
2. Click **Search**.
3. Show the returned shipment details.

This demonstrates direct shipment lookup from MySQL.

### Step 3: Shipment filtering

Use the filter form:

1. Select a shipment status, such as `Delivered` or `Cancelled`.
2. Choose an origin and destination.
3. Select a date range.
4. Select a courier.
5. Click **Apply Filters**.
6. Show the filtered table and CSV download option.

This demonstrates dynamic SQL filtering and dashboard interactivity.

### Step 4: KPI review

On the right panel, explain:

- Total shipment volume
- Delivery and cancellation percentages
- Delivered/cancelled counts
- Shipment status pie chart
- Average delivery time
- Total operational cost

### Step 5: Analytical views

Open each analytics tab:

- **Delivery**: Review route delivery performance and delays.
- **Courier**: Compare courier workload, on-time performance, and ratings.
- **Cost**: Analyze shipment costs, route costs, and cost contribution percentages.
- **Cancellation**: Identify high cancellation origins and couriers.
- **Warehouse**: Compare warehouse capacity and high-traffic cities.

### Step 6: Refresh data

Use the sidebar **Refresh data** button to clear cached data and reload updated results from MySQL.

## SQL and Performance Notes

- Queries use aggregate SQL such as `COUNT`, `SUM`, `AVG`, and `GROUP BY` for KPI calculations.
- Shipment filtering uses parameterized SQL to avoid unsafe string interpolation for user filters.
- Analytical views use grouped queries and `LIMIT` clauses to keep dashboard rendering responsive.
- Streamlit `@st.cache_data` is used with short TTL values for faster repeated views while still allowing updated database reads.

## Troubleshooting

### MySQL connection error

Check:

- MySQL server is running
- `resources/db.properties` has the correct credentials
- Database name exists
- User has permission to read the tables

### Module import error

Run the app from the project root:

```powershell
streamlit run src\app.py
```

### Missing package error

Install missing dependencies:

```powershell
pip install streamlit pandas mysql-connector-python matplotlib
```

### Empty dashboard tables

Check whether the database tables were populated from the dataset files.

## Future Enhancements

- Add authentication for dashboard access
- Add date filters to analytical views
- Add route-level drill-down pages
- Add predictive delay risk scoring
- Add export options for KPI and analytics reports
- Move analytical SQL queries from `app.py` into constants or repository-specific modules for cleaner separation
