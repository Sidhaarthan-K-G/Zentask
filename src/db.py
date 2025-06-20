import mysql.connector
from flask import jsonify


class Execute:
    def __init__(self):
        self.conn = self.connect()

    def connect(self):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                database="Zentask",
                user="root",
                password="Cyber@Titan22",
            )
            conn.autocommit = True
            return conn
        except mysql.connector.Error as e:
            print("Database Connection error:", e)

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

    def login_table(self):
        try:
            self.table(
                """
            create table if not exists login_details(
                login_id int auto_increment primary key,
                email varchar(255)not null,
                password varchar(255)not null);
            """
            )
        except Exception as e:
            print("Table not created:", e)

    def insert(self, query, data):
        cur = None
        try:
            cur = self.conn.cursor()
            cur.execute(query, data)
            self.conn.commit()
            print("Data inserted successfully:", data)
        except Exception as e:
            print("Execution Failed:", e)
            return []
        finally:
            if cur:
                cur.close()

    def login_values(self, data):
        try:
            self.insert(
                """
                INSERT INTO login_details (email, password)
                VALUES (%(email)s, %(password)s)
            """,
                data,
            )
        except Exception as e:
            print("Data not inserted:", e)
            return []

    def signup_table(self):
        try:
            self.table(
                """
                create table if not exists signup_details(
                    signup_id int auto_increment primary key,
                    name varchar(255)not null,
                    email varchar(255)not null,
                    username varchar(255),
                    password varchar(255)not null);
                    """
            )
        except Exception as e:
            print("table not created:", e)

    def signup_values(self, data):
        cur = None
        try:
            cur = self.conn.cursor()
            cur.execute(
                """
                INSERT INTO signup_details (name, email, username, password)
                VALUES (%s, %s, %s, %s)
            """,
                (data["name"], data["email"], data["username"], data["password"]),
            )
            self.conn.commit()  # ✅ commit after insert
        except Exception as e:
            print("Error in signup_values:", e)
        finally:
            if cur:
                cur.close()

    def verify_login(self, email, password):
        cur = None
        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM signup_details WHERE email = %s AND password = %s",
                (email, password),
            )
            user = cur.fetchone()
            return user  # Returns user if found, else None
        except Exception as e:
            print("Login verification error:", e)
            return None
        finally:
            if cur:
                cur.close()

    def verify_email(self, email):
        cur = None
        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM signup_details WHERE email = %s", (email,))
            user = cur.fetchone()
            return user  # Returns user if found, else None
        except Exception as e:
            print("Email verification error:", e)
            return None
        finally:
            if cur:
                cur.close()

    def verify_signup(self, username, email):
        cur = None
        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT * FROM signup_details
                WHERE username = %s OR email = %s
            """,
                (username, email),
            )
            return cur.fetchall()  # ✅ fetches result fully
        except Exception as e:
            print("Not able to fetch data", e)
            return None  # better than empty list for clarity
        finally:
            if cur:
                cur.close()

    def task_table(self):
        try:
            self.table(
                """
                create table if not exists tasks(
                    Task_id int auto_increment primary key,
                    Task varchar(255)not null,
                    Due_date varchar(255)not null,
                    Priority varchar(255) not null,
                    Status varchar(255)default "Not Done",
                    email varchar(255)not null)
                """
            )
        except Exception as e:
            print("Table not created", e)

    def insert_task(self, data):
        try:
            self.insert(
                """
            INSERT INTO tasks (Task, Due_date, Priority, Status, Email)
            VALUES (%(task)s, %(date)s, %(priority)s, 'Not Done', %(email)s)
        """,
                data,
            )
        except Exception as e:
            print("Task not added:", e)
            return []

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

    def get_tasks(self, email):
        cur = None
        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM tasks WHERE Email = %s ORDER BY Status ASC", (email,)
            )
            tasks = cur.fetchall()
            return tasks
        except Exception as e:
            print("Error fetching tasks:", e)
            return []
        finally:
            if cur:
                cur.close()

    def update_tasks(self, task):
        cur = None
        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute(
                "update tasks set Status=%s where task=%s and email=%s",
                (task["Status"], task["task"], task["email"]),
            )
        except Exception as e:
            print("Error updating the status:", e)
            return []

    def update_pwd(self, password, email):
        cur = None
        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute(
                "update signup_details set password=%s where email=%s",
                (password, email),
            )
        except Exception as e:
            print("Error updating the status:", e)
            return []

    def update_status_by_id(self, task_id, new_status):
        cur = None
        try:
            cur = self.conn.cursor()
            cur.execute(
                "UPDATE tasks SET Status = %s WHERE Task_id = %s", (new_status, task_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print("Error updating task status by ID:", e)
            return False
        finally:
            if cur:
                cur.close()

    def delete_by_id(self, task_id):
        cur = None
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM tasks WHERE Task_id = %s", (task_id,))
            return cur.rowcount > 0
        except Exception as e:
            print("Error deleting row", e)
            return False

    def __del__(self):
        if self.conn:
            self.conn.close()
