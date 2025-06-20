import mysql.connector
from flask import jsonify

class Admin:
    def __init__(self):
        self.conn = self.connect()

    def connect(self):
        try:
            conn = mysql.connector.connect(
                host = "localhost",
                database = "Zentask",
                user = "root",
                password = "Cyber@Titan22",
            )
            conn.autocommit = True
            return conn
        except mysql.connector.Error as e:
            print("Database Connection error:",e)

    def table(self, query):
        cur = None
        try:
            cur = self.conn.cursor()
            cur.execute(query)

        except Exception as e:
            print("Execution Failed:", e)
        finally:
            if cur:
                cur.close()

    def admin_table(self):
        try:
            self.table(
                """
                create table if not exists admin_login(
                    admin_id int auto_increment primary key,
                    email varchar(255) not null,
                    password varchar(255) not null)
                    """
            )
        except Exception as e:
            print("table not created:", e)

    def verify_admin(self, email, password):
        cur = None
        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute(
                "select * from admin_login where email=%s and password=%s",
                (email, password),
            )
            user = cur.fetchone()
            return user
        except Exception as e:
            print("Admin verification error:", e)

    

    def __del__(self):
        if self.conn:
            self.conn.close()
