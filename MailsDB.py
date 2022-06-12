import sqlite3
from uuid import uuid4


class MailsDB:
    
    def __init__(self):
        # self.conn = self.connect()
        cur = self.connect()
        
        self.table_name = "users"
        self.col_id = "id"
        self.col_tg_id = "telegram_id"
        # self.col_username = "username"
        self.col_email = "email"
        self.col_pass = "password_hash"
        self.col_active = "active"
        self.col_content = "show_content"
        self.col_attaches = "show_attaches"
        
        cur.execute(f"""CREATE TABLE IF NOT EXISTS {self.table_name}(
            {self.col_id} TEXT PRIMARY KEY,
            {self.col_tg_id} INT,
            {self.col_email} TEXT,
            {self.col_pass} TEXT,
            {self.col_active} BOOL,
            {self.col_content} BOOL,
            {self.col_attaches} BOOL
            );""")
        self.save()
        return
    
    
    def connect(self):
        self.conn = sqlite3.connect('./DB/Mails.db')
        return self.conn.cursor()
    
    
    def save(self):
        self.conn.commit()
        self.close()
        return
    
    # def execute(self, query):
    #     conn = self.connect()
    #     cur = conn.cursor()
    #     data = cur.execute(query)
    #     return data
    
    
    def close(self):
        self.conn.close()
        return
    
    
    #^##############################################^#
    #^##################  CREATE  ##################^#
    #^##############################################^#
    
    def add(self, telegram_id: int, email: str, password_hash: str, active: bool = True, show_content: bool = True, show_attaches: bool = True):
        cur = self.connect()
        cur.execute(f"""INSERT INTO {self.table_name} (
                                        {self.col_id},
                                        {self.col_tg_id},
                                        {self.col_email},
                                        {self.col_pass},
                                        {self.col_active},
                                        {self.col_content},
                                        {self.col_attaches}
                                    ) VALUES (
                                        '{uuid4().hex}',
                                        {telegram_id},
                                        '{email}',
                                        '{password_hash}',
                                        {active},
                                        {show_content},
                                        {show_attaches}
                                    );""")
        self.save()
        return
    
    
    #^##############################################^#
    #^###################  READ  ###################^#
    #^##############################################^#
    
    # def getUserByTelegramId(self, telegram_id: int):
    #     user = cur.execute(f"""SELECT * FROM {self.table_name} WHERE {self.col_tg_id}={telegram_id};""").fetchone()
    #     return user
    
    
    def getEmailsByTelegramId(self, telegram_id: int):
        cur = self.connect()
        emails = cur.execute(f"""SELECT * FROM {self.table_name} WHERE {self.col_tg_id}={telegram_id};""").fetchall()
        return emails
    
    
    # def getUserByUsername(self, username: str):
    #     user = cur.execute(f"""SELECT * FROM {self.table_name} WHERE {self.col_username}={username};""").fetchone()
    #     return user
    
    
    def getUserByEmail(self, email: str):
        cur = self.connect()
        user = cur.execute(f"""SELECT * FROM {self.table_name} WHERE {self.col_email}='{email}';""").fetchone()
        return user
    
    
    def getPasswordHashByEmail(self, email: str):
        cur = self.connect()
        password_hash = cur.execute(f"""SELECT {self.col_pass} FROM {self.table_name} WHERE {self.col_email}='{email}';""").fetchone()[0]
        return password_hash
    
    
    def isActive(self, email: str):
        cur = self.connect()
        is_active = cur.execute(f"""SELECT {self.col_active} FROM {self.table_name} WHERE {self.col_email}='{email}';""").fetchone()[0]
        return bool(is_active)
    
    
    def showContent(self, email: str):
        cur = self.connect()
        show_content = cur.execute(f"""SELECT {self.col_content} FROM {self.table_name} WHERE {self.col_email}='{email}';""").fetchone()[0]
        return bool(show_content)
    
    
    def showAttaches(self, email: str):
        cur = self.connect()
        show_attaches = cur.execute(f"""SELECT {self.col_attaches} FROM {self.table_name} WHERE {self.col_email}='{email}';""").fetchone()[0]
        return bool(show_attaches)
    
    
    #^##############################################^#
    #^##################  UPDATE  ##################^#
    #^##############################################^#
    
    # def setUsernameByTelegramId(self, telegram_id: int, username: str):
    #     cur.execute(f"""UPDATE {self.table_name} SET ({self.col_username}) = ({username}) WHERE {self.col_tg_id}={telegram_id};""")
    #     self.save()
    #     return
    
    
    def changeEmail(self, old_email: str, new_email: str):
        cur = self.connect()
        cur.execute(f"""UPDATE {self.table_name} SET ({self.col_email}) = ('{new_email}') WHERE {self.col_email}='{old_email}';""")
        self.save()
        return
    
    
    def changePassword(self, email: str, password_hash: str):
        cur = self.connect()
        cur.execute(f"""UPDATE {self.table_name} SET ({self.col_pass}) = ('{password_hash}') WHERE {self.col_email}='{email}';""")
        self.save()
        return
    
    
    def setActiveByEmail(self, email: str, active: bool):
        cur = self.connect()
        cur.execute(f"""UPDATE {self.table_name} SET ({self.col_active}) = ({active}) WHERE {self.col_email}='{email}';""")
        self.save()
        return
    
    
    def setContentByEmail(self, email: str, content: bool):
        cur = self.connect()
        cur.execute(f"""UPDATE {self.table_name} SET ({self.col_content}) = ({content}) WHERE {self.col_email}='{email}';""")
        self.save()
        return
    
    
    def setAttachesByEmail(self, email: str, attaches: bool):
        cur = self.connect()
        cur.execute(f"""UPDATE {self.table_name} SET ({self.col_attaches}) = ({attaches}) WHERE {self.col_email}='{email}';""")
        self.save()
        return
    
    
    #^##############################################^#
    #^##################  REMOVE  ##################^#
    #^##############################################^#
    
    def removeByTelegramId(self, telegram_id: int):
        cur = self.connect()
        cur.execute(f"""DELETE FROM {self.table_name} WHERE {self.col_tg_id}={telegram_id};""")
        self.save()
        return
    
    
    # def removeByUsername(self, username: str):
    #     cur.execute(f"""DELETE FROM {self.table_name} WHERE {self.col_username}={username};""")
    #     self.save()
    #     return
    
    
    def removeByEmail(self, email: str):
        cur = self.connect()
        cur.execute(f"""DELETE FROM {self.table_name} WHERE {self.col_email}='{email}';""")
        self.save()
        return

