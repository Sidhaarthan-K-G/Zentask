from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash,jsonify
from flask import session
from src.db import Execute

app=Flask(__name__)
app.secret_key = 'your-secret-key'
@app.before_request
def create():
    try:
        e=Execute()
        e.login_table()
        e.signup_table()
        e.task_table()
    except Exception as e:
        print("table not created")
    
@app.route("/")
def home():
    return render_template("home.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            data = {
                "email": request.form.get("email", "").strip().lower(),
                "password": request.form.get("password", "")
            }

            e = Execute()
            user = e.verify_login(data["email"], data["password"])

            if user:
                session["user_id"] = user["signup_id"]
                session["email"] = user["email"]
                e.login_values(data)
                return redirect(url_for("dashboard", user=user["username"]))
            else:
                flash("Invalid email or password", "error")  # 🔴 Show error
                return redirect(url_for("login"))

        return render_template("login.html")

    except Exception as e:
        print("Login error:", e)
        flash("Something went wrong during login. Please try again.", "error")  # 🔴 Show exception flash
        return render_template("login.html")

@app.route('/signup', methods=["GET", "POST"])
def signup():
    try:
        if request.method == "POST":
            data = {
                "name": request.form.get("name").strip(),
                "email": request.form.get("email").strip().lower(),
                "username": request.form.get("username").strip().lower(),
                "password": request.form.get("password")
            }

            e = Execute()
            existing_user = e.verify_signup(data["username"], data["email"])

            if existing_user:
                flash("User already exists. Try a different username or email.", "error")
                return redirect(url_for("signup"))

            # ✅ Add user to DB
            e.signup_values(data)

            # ✅ Fetch the user back to get their signup_id
            user = e.verify_login(data["email"], data["password"])
            if user:
                session["user_id"] = user["signup_id"]
                session["email"] = user["email"]

            return redirect(url_for("dashboard"))

        return render_template("signup.html")
    except Exception as e:
        print("Signup error:", e)
        flash("An error occurred during signup. Please try again.", "error")
        return render_template("signup.html")


    
    
    
@app.route("/dashboard")
def dashboard():
    try:
        if "email" not in session:
            flash("Please log in to view dashboard")
            return redirect(url_for("login"))
        e = Execute()
        user_data = e.get_user_by_email(session["email"])  # You'll add this method
        username = user_data.get("username") if user_data else "User"

        return render_template("dashboard.html", username=username)
    except Exception as e:
        print("Error loading dashboard:", e)
        flash("Error loading tasks. Please try again.")
        return redirect(url_for("login"))
    
@app.route("/api/get_tasks",methods=["GET"])
def get_tasks():
    try:
        if "email" not in session:
            return jsonify({"error":"Unauthorized"}),401
        e=Execute()
        tasks=e.get_tasks(session["email"])
        
        return jsonify({"tasks":tasks})
    except Exception as e:
        print("Error fetching tasks:",e)
        return[]
    
@app.route("/new_task",methods=["POST","GET"])
def new_tasks():
    try:
        if "email" not in session:
            
            return redirect(url_for("login"))
        if request.method == "POST":
            data={
                "task":request.form.get("task").strip(),
                "date":request.form.get("date").strip(),
                "priority":request.form.get("priority").strip(),
                "email":session["email"]
            }
            e=Execute()
            e.insert_task(data)
            return redirect(url_for("dashboard"))
        return render_template("new_task.html")
    except Exception as e:
        print("Task not added:",e)
        return redirect(url_for("new_task"))

@app.route("/api/update_tasks",methods=["POST"])
def update_tasks():
    try:
        tasks=request.get_json()
        e=Execute()
        for i in tasks:
            e.update_tasks(i)
        return jsonify({"message":"Task updated"}),200
    except Exception as e:
        print("Status not updated",e)
        return jsonify({"error":"failed"}),500
    

@app.route("/api/delete_tasks", methods=["POST"])
def delete_tasks():
    try:
        if "email" not in session:
            return redirect(url_for("login"))

        data = request.get_json()
        if not data or "task_id" not in data:
            return jsonify({"error": "Invalid request"}), 400

        task_id = data["task_id"]
        e = Execute()
        success = e.delete_by_id(task_id)
        if success:
            return jsonify({"message": "Task deleted successfully"}), 200
        else:
            return jsonify({"error": "Task not found or could not be deleted"}), 404
    except Exception as e:
        print("Unable to delete task:", e)
        return jsonify({"error": "Internal server error"}), 500
    
@app.route("/api/update_task_status", methods=["POST"])
def update_task_status():
    try:
        if "email" not in session:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json()
        task_id = data.get("task_id")
        new_status = data.get("status")

        if not task_id or not new_status:
            return jsonify({"error": "Missing task_id or status"}), 400

        e = Execute()
        e.update_status_by_id(task_id, new_status)
        return jsonify({"message": "Task status updated"}), 200

    except Exception as e:
        print("Error updating task status:", e)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/logout")
def logout():
    session.clear()
    return render_template("login.html")

if __name__=="__main__":
    app.run(debug=True)