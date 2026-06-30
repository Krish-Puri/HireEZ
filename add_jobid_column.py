import pymysql
conn = pymysql.connect(host='localhost', user='root', password='krish@spring24', database='hireez')
cur = conn.cursor()
try:
    cur.execute("ALTER TABLE candidates ADD COLUMN job_id INT NULL")
    print("Column added")
except Exception as e:
    print(f"Note: {e}")
conn.commit()
conn.close()