"""Quick test of CSV parsing."""
import sys
sys.path.insert(0, '.')
from backend.services.csv_service import csv_service

# Create a test CSV
import csv, io
data = """s_no,name,email,college,branch,cgpa,test_la,test_code
1,Student 1,a@test.com,MIT,CS,8.5,49,90
2,Student 2,b@test.com,Stanford,EE,9.0,52,87
3,Student 3,c@test.com,IIT,ME,8.2,67,82"""

with open("test_results_debug.csv", "w") as f:
    f.write(data)

report = csv_service.parse_test_results("test_results_debug.csv")
print("Results:")
for r in report.results:
    print(" ", r)
print("Stats:", report.statistics)