import sqlite3
import datetime

"""
id: primary key
date: 日付
summary: 予定の名前
stauts: 予定の状態 0未完了, 1完了を想定
"""

class calendarDB:
    def __init__(self, dbname):
        self.dbname = dbname
        conn = sqlite3.connect(dbname)
        # sqliteを操作するカーソルオブジェクト
        cur = conn.cursor()
        # 日付は単なる文字列として扱う方向で運用していく
        cur.execute("CREATE TABLE IF NOT EXISTS " + self.dbname + "(\
            id INTEGER PRIMARY KEY AUTOINCREMENT,\
            date TEXT NOT NULL CHECK(date like '____-__-__'),\
            summary TEXT NOT NULL,\
            status INTEGER\
            )")
        
        conn.commit()
        conn.close()
    
    def insert_event(self, date: datetime.datetime, summaries: list):
        date_str = datetime.datetime.strftime(date, '%Y-%m-%d')
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        sql = "INSERT INTO " + self.dbname + "(date, summary, status) values (:date, :summary, 0)"
        #print(sql)
        data_list = [{"date": date_str, "summary": summaries[i], "datee": date_str, "summaryy": summaries[i]} for i in range(len(summaries))]
        cur.executemany(sql, data_list)
        conn.commit()
        conn.close()
        
    def set_status(self, id, status):
        try:
            conn = sqlite3.connect(self.dbname)
            cur = conn.cursor()
            sql = "UPDATE " + self.dbname + " SET status=" + str(status) + " WHERE id=" + str(id)
            cur.execute(sql)
            conn.commit()
            conn.close()
            return 0
        except:
            return 1
        
        
    def get_posts(self, date):
        date_str = datetime.datetime.strftime(date, '%Y-%m-%d')
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        sql = "SELECT * FROM " + self.dbname + " WHERE date='" + date_str + "'"
        #print(sql)
        schedule = cur.execute(sql).fetchall()
        conn.close()
        
        return schedule
    
    def get_all_posts(self):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute("SELECT * FROM " + self.dbname)
        print(cur.fetchall())
        conn.close()
        
if __name__ == "__main__":
    db = calendarDB("calendar")
    today = datetime.datetime.now()
    summaries = ["hoge"]
    #db.insert_event(today, summaries)
    db.set_status(1, 1)
    print(db.get_posts(today))
    db.get_all_posts()
    
    
