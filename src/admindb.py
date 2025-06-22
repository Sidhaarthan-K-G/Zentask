import mysql.connector
from flask import jsonify
import traceback

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

    def get_user_by_email(self, email):
        cur = None
        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute(
                "SELECT username FROM signup_details WHERE email = %s", (email,)
            )
            return cur.fetchone()
        except Exception as e:
            print("Error fetching user info:", e)
            return None
        finally:
            if cur:
                cur.close()

    def signup_table(self):
        cur = None
        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute("select*from signup_details order by signup_id desc")
            return cur.fetchall()
        except Exception as e:
            print("Error loading signup table:",e)
            return[]
        
    def login_table(self):
        cur = None
        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute("select*from login_details order by login_id desc")
            return cur.fetchall()
        except Exception as e:
            print("Error loading login table:",e)
            return[]

    def delete_by_id(self, signup_id):
        cur = None
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM signup_details WHERE signup_id = %s", (signup_id,))
            return cur.rowcount > 0
        except Exception as e:
            print("Error deleting row", e)
            return False

    def __del__(self):
        if self.conn:
            self.conn.close()
