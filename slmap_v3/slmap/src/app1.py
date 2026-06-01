import streamlit as st

# Current values
total_shipments = 69999
delivered_pct = 24.77
cancelled_pct = 25.04
avg_delivery_time = 6856.37   # minutes
total_cost = 11731008.67

# Previous values (for comparison)
prev_total_shipments = 68000
prev_delivered_pct = 23.50
prev_cancelled_pct = 26.10
prev_avg_delivery_time = 7000.00
prev_total_cost = 11500000.00

# KPIs with delta
col1, col2, col3 = st.columns(3)
col1.metric("Total Shipments", f"{total_shipments}", f"{total_shipments - prev_total_shipments}")
col2.metric("Delivered %", f"{delivered_pct:.2f}%", f"{delivered_pct - prev_delivered_pct:.2f}%")
col3.metric("Cancelled %", f"{cancelled_pct:.2f}%", f"{cancelled_pct - prev_cancelled_pct:.2f}%")

col4, col5 = st.columns(2)
col4.metric("Avg Delivery Time (minutes)", f"{avg_delivery_time:.2f}", f"{avg_delivery_time - prev_avg_delivery_time:.2f}")
col5.metric("Total Operational Cost", f"{total_cost:,.2f}", f"{total_cost - prev_total_cost:,.2f}")