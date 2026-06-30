import pymysql
conn = pymysql.connect(host='localhost', user='root', password='krish@spring24', database='hireez')
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS test_results (
        id INT AUTO_INCREMENT PRIMARY KEY,
        candidate_id INT NOT NULL,
        test_la FLOAT NULL,
        test_code FLOAT NULL,
        test_link VARCHAR(500) NULL,
        test_link_sent VARCHAR(20) DEFAULT 'Pending',
        interview_scheduled VARCHAR(20) DEFAULT 'Pending',
        interview_link VARCHAR(500) NULL,
        interview_time DATETIME NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY unique_candidate (candidate_id)
    )
""")
conn.commit()
print("Table created successfully")
conn.close()