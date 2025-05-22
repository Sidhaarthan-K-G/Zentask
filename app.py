from flask import Flask,render_template,request,redirect,url_for,flash,session
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
            email = request.form.get("email")
            password = request.form.get("password")

            e = Execute()
            user = e.verify_login(email, password)

            if user:
                session["user_id"] = user["signup_id"]
                flash("Login successful!")
                return redirect(url_for("dashboard", user=user["username"]))
            
            else:
                flash("Invalid email or password.")
                return redirect(url_for("login"))

        return render_template("login.html")
    except Exception as e:
        print("Login error:", e)
        flash("An error occurred during login. Please try again.")
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
                flash("User already exists. Try a different username or email.")
                return redirect(url_for("signup"))

            # Insert new user
            e.signup_values(data)
            return redirect(url_for("dashboard", user=data["username"]))
        
        return render_template("signup.html")
    except Exception as e:
        print("Signup error:", e)
        flash("An error occurred during signup. Please try again.")
        return render_template("signup.html")
    
    
    
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")
@app.route("/my_tasks")
def my_tasks():
    return render_template("my_tasks.html")
@app.route("/new_task")
def new_tasks():
    return render_template("new_task.html")
@app.route("/logout")
def logout():
    return render_template("login.html")

if __name__=="__main__":
    app.run(debug=True)