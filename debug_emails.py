import pymysql
conn = pymysql.connect(host='localhost', user='root', password='krish@spring24', database='hireez')
cur = conn.cursor()

# Show all candidate emails and IDs
cur.execute("SELECT id, email FROM candidates ORDER BY id")
rows = cur.fetchall()
print("All candidate emails:")
for r in rows:
    print(f"  ID {r[0]}: {r[1]}")

# Test the LIKE pattern for base email
base = "rishabh.choudhary+hatif@mynachiketa.com"
local = base.split("@")[0]  # rishabh.choudhary+hatif
domain = base.split("@")[1]  # mynachiketa.com
pattern = f"{local}%@{domain}"
print(f"\nLIKE pattern: {pattern}")

cur.execute("SELECT id, email FROM candidates WHERE email LIKE %s", (pattern,))
matches = cur.fetchall()
print(f"Matching candidates: {matches}")

conn.close()