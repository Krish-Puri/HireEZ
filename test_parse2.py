"""Test CSV parsing with exact user format."""
import sys
sys.path.insert(0, '.')
from backend.services.csv_service import csv_service

# Create test CSV matching exact user format
with open("test_results_debug.csv", "w", newline="") as f:
    f.write("""s_no,name,email,college,branch,cgpa,test_la,test_code
1,Student 1,test1@test.com,DTU,CS,8.5,49,90
2,Student 2,test2@test.com,MIT,EE,9.0,52,87
3,Student 3,test3@test.com,IIT,ME,8.22,67,82""")

report = csv_service.parse_test_results("test_results_debug.csv")
print("Parsed results:")
for r in report.results:
    print(" ", r)
print("Stats:", report.statistics)