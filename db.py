import sqlite3

class UserDB:
    def __init__(self):
        self.conn = sqlite3.connect("BotDataBase.db")
        self.cursor = self.conn.cursor()

        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='User';"
        self.cursor.execute(sql)

        boolean = self.cursor.fetchall()
        if(boolean):
            pass
        else:
            self.cursor.execute("""
                CREATE TABLE "User" (
                    "id"	INTEGER,
                    "telegram_id"	INTEGER,
                    "bitrix_id"	INTEGER,
                    "departmentId"	INTEGER,
                    "departmentName"	TEXT,
                    "active"	INTEGER DEFAULT 1,
                    PRIMARY KEY("id" AUTOINCREMENT)
                );
            """)
            self.conn.commit()

    
    def identification(self, telegram_id):
        sql = "SELECT * FROM User WHERE telegram_id=%s AND active=1"%(telegram_id)
        self.cursor.execute(sql)
        user = self.cursor.fetchall()
        if user:
            return user
        else:
            return False

    def CreateUser(self, telegram_id, bitrix_id, departmentId, departmentName):
        sql = "SELECT * FROM User WHERE telegram_id=%s AND active=1"%(telegram_id)
        self.cursor.execute(sql)

        print(bitrix_id)
        if not self.identification(telegram_id):
            self.cursor.execute("""INSERT INTO User (telegram_id, bitrix_id, departmentId, departmentName)
                VALUES ('%s', '%s', '%s', '%s')"""%(telegram_id, bitrix_id, departmentId, departmentName)
            )
            self.conn.commit()

            return True
        else:
            return False


    def GetField(self, telegram_id):
        sql = "SELECT * FROM User WHERE telegram_id=%s AND active=1"%(telegram_id)
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    
x = UserDB()

# x.CreateUser(232123, 23)
# print(x.identification(1598571191))