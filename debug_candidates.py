import pymysql
conn = pymysql.connect(host='localhost', user='root', password='krish@spring24', database='hireez')
cur = conn.cursor()

cur.execute("SELECT id, name, email, test_la, test_code, final_score FROM candidates ORDER BY id")
rows = cur.fetchall()
print(f"{'ID':<4} {'Name':<15} {'test_la':<10} {'test_code':<10} {'final_score':<12}")
print("-" * 55)
for r in rows:
    print(f"{r[0]:<4} {r[1][:14]:<15} {str(r[3]):<10} {str(r[4]):<10} {str(r[5]):<12}")

print()
cur.execute("SELECT candidate_id, test_la, test_code FROM test_results ORDER BY candidate_id")
trs = cur.fetchall()
print(f"test_results table ({len(trs)} rows):")
for tr in trs:
    print(f"  candidate_id={tr[0]}, test_la={tr[1]}, test_code={tr[2]}")

conn.close()