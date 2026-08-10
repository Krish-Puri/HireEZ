import pymysql
conn = pymysql.connect(host='localhost', user='root', password='krish@spring24', database='hireez')
cur = conn.cursor()
cur.execute('DELETE FROM test_results')
cur.execute('DELETE FROM evaluations')
cur.execute('DELETE FROM candidates')
conn.commit()
print('All data cleared')
conn.close()