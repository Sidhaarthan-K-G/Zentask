import mysql.connector
from flask import jsonify


class Execute:
    def __init__(self):
        self.conn=self.connect()
    
    def connect(self):
        try:
            conn=mysql.connector.connect(
                host="localhost",
                database="Zentask",
                user="root",
                password="Cyber@Titan22"
            )
            conn.autocommit=True
            return conn
        except mysql.connector.Error as e:
            print("Database Connection error:",e)

    def table(self,query):
        cur=None
        try:
            cur=self.conn.cursor()
            cur.execute(query)
            print("Table created Successfully")
        except Exception as e:
            print("Execution Failed:",e)
        finally:
            if cur:
                cur.close()
    
    def login_table(self):
        try:
            self.table("""
            create table if not exists login_details(
                login_id int auto_increment primary key,
                email varchar(255)not null,
                password varchar(255)not null);
            """)
        except Exception as e:
            print("Table not created:",e)
            
    def insert(self,query,data):
        cur=None
        try:
            cur=self.conn.cursor()
            cur.execute(query,data)
            self.conn.commit()
            print("Data inserted successfully:",data)
        except Exception as e:
            print("Execution Failed:",e)
            return []
        finally:
            if cur:
                cur.close()
                
    def login_values(self,data):
        try:
            self.insert("""
            INSERT IGNORE INTO login_details (email, password)
            VALUES (%(email)s, %(password)s""",data)

        except Exception as e:
            print("Data not inserted:",e)
            return []
        
        
    def signup_table(self):
        try:
            self.table("""
                create table if not exists signup_details(
                    signup_id int auto_increment primary key,
                    name varchar(255)not null,
                    email varchar(255)not null,
                    username varchar(255),
                    password varchar(255)not null);
                    """)
        except Exception as e:
            print("table not created")
    def signup_values(self,data):
        try:
            self.insert("""
                insert into signup_details(
                    name,email,username,password)
                    values(%(name)s,%(email)s,%(username)s,%(password)s)""",data)
        except Exception as e:
            print("Data not inserted")
            return []
        
    def verify_login(self, email, password):
        cur = None
        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM signup_details WHERE email = %s AND password = %s", (email, password))
            user = cur.fetchone()
            return user  # Returns user if found, else None
        except Exception as e:
            print("Login verification error:", e)
            return None
        finally:
            if cur:
                cur.close()


                
    def verify_signup(self,username,email):
        cur=None
        try:
            cur=self.conn.cursor(dictionary=True)
            cur.execute("""
                select * from signup_details where username=%s or email=%s """,(username,email))
            exist=cur.fetchone()
            return exist
        except Exception as e:
            print("Not able to fetch data",e)
            return []
        finally:
            if cur:
                cur.close()
                
    def task_table(self):
        try:
            self.table("""
                create table if not exists tasks(
                    Task_id int auto_increment primary key,
                    Task varchar(255)not null,
                    Due_date varchar(255)not null,
                    Priority varchar(255) not null,
                    Status varchar(255)default "Not Done",
                    email varchar(255)not null)
                """)
        except Exception as e:
            print("Table not created",e)
            
    def insert_task(self,data):
        try:
            self.insert("""
            INSERT INTO tasks (Task, Due_date, Priority, Status, Email)
            VALUES (%(task)s, %(date)s, %(priority)s, 'Not Done', %(email)s)
        """, data)
        except Exception as e:
            print("Task not added:",e)
            return []
    
    
    def get_tasks(self,email):
        cur=None
        try:
            cur=self.conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM tasks WHERE Email = %s ORDER BY Status ASC", (email,))
            tasks=cur.fetchall()
            return (tasks)
        except Exception as e:
            print("Error fetching tasks:", e)
            return []
        finally:
            if cur:
                cur.close()
    def __del__(self):
        if self.conn:
            self.conn.close()
        