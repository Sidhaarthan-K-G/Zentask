from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash, jsonify
from flask import session
from src.db import Execute
from src.admindb import Admin
from flask import make_response

app = Flask(__name__)
app.secret_key = "your-secret-key"


@app.before_request
def create():
    try:
        e = Execute()
        e.login_table()
        e.signup_table()
        e.task_table()
        a = Admin()
        a.admin_table()
    except Exception as e:
        print("table not created")
# <--------------------------------------------------------------------------------------------->#
# USER CONTENTS

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            data = {
                "email": request.form.get("email", "").strip().lower(),
                "password": request.form.get("password", ""),
            }
            e = Execute()
            user = e.verify_login(data["email"], data["password"])
            if user:
                session["user_id"] = user["signup_id"]
                session["email"] = user["email"]
                e.login_values(data)
                return redirect(url_for("dashboard", user=user["username"]))
            else:
                flash("Invalid email or password", "error")  
                return redirect(url_for("login"))
        return render_template("login.html")
    except Exception as e:
        print("Login error:", e)
        flash(
            "Something went wrong during login. Please try again.", "error"
        )
        return render_template("login.html")


@app.route("/frgtpwd", methods=["GET", "POST"])
def forgot_pwd():
    if request.method == "POST":
        data = {"email": request.form.get("email", "").strip().lower()}
        e = Execute()
        existing_user = e.verify_email(data["email"])
        if not existing_user:
            flash("User with this email does not exist.", "error")
            return redirect(url_for("forgot_pwd"))
        session["reset_email"] = data["email"]
        return render_template("cnfrmpwd.html")
    return render_template("frgtpwd.html")


@app.route("/cnfrmpwd", methods=["GET", "POST"])
def confirm_pwd():
    if request.method == "POST":
        data = {
            "cnfpwd": request.form.get("cnfpwd", ""),
            "email": session["reset_email"],
        }
        e = Execute()
        e.update_pwd(data["cnfpwd"], data["email"])
        return render_template("login.html")
    return render_template("cnfrmpwd.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    try:
        if request.method == "POST":
            data = {
                "name": request.form.get("name").strip(),
                "email": request.form.get("email").strip().lower(),
                "username": request.form.get("username").strip().lower(),
                "password": request.form.get("password"),
            }
            e = Execute()
            existing_user = e.verify_signup(data["username"], data["email"])
            if existing_user:
                flash(
                    "User already exists. Try a different username or email.", "error"
                )
                return redirect(url_for("signup"))
            e.signup_values(data)
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
        user_data = e.get_user_by_email(session["email"])
        username = user_data.get("username") if user_data else "User"

        response = make_response(render_template("dashboard.html", username=username))
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, post-check=0, pre-check=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        print("Error loading dashboard:", e)
        flash("Error loading tasks. Please try again.")
        return redirect(url_for("login"))


@app.route("/api/get_tasks", methods=["GET"])
def get_tasks():
    try:
        if "email" not in session:
            return jsonify({"error": "Unauthorized"}), 401
        e = Execute()
        tasks = e.get_tasks(session["email"])

        return jsonify({"tasks": tasks})
    except Exception as e:
        print("Error fetching tasks:", e)
        return []


@app.route("/new_task", methods=["POST", "GET"])
def new_tasks():
    try:
        if "email" not in session:
            return redirect(url_for("login"))

        if request.method == "POST":
            data = {
                "task": request.form.get("task").strip(),
                "date": request.form.get("date").strip(),
                "priority": request.form.get("priority").strip(),
                "email": session["email"],
            }
            e = Execute()
            e.insert_task(data)
            return redirect(url_for("dashboard"))

        response = make_response(render_template("new_task.html"))
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, post-check=0, pre-check=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    except Exception as e:
        print("Task not added:", e)
        return redirect(url_for("new_tasks"))
    except Exception as e:
        print("Task not added:", e)
        return redirect(url_for("new_task"))


@app.route("/api/update_tasks", methods=["POST"])
def update_tasks():
    try:
        tasks = request.get_json()
        e = Execute()
        for i in tasks:
            e.update_tasks(i)
        return jsonify({"message": "Task updated"}), 200
    except Exception as e:
        print("Status not updated", e)
        return jsonify({"error": "failed"}), 500


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


@app.after_request
def add_cache_control_headers(response):
    if request.endpoint in ["dashboard", "new_tasks"]:
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, post-check=0, pre-check=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return render_template("login.html")
# <------------------------------------------------------------------------------------------------->#
# ADMIN LOGIN

@app.route("/adminlogin",methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        data = {
            "email":request.form.get("email"),
            "password":request.form.get("password")
        }
        a=Admin()
        existing_user = a.verify_admin(data["email"],data["password"])
        if existing_user:
            session["email"] = existing_user["email"]
            return redirect(url_for("admindashboard",existing_user=existing_user["email"]))
        else:
            flash("Unauthorized access","error")
            return redirect(url_for("admin_login"))
    return render_template("adminlogin.html")

@app.route("/admin_dashboard")
def admindashboard():
    try:
        if "email" not in session:
            flash("Please log in to view admin dashboard")
            return redirect(url_for("admin_login"))
        a = Admin()
        user_data = a.get_user_by_email(session["email"])
        response = make_response(render_template("admindashboard.html",user_data=user_data))
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, post-check=0, pre-check=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        print("Error loading admin dashboard:", e)
        flash("Error loading admin dashboard. Please try again.")
        return redirect(url_for("admin_login"))


@app.route("/signuplog")
def signuplog():
    try:
        if "email" not in session:
            flash("Please log in to view dashboard")
            return redirect(url_for("admin_login"))

        # Only render template; data fetched via JS
        response = make_response(render_template("adminsignuplog.html"))
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, post-check=0, pre-check=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        print("❌ Error loading signuplog:", e)
        flash("Error loading signup log. Please try again.")
        return redirect(url_for("admin_login"))


@app.route("/api/get_signup_log", methods=["GET"])
def api_signup_log():
    try:
        if "email" not in session:
            return jsonify({"error": "Unauthorized"}), 401

        a = Admin()
        data = a.signup_table()
        return jsonify({"signup_table": data})
    except Exception as e:
        print("❌ Error fetching signup log:", e)
        return jsonify({"error": "Internal Server Error"}), 500


@app.route("/api/delete_user", methods=["POST"])
def delete_user():
    try:
        if "email" not in session:
            return redirect(url_for("admin_login"))

        data = request.get_json()
        if not data or "signup_id" not in data:
            return jsonify({"error": "Invalid request"}), 400

        signup_id = data["signup_id"]
        a = Admin()
        success = a.delete_by_id(signup_id)
        if success:
            return jsonify({"message": "User removed successfully"}), 200
        else:
            return jsonify({"error": "User not found or could not be removed"}), 404
    except Exception as e:
        print("Unable to remove user:", e)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/loginlog")
def loginlog():
    try:
        if "email" not in session:
            flash("Please log in to view dashboard")
            return redirect(url_for("admin_login"))

        # Only render template; data fetched via JS
        response = make_response(render_template("adminloginlog.html"))
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, post-check=0, pre-check=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        print("❌ Error loading loginlog:", e)
        flash("Error loading login log. Please try again.")
        return redirect(url_for("admin_login"))


@app.route("/api/get_login_log", methods=["GET"])
def api_login_log():
    try:
        if "email" not in session:
            return jsonify({"error": "Unauthorized"}), 401

        a = Admin()
        data = a.login_table()
        return jsonify({"login_table": data})
    except Exception as e:
        print("❌ Error fetching login log:", e)
        return jsonify({"error": "Internal Server Error"}), 500


@app.route("/adminlogout")
def adminlogout():
    session.clear()
    flash("You have been logged out.", "success")
    return render_template("adminlogin.html")


if __name__ == "__main__":
    app.run(debug=True)
