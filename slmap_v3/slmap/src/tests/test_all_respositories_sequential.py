import subprocess

files = [
    "src.tests.test_drop_all_tables",
    "src.tests.test_courierstaff_repository",
    "src.tests.test_shipments_repository",
    "src.tests.test_shipment_tracking_repository",
    "src.tests.test_routes_repository",
    "src.tests.test_warehoue_repository",
    "src.tests.test_costs_repository"
]

for f in files:
    print(f"Running {f}...")
    subprocess.run(["python", "-m", f], check=True)
