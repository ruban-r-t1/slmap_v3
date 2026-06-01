import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from main.services.shipments_services import ShipmentsService

st.set_page_config(page_title="Shipment Dashboard", page_icon="📦", layout="wide")

repo = ShipmentsService()

# ---- Cached lookups for filter dropdowns (TTL keeps it near real-time) ----
@st.cache_data(ttl=60, show_spinner=False)
def load_filter_options():
    return repo.fetch_filter_options()

@st.cache_data(ttl=30, show_spinner=False)
def run_filter(status, origin, destination, start_date, end_date, courier_id):
    return repo.filter_shipments(
        status=status,
        origin=origin,
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        courier_id=courier_id,
    )

@st.cache_data(ttl=30, show_spinner=False)
def run_search_by_id(shipment_id):
    return repo.fetch_Shipment_by_id(shipment_id)

@st.cache_data(ttl=60, show_spinner=False)
def analytics_df(query):
    columns, rows = repo.fetch_analytics_view(query)
    return pd.DataFrame(rows, columns=columns)

ANALYTICS_QUERIES = {
    "average_delivery_time_per_route": """
        SELECT r.route_id, CONCAT(r.origin, ' → ', r.destination) AS route,
               ROUND(r.distance_km, 2) AS distance_km,
               ROUND(AVG(TIMESTAMPDIFF(MINUTE, fe.first_time, le.last_time)) / 60, 2) AS avg_actual_hours,
               ROUND(r.avg_time_hours, 2) AS expected_hours
        FROM shipments s
        JOIN routes r ON s.origin = r.origin AND s.destination = r.destination
        JOIN (SELECT shipment_id, MIN(`timestamp`) AS first_time FROM shipment_tracking GROUP BY shipment_id) fe ON s.shipment_id = fe.shipment_id
        JOIN (SELECT shipment_id, MAX(`timestamp`) AS last_time FROM shipment_tracking GROUP BY shipment_id) le ON s.shipment_id = le.shipment_id
        WHERE s.status = 'Delivered'
        GROUP BY r.route_id, r.origin, r.destination, r.distance_km, r.avg_time_hours
        ORDER BY avg_actual_hours DESC
        LIMIT 10
    """,
    "most_delayed_routes": """
        SELECT r.route_id, CONCAT(r.origin, ' → ', r.destination) AS route,
               COUNT(*) AS delivered_shipments,
               ROUND(AVG(TIMESTAMPDIFF(MINUTE, fe.first_time, le.last_time)) / 60, 2) AS avg_actual_hours,
               ROUND(r.avg_time_hours, 2) AS expected_hours,
               ROUND(AVG(TIMESTAMPDIFF(MINUTE, fe.first_time, le.last_time)) / 60 - r.avg_time_hours, 2) AS delay_hours
        FROM shipments s
        JOIN routes r ON s.origin = r.origin AND s.destination = r.destination
        JOIN (SELECT shipment_id, MIN(`timestamp`) AS first_time FROM shipment_tracking GROUP BY shipment_id) fe ON s.shipment_id = fe.shipment_id
        JOIN (SELECT shipment_id, MAX(`timestamp`) AS last_time FROM shipment_tracking GROUP BY shipment_id) le ON s.shipment_id = le.shipment_id
        WHERE s.status = 'Delivered'
        GROUP BY r.route_id, r.origin, r.destination, r.avg_time_hours
        HAVING delay_hours > 0
        ORDER BY delay_hours DESC
        LIMIT 10
    """,
    "delivery_time_vs_distance": """
        SELECT CONCAT(r.origin, ' → ', r.destination) AS route,
               ROUND(r.distance_km, 2) AS distance_km,
               ROUND(AVG(TIMESTAMPDIFF(MINUTE, fe.first_time, le.last_time)) / 60, 2) AS avg_actual_hours
        FROM shipments s
        JOIN routes r ON s.origin = r.origin AND s.destination = r.destination
        JOIN (SELECT shipment_id, MIN(`timestamp`) AS first_time FROM shipment_tracking GROUP BY shipment_id) fe ON s.shipment_id = fe.shipment_id
        JOIN (SELECT shipment_id, MAX(`timestamp`) AS last_time FROM shipment_tracking GROUP BY shipment_id) le ON s.shipment_id = le.shipment_id
        WHERE s.status = 'Delivered'
        GROUP BY r.route_id, r.origin, r.destination, r.distance_km
        ORDER BY r.distance_km
        LIMIT 50
    """,
    "shipments_handled_per_courier": """
        SELECT c.name, COUNT(s.shipment_id) AS shipments_handled
        FROM courier_staff c
        LEFT JOIN shipments s ON c.courier_id = s.courier_id
        GROUP BY c.courier_id, c.name
        ORDER BY shipments_handled DESC
        LIMIT 10
    """,
    "on_time_delivery_percentage": """
        SELECT c.name, COUNT(s.shipment_id) AS delivered_shipments,
               ROUND(100 * SUM(CASE WHEN TIMESTAMPDIFF(MINUTE, fe.first_time, le.last_time) / 60 <= r.avg_time_hours THEN 1 ELSE 0 END) / COUNT(s.shipment_id), 2) AS on_time_percentage
        FROM courier_staff c
        JOIN shipments s ON c.courier_id = s.courier_id
        JOIN routes r ON s.origin = r.origin AND s.destination = r.destination
        JOIN (SELECT shipment_id, MIN(`timestamp`) AS first_time FROM shipment_tracking GROUP BY shipment_id) fe ON s.shipment_id = fe.shipment_id
        JOIN (SELECT shipment_id, MAX(`timestamp`) AS last_time FROM shipment_tracking GROUP BY shipment_id) le ON s.shipment_id = le.shipment_id
        WHERE s.status = 'Delivered'
        GROUP BY c.courier_id, c.name
        ORDER BY on_time_percentage DESC
        LIMIT 10
    """,
    "average_rating_comparison": """
        SELECT name, ROUND(rating, 2) AS rating, vehicle_type
        FROM courier_staff
        ORDER BY rating DESC
        LIMIT 10
    """,
    "total_cost_per_shipment": """
        SELECT s.shipment_id, CONCAT(s.origin, ' → ', s.destination) AS route,
               ROUND(c.fuel_cost + c.labor_cost + c.misc_cost, 2) AS total_cost
        FROM shipments s
        JOIN costs c ON s.shipment_id = c.shipment_id
        ORDER BY total_cost DESC
        LIMIT 10
    """,
    "cost_per_route": """
        SELECT CONCAT(s.origin, ' → ', s.destination) AS route,
               COUNT(*) AS shipment_count,
               ROUND(SUM(c.fuel_cost + c.labor_cost + c.misc_cost), 2) AS total_route_cost,
               ROUND(AVG(c.fuel_cost + c.labor_cost + c.misc_cost), 2) AS avg_cost_per_shipment
        FROM shipments s
        JOIN costs c ON s.shipment_id = c.shipment_id
        GROUP BY s.origin, s.destination
        ORDER BY total_route_cost DESC
        LIMIT 10
    """,
    "fuel_vs_labor_percentage": """
        SELECT ROUND(100 * SUM(fuel_cost) / SUM(fuel_cost + labor_cost + misc_cost), 2) AS fuel_percentage,
               ROUND(100 * SUM(labor_cost) / SUM(fuel_cost + labor_cost + misc_cost), 2) AS labor_percentage,
               ROUND(100 * SUM(misc_cost) / SUM(fuel_cost + labor_cost + misc_cost), 2) AS misc_percentage
        FROM costs
    """,
    "high_cost_shipments": """
        SELECT s.shipment_id, CONCAT(s.origin, ' → ', s.destination) AS route, s.status,
               ROUND(c.fuel_cost + c.labor_cost + c.misc_cost, 2) AS total_cost
        FROM shipments s
        JOIN costs c ON s.shipment_id = c.shipment_id
        WHERE c.fuel_cost + c.labor_cost + c.misc_cost > (SELECT AVG(fuel_cost + labor_cost + misc_cost) FROM costs)
        ORDER BY total_cost DESC
        LIMIT 10
    """,
    "cancellation_rate_by_origin": """
        SELECT origin, COUNT(*) AS total_shipments,
               SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_shipments,
               ROUND(100 * SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(*), 2) AS cancellation_rate
        FROM shipments
        GROUP BY origin
        ORDER BY cancellation_rate DESC
        LIMIT 10
    """,
    "cancellation_rate_by_courier": """
        SELECT c.name, COUNT(s.shipment_id) AS total_shipments,
               SUM(CASE WHEN s.status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_shipments,
               ROUND(100 * SUM(CASE WHEN s.status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(s.shipment_id), 2) AS cancellation_rate
        FROM courier_staff c
        JOIN shipments s ON c.courier_id = s.courier_id
        GROUP BY c.courier_id, c.name
        ORDER BY cancellation_rate DESC
        LIMIT 10
    """,
    "time_to_cancellation": """
        SELECT s.shipment_id, CONCAT(s.origin, ' → ', s.destination) AS route,
               ROUND(TIMESTAMPDIFF(MINUTE, MIN(st.`timestamp`), MAX(st.`timestamp`)) / 60, 2) AS hours_to_cancellation
        FROM shipments s
        JOIN shipment_tracking st ON s.shipment_id = st.shipment_id
        WHERE s.status = 'Cancelled'
        GROUP BY s.shipment_id, s.origin, s.destination
        ORDER BY hours_to_cancellation DESC
        LIMIT 10
    """,
    "warehouse_capacity_comparison": """
        SELECT warehouse_id, city, state, capacity
        FROM warehouses
        ORDER BY capacity DESC
        LIMIT 10
    """,
    "high_traffic_warehouse_cities": """
        SELECT w.city, w.state, w.capacity, COUNT(s.shipment_id) AS shipment_traffic
        FROM warehouses w
        LEFT JOIN shipments s ON w.city = s.origin OR w.city = s.destination
        GROUP BY w.city, w.state, w.capacity
        ORDER BY shipment_traffic DESC
        LIMIT 10
    """
}

st.title("📦 Shipment Dashboard")

# =====================================================================
# Layout: LEFT = Search & Filter, RIGHT = Business Analytics
# =====================================================================
left_col, right_col = st.columns(2, gap="large")

# ---------------------------------------------------------------------
# LEFT PANEL — Shipment Search & Filtering
# ---------------------------------------------------------------------
with left_col:
    st.header("🔎 Shipment Search & Filtering")

    # --- Search by Shipment ID ---
    st.subheader("Search Shipment by ID")
    with st.form("search_form", clear_on_submit=False):
        shipment_id = st.text_input("Enter Shipment ID")
        search_clicked = st.form_submit_button("Search")

    if search_clicked:
        if not shipment_id.strip():
            st.warning("Please enter a shipment ID.")
        else:
            columns, result = run_search_by_id(shipment_id.strip())
            if result:
                df = pd.DataFrame(result, columns=columns)
                st.dataframe(df, use_container_width=True)
            else:
                st.warning(f"No shipment found for ID '{shipment_id}'.")

    st.divider()

    # --- Filter Shipments ---
    st.subheader("Filter Shipments")

    try:
        origins, destinations, couriers = load_filter_options()
    except Exception as e:
        st.error(f"Could not load filter options from DB: {e}")
        origins, destinations, couriers = [], [], []

    courier_display = {f"{name} ({cid})": cid for cid, name in couriers}

    with st.form("filter_form"):
        f1, f2 = st.columns(2)
        with f1:
            status = st.selectbox("Status", ["All", "Delivered", "In Transit", "Cancelled"])
            origin = st.selectbox("Origin", ["All"] + origins)
            date_range = st.date_input("Order Date Range", [])
        with f2:
            destination = st.selectbox("Destination", ["All"] + destinations)
            courier_label = st.selectbox("Courier", ["All"] + list(courier_display.keys()))

        apply_clicked = st.form_submit_button("Apply Filters")

    if apply_clicked:
        start_date, end_date = (None, None)
        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            start_date, end_date = date_range

        columns, results = run_filter(
            status=None if status == "All" else status,
            origin=None if origin == "All" else origin,
            destination=None if destination == "All" else destination,
            start_date=start_date,
            end_date=end_date,
            courier_id=None if courier_label == "All" else courier_display[courier_label],
        )

        if results:
            df = pd.DataFrame(results, columns=columns)
            st.success(f"Found {len(df)} shipment(s).")
            st.dataframe(df, use_container_width=True)
            st.download_button(
                "⬇️ Download as CSV",
                df.to_csv(index=False).encode("utf-8"),
                file_name="shipments_filtered.csv",
                mime="text/csv",
            )
        else:
            st.info("No shipments found for the given filters.")
    else:
        st.caption("Set filters above and click **Apply Filters** to view shipments.")

# ---------------------------------------------------------------------
# RIGHT PANEL — Business Analytics / KPIs
# ---------------------------------------------------------------------
with right_col:
    st.header("📈 Business Analytics")

    # --- KPI metrics ---
    total_count_shipments, total_delivered_count, total_cancelled_count, delivered_percentile, cancelled_percentile = repo.fetch_shipments_percentile()
    avg_dliverytime_one_shipment = repo.avg_duration_delivered_shipments()
    total_operational_cost_of_shipment = repo.total_operational_cost_of_shipment()

    k1, k2, k3 = st.columns(3)
    k1.metric("Total Shipments", f"{total_count_shipments:,}")
    k2.metric("Delivered %", delivered_percentile)
    k3.metric("Cancelled %", cancelled_percentile)

    k4, k5 = st.columns(2)
    k4.metric("Delivered", f"{total_delivered_count:,}")
    k5.metric("Cancelled", f"{total_cancelled_count:,}")

    st.divider()

    # --- Pie chart: Delivered vs Cancelled vs Other ---
    st.subheader("Shipment Status Distribution")
    other_count = max(total_count_shipments - total_delivered_count - total_cancelled_count, 0)
    pie_df = pd.DataFrame({
        "Status": ["Delivered", "Cancelled", "Other / In Transit"],
        "Count": [total_delivered_count, total_cancelled_count, other_count],
    })
    pie_df = pie_df[pie_df["Count"] > 0]

    color_map = {
        "Delivered": "#2ecc71",
        "Cancelled": "#e74c3c",
        "Other / In Transit": "#f1c40f",
    }
    colors = [color_map[s] for s in pie_df["Status"]]

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(
        pie_df["Count"],
        labels=pie_df["Status"],
        colors=colors,
        autopct="%1.2f%%",
        startangle=90,
        wedgeprops={"width": 0.4, "edgecolor": "white"},
        textprops={"fontsize": 10},
    )
    ax.axis("equal")
    st.pyplot(fig, use_container_width=True)

    st.divider()

    # --- Average Delivery Time ---
    st.subheader("Average Delivery Time")
    a1, a2 = st.columns(2)
    a1.metric("Delivered Shipments", f"{avg_dliverytime_one_shipment[0]:,}")
    a2.metric("Avg (minutes)", f"{float(avg_dliverytime_one_shipment[2]):.2f}")
    st.caption(f"Avg duration: **{avg_dliverytime_one_shipment[3]}**  •  Total duration: {avg_dliverytime_one_shipment[1]:,} min")

    st.divider()

    # --- Total Operational Cost ---
    st.subheader("Total Operational Cost")
    st.metric("Total Operational Cost", f"{float(total_operational_cost_of_shipment):,.2f}")
    st.divider()
    st.header("?? Analytical Views")

    delivery_tab, courier_tab, cost_tab, cancel_tab, warehouse_tab = st.tabs([
        "Delivery",
        "Courier",
        "Cost",
        "Cancellation",
        "Warehouse",
    ])

    with delivery_tab:
        with st.expander("Average delivery time per route", expanded=True):
            df = analytics_df(ANALYTICS_QUERIES["average_delivery_time_per_route"])
            st.dataframe(df, use_container_width=True)
            if not df.empty:
                st.bar_chart(df.set_index("route")[["avg_actual_hours", "expected_hours"]])

        with st.expander("Most delayed routes"):
            df = analytics_df(ANALYTICS_QUERIES["most_delayed_routes"])
            st.dataframe(df, use_container_width=True)
            if not df.empty:
                st.bar_chart(df.set_index("route")["delay_hours"])

        with st.expander("Delivery time vs distance comparison"):
            df = analytics_df(ANALYTICS_QUERIES["delivery_time_vs_distance"])
            st.dataframe(df, use_container_width=True)
            if not df.empty:
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.scatter(df["distance_km"], df["avg_actual_hours"], alpha=0.75)
                ax.set_xlabel("Distance (km)")
                ax.set_ylabel("Average delivery time (hours)")
                ax.grid(True, alpha=0.3)
                st.pyplot(fig, use_container_width=True)

    with courier_tab:
        with st.expander("Shipments handled per courier", expanded=True):
            df = analytics_df(ANALYTICS_QUERIES["shipments_handled_per_courier"])
            st.dataframe(df, use_container_width=True)
            if not df.empty:
                st.bar_chart(df.set_index("name")["shipments_handled"])

        with st.expander("On-time delivery %"):
            df = analytics_df(ANALYTICS_QUERIES["on_time_delivery_percentage"])
            st.dataframe(df, use_container_width=True)
            if not df.empty:
                st.bar_chart(df.set_index("name")["on_time_percentage"])

        with st.expander("Average rating comparison"):
            df = analytics_df(ANALYTICS_QUERIES["average_rating_comparison"])
            st.dataframe(df, use_container_width=True)
            if not df.empty:
                st.bar_chart(df.set_index("name")["rating"])

    with cost_tab:
        with st.expander("Total cost per shipment", expanded=True):
            df = analytics_df(ANALYTICS_QUERIES["total_cost_per_shipment"])
            st.dataframe(df, use_container_width=True)
            if not df.empty:
                st.bar_chart(df.set_index("shipment_id")["total_cost"])

        with st.expander("Cost per route"):
            df = analytics_df(ANALYTICS_QUERIES["cost_per_route"])
            st.dataframe(df, use_container_width=True)
            if not df.empty:
                st.bar_chart(df.set_index("route")["total_route_cost"])

        with st.expander("Fuel vs labor percentage contribution"):
            df = analytics_df(ANALYTICS_QUERIES["fuel_vs_labor_percentage"])
            st.dataframe(df, use_container_width=True)
            if not df.empty:
                labels = ["Fuel", "Labor", "Misc"]
                values = [float(df.loc[0, "fuel_percentage"]), float(df.loc[0, "labor_percentage"]), float(df.loc[0, "misc_percentage"])]
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(values, labels=labels, autopct="%1.2f%%", startangle=90)
                ax.axis("equal")
                st.pyplot(fig, use_container_width=True)

        with st.expander("High-cost shipments"):
            df = analytics_df(ANALYTICS_QUERIES["high_cost_shipments"])
            st.dataframe(df, use_container_width=True)
            if not df.empty:
                st.bar_chart(df.set_index("shipment_id")["total_cost"])

    with cancel_tab:
        with st.expander("Cancellation rate by origin", expanded=True):
            df = analytics_df(ANALYTICS_QUERIES["cancellation_rate_by_origin"])
            st.dataframe(df, use_container_width=True)
            if not df.empty:
                st.bar_chart(df.set_index("origin")["cancellation_rate"])

        with st.expander("Cancellation rate by courier"):
            df = analytics_df(ANALYTICS_QUERIES["cancellation_rate_by_courier"])
            st.dataframe(df, use_container_width=True)
            if not df.empty:
                st.bar_chart(df.set_index("name")["cancellation_rate"])

        with st.expander("Time-to-cancellation analysis"):
            df = analytics_df(ANALYTICS_QUERIES["time_to_cancellation"])
            st.dataframe(df, use_container_width=True)
            if not df.empty:
                st.bar_chart(df.set_index("shipment_id")["hours_to_cancellation"])

    with warehouse_tab:
        with st.expander("Warehouse capacity comparison", expanded=True):
            df = analytics_df(ANALYTICS_QUERIES["warehouse_capacity_comparison"])
            st.dataframe(df, use_container_width=True)
            if not df.empty:
                st.bar_chart(df.set_index("city")["capacity"])

        with st.expander("High-traffic warehouse cities"):
            df = analytics_df(ANALYTICS_QUERIES["high_traffic_warehouse_cities"])
            st.dataframe(df, use_container_width=True)
            if not df.empty:
                st.bar_chart(df.set_index("city")["shipment_traffic"])
