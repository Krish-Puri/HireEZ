import pymysql
conn = pymysql.connect(host='localhost', user='root', password='krish@spring24', database='hireez')
cur = conn.cursor()

print("=== TABLE CHECK ===")
cur.execute("SHOW TABLES")
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)

print("\n=== EVALUATIONS TABLE ===")
try:
    cur.execute("DESCRIBE evaluations")
    for c in cur.fetchall():
        print("  %s: %s" % (c[0], c[1]))
    cur.execute("SELECT COUNT(*) FROM evaluations")
    print("  Row count:", cur.fetchone()[0])
except Exception as e:
    print("  Error:", e)

print("\n=== TEST_RESULTS TABLE ===")
try:
    cur.execute("DESCRIBE test_results")
    for c in cur.fetchall():
        print("  %s: %s" % (c[0], c[1]))
    cur.execute("SELECT COUNT(*) FROM test_results")
    print("  Row count:", cur.fetchone()[0])
except Exception as e:
    print("  Error:", e)

print("\n=== SAMPLE CANDIDATES ===")
cur.execute("SELECT id, name, job_id, resume_text, github_score, github_url, best_ai_project, status, final_score, candidate_rank FROM candidates LIMIT 3")
for r in cur.fetchall():
    resume_len = len(str(r[3])) if r[3] else 0
    url = str(r[5])[:40] if r[5] else None
    print("ID=%s name=%s job_id=%s resume_len=%s github=%s url=%s best_proj=%s status=%s final=%s rank=%s" % (
        r[0], r[1][:20], r[2], resume_len, r[4], url, r[6], r[7], r[8], r[9]))

conn.close()
print("Done")