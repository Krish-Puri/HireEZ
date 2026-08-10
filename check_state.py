import pymysql
conn = pymysql.connect(host='localhost', user='root', password='krish@spring24', database='hireez')
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM evaluations")
print("Evaluations:", cur.fetchone()[0])
cur.execute("SELECT id, candidate_id, overall_score FROM evaluations ORDER BY id LIMIT 5")
for r in cur.fetchall():
    print("  Eval:", r)
cur.execute("SELECT id, name, final_score, candidate_rank, status FROM candidates ORDER BY id LIMIT 5")
for r in cur.fetchall():
    print("  Cand:", r)
conn.close()